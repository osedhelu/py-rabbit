from src.domain.entities.message import Message
from src.domain.usecases.receive_message_usecase import ReceiveMessageUsecase
from src.infrastructure.datasources.rabbitmq_datasource import RabbitMQDatasource
from src.infrastructure.repositories.rabbitmq_repository import RabbitMQRepository


def handle_message(message: Message, repository: RabbitMQRepository) -> None:
    """Maneja un mensaje recibido"""
    print("\nMensaje recibido:")
    print(f"Tipo: {message.type}")
    print(f"Payload: {message.payload}")
    print(f"Response Queue: {message.response_queue}")
    print(f"Correlation ID: {message.correlation_id}")

    # Ejemplo de respuesta
    if message.type == "get_user":
        if not message.response_queue:
            print("Error: No se recibió cola de respuesta en el mensaje")
            return

        response = Message(
            type="user_response",
            payload={"id": "123", "name": "Juan Pérez", "phone": "555-1234"},
            response_queue=message.response_queue,
            correlation_id=message.correlation_id,
        )
        repository.publish_response(response)


def main():
    # Configuración inicial
    datasource = RabbitMQDatasource()
    repository = RabbitMQRepository(datasource)

    # Caso de uso
    receive_usecase = ReceiveMessageUsecase(repository)

    try:
        # Iniciar el consumo de mensajes
        receive_usecase.execute(handle_message)
    except KeyboardInterrupt:
        print("\n [*] Deteniendo consumer...")
    finally:
        datasource.close()


if __name__ == "__main__":
    main()
