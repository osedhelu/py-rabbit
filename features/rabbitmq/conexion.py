"""
Módulo que maneja la conexión con RabbitMQ.
Implementa un patrón Singleton para mantener una única instancia de conexión.
"""

import time
from typing import Optional

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError, StreamLostError

from core.config.settings import RABBITMQ_CONFIG
from core.utils.logging import get_logger

logger = get_logger(__name__)


class RabbitMQConnection:
    """
    Clase que maneja la conexión con RabbitMQ.
    Implementa el patrón Singleton para asegurar una única instancia de conexión.
    """

    _instance: Optional["RabbitMQConnection"] = None
    _connection: Optional[pika.BlockingConnection] = None
    _channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None
    _is_connecting = False

    def __new__(cls, *args, **kwargs):
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa la conexión con RabbitMQ."""
        if self._initialized:
            return

        self._initialized = True
        self.url = RABBITMQ_CONFIG["url"]
        self.heartbeat = RABBITMQ_CONFIG["heartbeat"]
        self.connection_attempts = RABBITMQ_CONFIG["connection_attempts"]
        self.retry_delay = RABBITMQ_CONFIG["retry_delay"]

    def _create_channel(self) -> bool:
        """
        Crea un nuevo canal de RabbitMQ.

        Returns:
            bool: True si se creó el canal correctamente, False en caso contrario
        """
        try:
            if self._connection and self._connection.is_open:
                self._channel = self._connection.channel()
                return True
            return False
        except Exception as e:
            logger.error(f"Error al crear canal: {str(e)}")
            return False

    def connect(self) -> bool:
        """
        Establece la conexión con RabbitMQ con manejo de reconexión automática.

        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        if self._is_connecting:
            logger.warning("Ya existe un intento de conexión en curso")
            return False

        self._is_connecting = True
        try:
            parameters = pika.URLParameters(self.url)
            parameters.heartbeat = self.heartbeat
            parameters.connection_attempts = self.connection_attempts
            parameters.retry_delay = self.retry_delay

            attempts = 0
            while attempts < self.connection_attempts:
                try:
                    if self._connection and self._connection.is_open:
                        self._connection.close()

                    self._connection = pika.BlockingConnection(parameters)
                    if self._create_channel():
                        logger.info("Conexión y canal establecidos correctamente")
                        return True
                except (AMQPConnectionError, AMQPChannelError, StreamLostError) as e:
                    attempts += 1
                    logger.error(
                        f"Error al conectar con RabbitMQ (intento {attempts}/{self.connection_attempts}): {str(e)}"
                    )
                    if attempts < self.connection_attempts:
                        time.sleep(self.retry_delay)
                    else:
                        logger.error("Número máximo de intentos de conexión alcanzado")
                        return False
        finally:
            self._is_connecting = False

    def reconnect(self) -> bool:
        """
        Intenta reconectar con RabbitMQ.

        Returns:
            bool: True si la reconexión fue exitosa, False en caso contrario
        """
        if self._is_connecting:
            logger.warning("Ya existe un intento de reconexión en curso")
            return False

        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
            self._connection = None
            self._channel = None
        except Exception as e:
            logger.error(f"Error al cerrar la conexión: {str(e)}")

        return self.connect()

    def is_connected(self) -> bool:
        """
        Verifica si la conexión y el canal están activos.

        Returns:
            bool: True si la conexión y el canal están activos, False en caso contrario
        """
        try:
            return (
                self._connection is not None
                and self._connection.is_open
                and self._channel is not None
                and self._channel.is_open
            )
        except Exception:
            return False

    def ensure_channel(self) -> bool:
        """
        Asegura que el canal esté activo, recreándolo si es necesario.

        Returns:
            bool: True si el canal está activo, False en caso contrario
        """
        if not self.is_connected():
            return self.reconnect()

        if not self._channel or not self._channel.is_open:
            return self._create_channel()

        return True

    def process_data_events(self, time_limit: float = 1.0):
        """Procesa eventos de datos de la conexión."""
        if self._connection:
            self._connection.process_data_events(time_limit=time_limit)

    @property
    def channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """
        Obtiene el canal actual, asegurando que esté activo.

        Returns:
            pika.adapters.blocking_connection.BlockingChannel: El canal activo

        Raises:
            ConnectionError: Si no se puede establecer el canal
        """
        if not self.ensure_channel():
            raise ConnectionError("No se pudo establecer el canal")
        return self._channel

    def close(self):
        """Cierra la conexión con RabbitMQ."""
        try:
            if self._connection and self._connection.is_open:
                self._connection.close()
                logger.info("Conexión con RabbitMQ cerrada correctamente")
        except Exception as e:
            logger.error(f"Error al cerrar la conexión: {str(e)}")
        finally:
            self._connection = None
            self._channel = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
