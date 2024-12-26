from pathlib import Path

from transcribers.whisper_transcriber import WhisperTranscriber
# from transcribers.faster_whisper_transcriber import FasterWhisperTranscriber

transcriber = WhisperTranscriber("small")

res = transcriber.transcribe(Path("../data/audio.m4a"))

print(res)
