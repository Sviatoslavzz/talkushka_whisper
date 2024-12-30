import asyncio

from loguru import logger

from app_worker import AppWorker
from config.base import YAMLConfig
from parser import get_parser
from service.server import serve
from utils import create_saving_dir


async def launch_server():
    parser = get_parser()
    args = parser.parse_args()
    config: YAMLConfig = args.config

    create_saving_dir("data")
    AppWorker(config.data.transcriber)

    await serve(config.data.grpc_server)


def main():
    try:
        asyncio.run(launch_server())
    except Exception as e:
        logger.warning(f"Turning off {e.__repr__()}")


if __name__ == "__main__":
    main()
