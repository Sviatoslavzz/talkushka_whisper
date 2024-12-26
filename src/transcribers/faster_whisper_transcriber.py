from dataclasses import asdict, dataclass
from pathlib import Path

from faster_whisper import WhisperModel
from loguru import logger

from .abscract_transcriber import AbstractTranscriber


class FasterWhisperTranscriber(AbstractTranscriber):
    FASTER_WHISPER_FORMATS = ["mp3", "mp4", "m4a", "wav", "webm", "mov", "ogg", "opus"]

    @dataclass
    class Config:
        model_size_or_path: str
        device: str = "cpu"
        device_index: int | list[int] = 0
        compute_type: str = "int8"
        cpu_threads: int = 0
        num_workers: int = 1
        download_root: str | None = None
        local_files_only: bool = False
        files: dict = None

    def __init__(self, model: str, device: str | None = "auto"):
        if not self.validate_model(model):
            logger.error("Model {model} is not valid", model=model)
            raise ValueError(f"Model {model} is not valid")
        self.config = self.Config(model_size_or_path=model, device=device)
        self.whisper_model = WhisperModel(**asdict(self.config))
        logger.debug("{cls} init with a model {model}", cls=self.__class__.__name__, model=model)

    @AbstractTranscriber._count_time
    def transcribe(self, path: Path) -> str:
        if path.suffix.lstrip(".") not in self.FASTER_WHISPER_FORMATS:
            logger.error("File format is not supported: {path}", path=path.suffix)
            raise NotImplementedError("File format is not supported")

        logger.info("{self} transcription started", self=self.__repr__())
        segments, info = self.whisper_model.transcribe(path.__fspath__())
        logger.info("Detected language {language} with probability {prob}", language=info.language,
                    prob=info.language_probability)
        result = ""
        for segment in segments:
            result += segment.text

        return result

    def __repr__(self):
        return f"{self.__class__.__name__}, model {self.config.model_size_or_path}"
