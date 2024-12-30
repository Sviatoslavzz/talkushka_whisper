import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import aiofiles
import aiofiles.os
from loguru import logger

from app_worker import AppWorker
from objects import TranscriptionTask
from proto_gen import AudioChunk, AudioTransferBase, Response
from utils import get_project_root


async def write_stream_to_file(audio_chunk_iterator: AsyncIterator[AudioChunk]) -> Path:
    save_to = (get_project_root() / "data" / f"{uuid.uuid4()}.m4a")
    async with aiofiles.open(file=save_to, mode="wb") as audio_file:
        prev_chunk_num = -1
        async for chunk in audio_chunk_iterator:
            if chunk.chunk_number != prev_chunk_num + 1:
                raise LookupError("Wrong order of chunks received")
            prev_chunk_num = chunk.chunk_number
            await audio_file.write(chunk.payload)

    return save_to


async def get_transcription_result(task: TranscriptionTask) -> tuple[bool, bytes | None, str | None]:
    if not task.result:
        return task.result, None, task.message

    try:
        async with aiofiles.open(file=task.text_path, mode="rb") as text_file:
            payload = await text_file.read()
        await aiofiles.os.unlink(task.text_path)
        return task.result, payload, task.message
    except Exception as e:
        raise e


class AudioTransfer(AudioTransferBase):
    async def stream_audio(self, audio_chunk_iterator: AsyncIterator[AudioChunk]):
        logger.info("Got a new gRPC stream : Receiving audio chunks")

        result = False
        payload = None

        try:
            load_path = await write_stream_to_file(audio_chunk_iterator)
            logger.info("Successfully saved stream to file : {path}", path=load_path)
            task: TranscriptionTask = await AppWorker.get_instance().get_transcription(load_path)
            result, payload, message = await get_transcription_result(task)
        except Exception as e:
            logger.error("Failed to save stream to file {err}", err=e.__repr__())
            message = e.__repr__()

        return Response(result=result, message=message, payload=payload)
