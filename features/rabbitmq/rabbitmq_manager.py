import logging
from typing import Optional

from features.rabbitmq.rabbitmq_connection_client import RabbitMQClient
from features.rabbitmq.rabbitmq_connection_server import RabbitMQServer

from .conexion import RabbitMQConnection

logger = logging.getLogger(__name__)


class RabbitMQManager:
    _instance: Optional["RabbitMQManager"] = None
    _connection: Optional[RabbitMQConnection] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self._connection = None

    @property
    def connection(self) -> RabbitMQConnection:
        """Obtiene la conexión actual o crea una nueva si no existe."""
        if self._connection is None or not self._connection.is_connected():
            self._connection = RabbitMQConnection()
            if not self._connection.connect():
                logger.error("No se pudo establecer la conexión con RabbitMQ")
                raise ConnectionError("No se pudo establecer la conexión con RabbitMQ")
        return self._connection

    def get_channel(self):
        """Obtiene el canal de la conexión actual."""
        return self.connection.channel

    def reconnect(self) -> bool:
        """Intenta reconectar con RabbitMQ."""
        if self._connection:
            return self._connection.reconnect()
        return False

    def conexionClient(self):
        return RabbitMQClient(self.connection)

    def conexionServer(self):
        channel = self.get_channel()
        return RabbitMQServer(channel)

    def close(self):
        """Cierra la conexión con RabbitMQ."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
