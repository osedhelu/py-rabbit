import logging
import time
from typing import Optional

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError

from core.config.settings import RABBITMQ_CONFIG

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    _instance: Optional["RabbitMQConnection"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.url = RABBITMQ_CONFIG["url"]
        self.heartbeat = RABBITMQ_CONFIG["heartbeat"]
        self.connection_attempts = RABBITMQ_CONFIG["connection_attempts"]
        self.retry_delay = RABBITMQ_CONFIG["retry_delay"]

        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def connect(self) -> bool:
        """Establece la conexión con RabbitMQ con manejo de reconexión automática."""
        parameters = pika.URLParameters(self.url)
        parameters.heartbeat = self.heartbeat
        parameters.connection_attempts = self.connection_attempts
        parameters.retry_delay = self.retry_delay

        attempts = 0
        while attempts < self.connection_attempts:
            try:
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                logger.info("Conexión establecida con RabbitMQ")
                return True
            except (AMQPConnectionError, AMQPChannelError) as e:
                attempts += 1
                logger.error(
                    f"Error al conectar con RabbitMQ (intento {attempts}/{self.connection_attempts}): {str(e)}"
                )
                if attempts < self.connection_attempts:
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Número máximo de intentos de conexión alcanzado")
                    return False

    def reconnect(self) -> bool:
        """Intenta reconectar con RabbitMQ."""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                logger.error(f"Error al cerrar la conexión: {str(e)}")

        return self.connect()

    def is_connected(self) -> bool:
        """Verifica si la conexión está activa."""
        return self.connection is not None and self.connection.is_open

    def close(self):
        """Cierra la conexión con RabbitMQ."""
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                logger.info("Conexión con RabbitMQ cerrada correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar la conexión: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
