import logging.config
from typing import Any

from core.config.settings import LOGGING_CONFIG


def setup_logging() -> None:
    """Configura el logging de la aplicación"""
    logging.config.dictConfig(LOGGING_CONFIG)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(name)


def log_message(logger: logging.Logger, level: int, message: str, **kwargs: Any) -> None:
    """Registra un mensaje con el nivel especificado"""
    logger.log(level, message, **kwargs)
