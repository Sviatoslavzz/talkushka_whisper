import asyncio
import signal
import ssl

from grpclib.server import Server
from loguru import logger

from config.models import GrpcConfig
from service.audio_transfer import AudioTransfer
from utils import get_project_root


def get_ssl_context():
    """
    Create and configure an SSL context for the gRPC client.
    """
    try:
        cert_path = get_project_root() / "cert"
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_verify_locations(cafile=cert_path / "ca.crt")
        ssl_context.load_cert_chain(certfile=cert_path / "server.crt", keyfile=cert_path / "server.key")
    except Exception as e:
        logger.error("Failed to configure SSL context: {err}", err=e.__repr__())
        raise e

    return ssl_context


async def serve(config: GrpcConfig):
    """
    Launch the async gRPC server
    """
    server = Server([AudioTransfer()])
    stop_event = asyncio.Event()

    def handle_signal():
        nonlocal stop_event
        logger.warning("Received signal to stop a server")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_signal)

    try:
        await server.start(config.host, config.port, ssl=get_ssl_context())
        logger.info("gRPC server started at {host}:{port}", host=config.host, port=config.port)
        for task in asyncio.as_completed(
                [stop_event.wait(), server.wait_closed()],
        ):
            await task
            break
    except Exception as e:
        logger.error("Server stopped with exception: {err}", err=e.__repr__())
    finally:
        server.close()
        logger.info("gRPC server stopped")
