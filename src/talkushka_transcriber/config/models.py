from functools import partial

from pydantic import BaseModel, Field, field_validator

from talkushka_transcriber.config.factory import get_transcriber_cls
from talkushka_transcriber.transcribers.base import AbstractTranscriber


class TranscriberConfig(BaseModel):
    q_size: int | None = Field(300, title="Process executor queue size")
    cls: type[AbstractTranscriber] | None = Field(
        default_factory=partial(get_transcriber_cls, "FasterWhisperTranscriber"),
        title="Transcriber class",
        description="Transcriber class, currently available only FasterWhisperTranscriber",
    )
    pool_size: int | None = Field(
        4, title="Transcriber worker pool size", description="How many transcription tasks could be run at parallel"
    )
    model_specific_settings: dict | None = Field(default_factory=dict, title="Model specific settings")

    @field_validator("cls", mode="before")
    @classmethod
    def validate_cls(cls, value) -> type[AbstractTranscriber]:
        return get_transcriber_cls(value)


class GrpcConfig(BaseModel):
    host: str | None = Field("localhost", title="gRPC server host")
    port: int | None = Field(50051, title="gRPC server port")


class BaseConfig(BaseModel):
    grpc_server: GrpcConfig
    transcriber: TranscriberConfig
