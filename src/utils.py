import importlib.metadata as im
import tomllib
from pathlib import Path

from loguru import logger


def get_package_name() -> str:
    pyproject_f = Path(__file__).parent.parent / "pyproject.toml"
    name = ""
    try:
        if not pyproject_f.is_file():
            raise FileNotFoundError(f"{pyproject_f} does not exist.")

        with pyproject_f.open(mode="rb") as f:
            pyproject = tomllib.load(f)
        name = pyproject["project"]["name"]
    except Exception as e:
        logger.error(f"Failed to get package name: {e}")

    return name


def get_version() -> str:
    package_name = get_package_name()
    version = ""
    try:
        version = im.version(package_name)
    except im.PackageNotFoundError:
        logger.error(f"Version not found for package {package_name}")

    return version


def get_project_root() -> Path:
    path_ = Path(__file__).parent
    while path_.name != "src":
        path_ = path_.parent

    return path_.parent


def create_saving_dir(dir_: str) -> Path:
    absolute_path = get_project_root()
    dir_ = absolute_path / dir_
    if not dir_.is_dir():
        dir_.mkdir()
        logger.info(f"Saving directory created: {dir_}")
    logger.info(f"Saving directory set up: {dir_}")
    return dir_
