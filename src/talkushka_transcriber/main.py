import asyncio

from talkushka_transcriber.app_worker import AppWorker
from talkushka_transcriber.config.base import YAMLConfig
from talkushka_transcriber.config.logger_settings import logger
from talkushka_transcriber.service.server import serve
from talkushka_transcriber.utils import create_saving_dir
from talkushka_transcriber.utils.parser import get_parser


async def launch_server():
    parser = get_parser()
    args = parser.parse_args()
    config: YAMLConfig = args.config

    create_saving_dir("data")
    AppWorker(config.data.transcriber)

    await serve(config.data.grpc_server)

    AppWorker.get_instance().stop_executors()


def main():
    try:
        asyncio.run(launch_server())
    except Exception as e:
        logger.warning(f"Turning off {e.__repr__()}")


if __name__ == "__main__":
    main()
