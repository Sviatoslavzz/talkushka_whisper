from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from time import time
from typing import Any

from loguru import logger


class AbstractTranscriber(ABC):
    @staticmethod
    def validate_model(model: str) -> bool:
        return model in [
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "distil-small.en",
            "medium",
            "medium.en",
            "distil-medium.en",
            "large-v1",
            "large-v2",
            "large-v3",
            "large",
            "distil-large-v2",
            "distil-large-v3",
        ]

    @staticmethod
    def _count_time(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time()
            res = func(*args, **kwargs)
            logger.debug("Transcribed in {diff} seconds", diff=time() - start)
            return res

        return wrapper

    @abstractmethod
    def transcribe(self, path: Path) -> str:
        pass

    @abstractmethod
    def __repr__(self):
        pass
