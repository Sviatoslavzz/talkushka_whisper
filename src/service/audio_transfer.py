import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import aiofiles
import aiofiles.os
from loguru import logger

from app_worker import AppWorker
from objects import MB, TranscriptionTask
from proto_gen import AudioChunk, AudioTransferBase, Response
from utils import get_project_root


class AudioTransfer(AudioTransferBase):
    async def stream_audio(self, audio_chunk_iterator: AsyncIterator[AudioChunk]) -> AsyncIterator[Response]:
        logger.info("Got a new gRPC stream : Receiving audio chunks")

        result = False
        text_file_path = None
        message = None

        try:
            load_path = await self.write_stream_to_file(audio_chunk_iterator)
            logger.info("Successfully saved stream to file : {path}", path=load_path)
            task: TranscriptionTask = await AppWorker.get_instance().get_transcription(load_path)
            if not task.result:
                message = task.message
            else:
                result = task.result
                text_file_path = task.text_path
        except Exception as e:
            logger.error("Failed to save stream to file {err}", err=e.__repr__())
            message = e.__repr__()

        async for resp in self.stream_response(result, message, text_file_path):
            yield resp

    @staticmethod
    async def write_stream_to_file(audio_chunk_iterator: AsyncIterator[AudioChunk]) -> Path:
        save_to = (get_project_root() / "data" / f"{uuid.uuid4()}.m4a")
        async with aiofiles.open(file=save_to, mode="wb") as audio_file:
            async for chunk in audio_chunk_iterator:
                await audio_file.write(chunk.payload)

        return save_to

    @staticmethod
    async def stream_response(status: bool, message: str | None, path_: Path | None) -> AsyncIterator[Response]:
        if not status:
            yield Response(result=status, message=message)
            logger.warning("Finished streaming response with status : no text file")
            return

        try:
            async with aiofiles.open(file=path_, mode="rb") as text_file:
                while True:
                    chunk = await text_file.read(MB)
                    if not chunk:
                        break
                    yield Response(result=True, payload=chunk, message=message)
            await aiofiles.os.unlink(path_)
            logger.info("Finished streaming response with status : success")
        except FileNotFoundError as e:
            logger.error("Unable to stream file:text file not found {err}", err=e.__repr__())
            yield Response(result=False, message="stream_error:text file not found")
