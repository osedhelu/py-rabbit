import logging
import logging.config
import os
import sys
from typing import Any, Dict

from core.config.settings import LOGGING_CONFIG


class ColoredFormatter(logging.Formatter):
    """Formateador personalizado que agrega colores a los logs"""

    # Códigos ANSI para colores llamativos
    COLORS = {
        "DEBUG": "\033[38;5;39m",  # Azul claro
        "INFO": "\033[38;5;118m",  # Verde brillante
        "WARNING": "\033[38;5;226m",  # Amarillo brillante
        "ERROR": "\033[38;5;196m",  # Rojo brillante
        "CRITICAL": "\033[48;5;196m\033[38;5;231m",  # Fondo rojo, texto blanco
        "RESET": "\033[0m",  # Resetear colores
        "FILENAME": "\033[38;5;196m",  # Rojo brillante para el nombre del archivo
    }

    def format(self, record):
        levelname = record.levelname

        # Extraer el nombre del archivo del path completo
        filename = os.path.basename(record.pathname)

        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            # Agregar el nombre del archivo en rojo entre corchetes
            record.msg = (
                f"[{self.COLORS['FILENAME']}{filename}{self.COLORS['RESET']}] -> {record.msg}{self.COLORS['RESET']}"
            )

        return super().format(record)


def setup_logging() -> None:
    """Configura el logging de la aplicación con colores llamativos"""
    # Configuración para desarrollo que muestra logs en formato colorido
    config = LOGGING_CONFIG.copy()

    # Asegurar que la configuración tenga el formato deseado para desarrollo
    config.setdefault("formatters", {})
    config["formatters"]["colored"] = {"()": ColoredFormatter, "format": "%(levelname)s: %(message)s"}

    # Configurar handlers para mostrar en consola con colores
    config.setdefault("handlers", {})
    config["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "level": "INFO",
        "formatter": "colored",
        "stream": sys.stdout,
    }

    # Configurar loggers
    config.setdefault("loggers", {})
    config["loggers"]["uvicorn.access"] = {
        "handlers": ["console"],
        "level": "INFO",
        "propagate": False,
    }

    # Configurar logger raíz para que todos los loggers hereden la configuración
    config.setdefault("root", {})
    config["root"] = {
        "handlers": ["console"],
        "level": "INFO",
    }

    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger con el nombre especificado"""
    return logging.getLogger(name)


def log_message(logger: logging.Logger, level: int, message: str, **kwargs: Any) -> None:
    """Registra un mensaje con el nivel especificado"""
    logger.log(level, message, **kwargs)


def configure_uvicorn_logging() -> Dict[str, Any]:
    """
    Retorna la configuración de logging para Uvicorn

    Returns:
        Dict[str, Any]: Configuración de logging para Uvicorn
    """
    return {
        "log_config": None,  # Desactivar la configuración por defecto
        "access_log": True,
        "use_colors": True,
    }
