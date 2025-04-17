from typing import Dict, Optional
from ..datasource.rabbitmq_datasource import (
    RabbitMQDatasource,
    RabbitMessage,
    RabbitResponse,
    ResponseCallback,
)
from ..providers.user_provider import UserProvider


class UserRepository:
    def __init__(self, datasource: RabbitMQDatasource, provider: UserProvider) -> None:
        self.datasource = datasource
        self.provider = provider

    def request_user_info(self, user_id: str, callback: ResponseCallback) -> None:
        """Solicita información de un usuario"""
        message: RabbitMessage = {
            "type": "get_user",
            "user_id": user_id,
            "response_queue": self.datasource.response_queue,
        }
        self.datasource.setup_response_consumer(callback)
        self.datasource.publish(message)

    def handle_user_request(self, message: Dict) -> None:
        """Procesa una solicitud de información de usuario"""
        try:
            if message.get("type") != "get_user":
                return

            user_id: Optional[str] = message.get("user_id")
            response_queue: Optional[str] = message.get("response_queue")

            if not user_id or not response_queue:
                return

            user_info: RabbitResponse = self.provider.get_user(user_id)
            self.datasource.publish_response(response_queue, user_info)

        except Exception as e:
            print(f"Error al procesar solicitud de usuario: {str(e)}")
