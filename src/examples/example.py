from domain.entities.message import Message
from domain.usecases.receive_message_usecase import ReceiveMessageUsecase
from domain.usecases.send_message_usecase import SendMessageUsecase
from infrastructure.datasources.rabbitmq_datasource import RabbitMQDatasource
from infrastructure.repositories.rabbitmq_repository import RabbitMQRepository


def handle_message(message: Message) -> None:
    """Maneja un mensaje recibido"""
    print("\nMensaje recibido:")
    print(f"Tipo: {message.type}")
    print(f"Payload: {message.payload}")

    # Ejemplo de respuesta
    if message.type == "get_user":
        response = Message(
            type="user_response",
            payload={"id": "123", "name": "Juan Pérez", "phone": "555-1234"},
            response_queue=message.response_queue,
            correlation_id=message.correlation_id,
        )
        repository.publish_response(response)


def handle_response(message: Message) -> None:
    """Maneja una respuesta recibida"""
    print("\nRespuesta recibida:")
    print(f"Tipo: {message.type}")
    print(f"Payload: {message.payload}")


if __name__ == "__main__":
    # Configuración inicial
    datasource = RabbitMQDatasource()
    repository = RabbitMQRepository(datasource)

    # Casos de uso
    send_usecase = SendMessageUsecase(repository)
    receive_usecase = ReceiveMessageUsecase(repository)

    # Ejemplo de envío de mensaje
    send_usecase.execute(
        message_type="get_user",
        payload={"user_id": "123"},
        response_callback=handle_response,
    )

    # Ejemplo de recepción de mensajes
    receive_usecase.execute(message_callback=handle_message)
