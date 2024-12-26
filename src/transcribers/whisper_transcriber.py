import warnings
from pathlib import Path

import whisper
from loguru import logger

from .abscract_transcriber import AbstractTranscriber

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")


class WhisperTranscriber(AbstractTranscriber):
    WHISPER_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm", "mov"]

    def __init__(self, model: str):
        if not self.validate_model(model):
            logger.error(f"Model {model} is not valid")
            raise ValueError

        self.model = model
        self.whisper_model = whisper.load_model(model)

        logger.debug("{cls} init with a model {model}", cls=self.__class__.__name__, model=model)

    @AbstractTranscriber._count_time
    def transcribe(self, path: Path) -> str:
        if path.suffix.lstrip(".") not in self.WHISPER_FORMATS:
            logger.error("File format is not supported: {suffix}", suffix=path.suffix)
            raise NotImplementedError("File format is not supported")

        logger.info("WhisperTranscriber transcription started")
        result = self.whisper_model.transcribe(path.__fspath__())

        return result["text"]

    def __repr__(self):
        return f"{self.__class__.__name__}, model {self.model}"
