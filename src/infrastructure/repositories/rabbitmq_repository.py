from src.domain.entities.message import Message
from src.domain.repositories.message_repository import MessageCallback, MessageRepository
from src.infrastructure.datasources.rabbitmq_datasource import RabbitMQDatasource


class RabbitMQRepository(MessageRepository):
    """Implementación del repositorio de mensajes usando RabbitMQ"""

    def __init__(self, datasource: RabbitMQDatasource) -> None:
        self.datasource = datasource

    def publish(self, message: Message) -> None:
        """Publica un mensaje"""
        self.datasource.publish(message)

    def consume(self, callback: MessageCallback) -> None:
        """Consume mensajes"""
        self.datasource.consume(callback)

    def setup_response_consumer(self, callback: MessageCallback) -> None:
        """Configura el consumidor de respuestas"""
        self.datasource.setup_response_consumer(callback)

    def publish_response(self, response: Message) -> None:
        """Publica una respuesta"""
        self.datasource.publish_response(response)

    def close(self) -> None:
        """Cierra la conexión"""
        self.datasource.close()
