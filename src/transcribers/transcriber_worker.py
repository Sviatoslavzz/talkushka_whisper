import time
from asyncio import get_running_loop
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any

from loguru import logger

from config.models import TranscriberConfig
from objects import TranscriptionTask


class TranscriberWorker:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self, config: TranscriberConfig):
        self.transcriber = config.cls(model=config.model)
        self.pool = ThreadPoolExecutor(max_workers=config.pool_size)

        logger.info(f"{self.__class__.__name__} initialized")

    @classmethod
    def get_instance(cls):
        return cls._instance

    @staticmethod
    def _async_wrap(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs):  # ANN202
            loop = get_running_loop()
            return await loop.run_in_executor(self.pool, lambda: func(self, *args, **kwargs))

        return wrapper

    @staticmethod
    def file_exist(task: TranscriptionTask) -> bool:
        if not task.audio_path.is_file():
            logger.error(f"{task.id} File does not exist: {task.audio_path}")
            task.message = "file_not_found_error:file for transcription not found"
            return False

        return True

    @_async_wrap
    def transcribe(self, task: TranscriptionTask) -> TranscriptionTask:
        """
        Checks the origin_path, launches transcription process, saves the result in .txt
        :param task: TranscriptionTask with filled origin path
        :return: TranscriptionTask
        """

        if not self.file_exist(task):
            return task

        try:
            transcription = self.transcriber.transcribe(path=task.audio_path)
        except NotImplementedError:
            task.message = "file_format_error:file format is not supported"
            return task

        task.text_path = task.audio_path.with_suffix(".txt")

        try:
            with task.text_path.open(mode="w") as file:
                file.write(transcription)
            logger.info(f"Transcription saved\nwhere: {task.text_path}")
            task.result = True
        except OSError:
            logger.error(f"Unable to save transcription to {task.text_path}")
            task.message = "os_error:unable to save transcription"

        return task


async def transcriber_worker_as_target(task: TranscriptionTask, config: TranscriberConfig) -> TranscriptionTask:
    worker = TranscriberWorker.get_instance()
    if not worker:
        worker = TranscriberWorker(config=config)
        time.sleep(1)  # blocking pause to wait for TranscriberWorker init

    return await worker.transcribe(task)
