from typing import Dict
from ..repository.user_repository import UserRepository
from ..datasource.rabbitmq_datasource import RabbitResponse, ResponseCallback


class UserUsecase:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    def get_user_info(self, user_id: str, callback: ResponseCallback) -> None:
        """Caso de uso para obtener información de usuario"""

        def handle_response(response: RabbitResponse) -> None:
            print("\nInformación del usuario recibida:")
            print(f"ID: {response.get('id')}")
            print(f"Nombre: {response.get('name')}")
            print(f"Teléfono: {response.get('phone')}")
            callback(response)

        self.repository.request_user_info(user_id, handle_response)

    def process_user_request(self, message: Dict) -> None:
        """Caso de uso para procesar solicitudes de usuario"""
        print(f"Procesando solicitud de usuario: {message}")
        self.repository.handle_user_request(message)
