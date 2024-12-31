from dataclasses import dataclass
from pathlib import Path

MB = 1024 * 1024

@dataclass(slots=True)
class TranscriptionTask:
    id: str
    message: str | None = None
    result: bool | None = False
    audio_path: Path | None = None
    text_path: Path | None = None
