from typing import Callable

from ..entities.message import Message
from ..repositories.message_repository import MessageRepository


class ReceiveMessageUsecase:
    """Caso de uso para recibir mensajes"""

    def __init__(self, repository: MessageRepository) -> None:
        self.repository = repository

    def execute(self, message_callback: Callable[[Message, MessageRepository], None]) -> None:
        """Ejecuta el caso de uso"""

        def wrapped_callback(message: Message) -> None:
            message_callback(message, self.repository)

        self.repository.consume(wrapped_callback)
