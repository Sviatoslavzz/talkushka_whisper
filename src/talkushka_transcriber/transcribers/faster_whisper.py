from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel
from loguru import logger
from pydantic import BaseModel

from talkushka_transcriber.transcribers.base import AbstractTranscriber


class FasterWhisperTranscriber(AbstractTranscriber):
    FASTER_WHISPER_FORMATS = ["mp3", "mp4", "m4a", "wav", "webm", "mov", "ogg", "opus"]

    class Config(BaseModel):
        model_size_or_path: str = "small"
        device: str = "cpu"
        device_index: int | list[int] = 0
        compute_type: str = "int8"
        cpu_threads: int = 0
        num_workers: int = 1
        download_root: str | None = None
        local_files_only: bool = False
        files: dict = None

    def __init__(self, config: dict[str, Any]):
        if not self.validate_model(config.get("model", "")):
            logger.error("Model {model} is not valid", model=config.get("model", ""))
            raise ValueError(f"Model {config.get('model', '')} is not valid")
        self.config = self.Config(**config)
        self.whisper_model = WhisperModel(**self.config.model_dump(exclude_none=True))
        logger.debug("{cls} init with a model {model}", cls=self.__class__.__name__, model=config["model"])

    @AbstractTranscriber._count_time
    def transcribe(self, path: Path) -> str:
        if path.suffix.lstrip(".") not in self.FASTER_WHISPER_FORMATS:
            logger.error("File format is not supported: {path}", path=path.suffix)
            raise NotImplementedError("File format is not supported")

        logger.info("{self} transcription started", self=self.__repr__())
        segments, info = self.whisper_model.transcribe(path.__fspath__())
        logger.info(
            "Detected language {language} with probability {prob}",
            language=info.language,
            prob=info.language_probability,
        )
        result = ""
        for segment in segments:
            result += segment.text

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}, model {self.config.model_size_or_path}"
