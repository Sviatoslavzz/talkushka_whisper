from os import getenv
from pathlib import Path
from typing import Any

import assemblyai as aai
from assemblyai import SpeechModel
from loguru import logger
from pydantic import BaseModel

from talkushka_transcriber.transcribers.base import AbstractTranscriber


class AssemblyaiTranscriber(AbstractTranscriber):
    class Config(BaseModel):
        language_detection: bool | None = True
        language_code: str | None = None
        language_confidence_threshold: float | None = 0.6
        speech_threshold: float | None = 0.3
        speaker_labels: bool | None = None
        speech_model: SpeechModel | None = SpeechModel.nano

    def __init__(self, config: dict[str, Any]):
        try:
            aai.settings.api_key = getenv(config["api_key_env"])
        except Exception as e:
            logger.error("Environment variable api_key_env not set {err}", err=e.__repr__())
            raise e

        self.config = self.Config(**config)
        print(f"actual config: {self.config}")
        self.transcriber = aai.Transcriber(config=aai.TranscriptionConfig(**self.config.model_dump(exclude_none=True)))

        logger.debug("{cls} initialized", cls=self.__class__.__name__)

    @AbstractTranscriber._count_time
    def transcribe(self, path: Path) -> str:
        logger.info("{self} transcription started", self=self.__repr__())
        text = ""
        transcript = self.transcriber.transcribe(path.__fspath__())

        if transcript.status == aai.TranscriptStatus.error:
            logger.error("{self} transcription failed {err}", self=self.__repr__(), err=transcript.status)
            return text

        if self.config.speaker_labels and transcript.utterances:
            for utterance in transcript.utterances:
                text += f"Speaker {utterance.speaker}: {utterance.text}\n"
        else:
            text = transcript.text

        return text

    def __repr__(self):
        return f"{self.__class__.__name__}"
