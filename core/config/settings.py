import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# Configuración de la aplicación
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-por-defecto")

# Configuración de RabbitMQ
RABBITMQ_URL = os.getenv("RABBITMQ_URL")
if not RABBITMQ_URL:
    logger.error("RABBITMQ_URL no está configurada en las variables de entorno")
    raise ValueError("RABBITMQ_URL no está configurada en las variables de entorno")

RABBITMQ_CONFIG: dict[str, Any] = {
    "url": RABBITMQ_URL,
    "queue": os.getenv("RABBITMQ_QUEUE", "notifications"),
    "response_queue": os.getenv("RABBITMQ_RESPONSE_QUEUE", "responses"),
    "heartbeat": 60,
    "connection_attempts": 5,
    "retry_delay": 5,
}

# Configuración de FastAPI
FASTAPI_CONFIG: dict[str, Any] = {
    "title": "Microservicio RabbitMQ",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json",
}

# Configuración de Logging
LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}
