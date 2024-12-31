# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/example.proto
# plugin: python-betterproto
# This file has been @generated

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    AsyncIterator,
    Dict,
    Iterable,
    Optional,
    Union,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase

if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class AudioChunk(betterproto.Message):
    payload: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class Response(betterproto.Message):
    result: bool = betterproto.bool_field(1)
    payload: bytes | None = betterproto.bytes_field(2, optional=True)
    message: str | None = betterproto.string_field(4, optional=True)


class AudioTransferStub(betterproto.ServiceStub):
    async def stream_audio(
        self,
        audio_chunk_iterator: AsyncIterable[AudioChunk] | Iterable[AudioChunk],
        *,
        timeout: float | None = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> AsyncIterator[Response]:
        async for response in self._stream_stream(
            "/AudioTransfer/StreamAudio",
            audio_chunk_iterator,
            AudioChunk,
            Response,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response


class AudioTransferBase(ServiceBase):

    async def stream_audio(
        self, audio_chunk_iterator: AsyncIterator[AudioChunk]
    ) -> AsyncIterator[Response]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)
        yield Response()

    async def __rpc_stream_audio(
        self, stream: "grpclib.server.Stream[AudioChunk, Response]"
    ) -> None:
        request = stream.__aiter__()
        await self._call_rpc_handler_server_stream(
            self.stream_audio,
            stream,
            request,
        )

    def __mapping__(self) -> dict[str, grpclib.const.Handler]:
        return {
            "/AudioTransfer/StreamAudio": grpclib.const.Handler(
                self.__rpc_stream_audio,
                grpclib.const.Cardinality.STREAM_STREAM,
                AudioChunk,
                Response,
            ),
        }
