from talkushka_transcriber.transcribers.assemblyai import AssemblyaiTranscriber
from talkushka_transcriber.transcribers.base import AbstractTranscriber
from talkushka_transcriber.transcribers.faster_whisper import FasterWhisperTranscriber


def get_transcriber_cls(cls: str) -> type[AbstractTranscriber]:
    mapping = {
        # "WhisperTranscriber": WhisperTranscriber,
        "FasterWhisperTranscriber": FasterWhisperTranscriber,
        "AssemblyaiTranscriber": AssemblyaiTranscriber,
    }
    if cls not in mapping:
        raise AssertionError(f"Unknown transcriber class {cls}")

    return mapping[cls]
