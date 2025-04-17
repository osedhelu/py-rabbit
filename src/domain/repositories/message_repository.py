from abc import ABC, abstractmethod

from ..entities.message import Message


class MessageCallback(ABC):
    """Protocolo para callbacks de mensajes"""

    @abstractmethod
    def __call__(self, message: Message) -> None:
        """Procesa un mensaje recibido"""
        pass


class MessageRepository(ABC):
    """Interfaz para el repositorio de mensajes"""

    @abstractmethod
    def publish(self, message: Message) -> None:
        """Publica un mensaje"""
        pass

    @abstractmethod
    def consume(self, callback: MessageCallback) -> None:
        """Consume mensajes"""
        pass

    @abstractmethod
    def setup_response_consumer(self, callback: MessageCallback) -> None:
        """Configura el consumidor de respuestas"""
        pass

    @abstractmethod
    def publish_response(self, response: Message) -> None:
        """Publica una respuesta"""
        pass

    @abstractmethod
    def close(self) -> None:
        """Cierra la conexión"""
        pass
