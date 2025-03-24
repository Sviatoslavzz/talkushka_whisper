import asyncio
from pathlib import Path
from platform import system as platform_system

import aiofiles.os
from loguru import logger

from talkushka_transcriber.config.models import TranscriberConfig
from talkushka_transcriber.executors.process_executor import ProcessExecutor
from talkushka_transcriber.executors.transcriber_executor import TranscriberExecutor
from talkushka_transcriber.objects import TranscriptionTask
from talkushka_transcriber.transcribers.transcriber_worker import transcriber_worker_as_target

IS_MACOS = platform_system() == "Darwin"


class AppWorker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, config: TranscriberConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(self.config.pool_size * 2)
        self.sem_queue_size = 0

        self._transcriber_executor: TranscriberExecutor | None = None
        logger.info("{cls} initialized", cls=self.__class__.__name__)

    @classmethod
    def get_instance(cls):
        return cls._instance

    async def get_transcription(self, audio_file: Path) -> TranscriptionTask:
        task = await self.__run_transcriber_executor(TranscriptionTask(id=audio_file.name, audio_path=audio_file))
        await aiofiles.os.unlink(task.audio_path)

        return task

    async def __submit_task(self, executor: ProcessExecutor, task_: TranscriptionTask) -> TranscriptionTask:
        """
        Transfer a task to executor and waits for the result in a separate thread
        :param executor: ProcessExecutor
        :param task_: TranscriptionTask
        """
        self.sem_queue_size += 1
        async with self.semaphore:
            self.sem_queue_size -= 1
            logger.info(
                "{cls} : tasks waiting in semaphore {size}", cls=self.__class__.__name__, size=self.sem_queue_size
            )
            executor.put_task(task_)
            while True:
                result = await asyncio.to_thread(executor.get_result)
                if result:
                    if task_.id == result.id:
                        return result
                    executor.put_result(result)

                await asyncio.sleep(0.1)

    async def __run_transcriber_executor(self, task: TranscriptionTask) -> TranscriptionTask:
        """
        Runs transcriber in a separate process,
        puts transcription tasks to process Queue,
        and asynchronously wait for results
        Returns: TranscriptionTask
        """

        if not self._transcriber_executor:
            self._transcriber_executor = TranscriberExecutor(transcriber_worker_as_target, config=self.config)
            self._transcriber_executor.configure(
                q_size=self.config.q_size,
                context="spawn" if IS_MACOS else "fork",
                process_name="python_transcriber_worker",
            )
            self._transcriber_executor.set_name("transcriber_worker")
            self._transcriber_executor.start()

        return await self.__submit_task(self._transcriber_executor, task)

    def stop_executors(self):
        if self._transcriber_executor:
            self._transcriber_executor.stop()
