from loguru import logger

from src.application import app


logger.add(
    "main.log",
    format="{time} {level} {message}",
    level="TRACE",
    rotation="10 MB",
    compression="zip",
)

__all__ = ["app"]
