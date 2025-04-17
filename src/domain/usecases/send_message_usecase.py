import uuid
from typing import Any, Dict, Optional

from ..entities.message import Message
from ..repositories.message_repository import MessageCallback, MessageRepository


class SendMessageUsecase:
    """Caso de uso para enviar mensajes"""

    def __init__(self, repository: MessageRepository) -> None:
        self.repository = repository

    def execute(
        self, message_type: str, payload: Dict[str, Any], response_callback: Optional[MessageCallback] = None
    ) -> None:
        """
        Envía un mensaje y configura el callback para la respuesta

        Args:
            message_type: Tipo de mensaje
            payload: Datos del mensaje
            response_callback: Callback para manejar la respuesta
        """
        # Generar un ID único para la correlación
        correlation_id = str(uuid.uuid4())

        # Crear el mensaje con la cola de respuesta
        message = Message(
            type=message_type,
            payload=payload,
            response_queue=self.repository.datasource.response_queue,
            correlation_id=correlation_id,
        )

        # Configurar el callback de respuesta si se proporciona
        if response_callback:
            self.repository.setup_response_consumer(response_callback)

        # Publicar el mensaje
        self.repository.publish(message)
