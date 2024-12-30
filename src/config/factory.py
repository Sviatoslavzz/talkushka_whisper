from transcribers.abscract_transcriber import AbstractTranscriber
from transcribers.faster_whisper_transcriber import FasterWhisperTranscriber


def get_transcriber_cls(cls: str) -> type[AbstractTranscriber]:
    mapping = {
        # "WhisperTranscriber": WhisperTranscriber,
        "FasterWhisperTranscriber": FasterWhisperTranscriber,
    }
    if cls not in mapping:
        raise AssertionError(f"Unknown transcriber class {cls}")

    return mapping[cls]
