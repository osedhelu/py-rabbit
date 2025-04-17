from src.domain.entities.message import Message
from src.domain.usecases.send_message_usecase import SendMessageUsecase
from src.infrastructure.datasources.rabbitmq_datasource import RabbitMQDatasource
from src.infrastructure.repositories.rabbitmq_repository import RabbitMQRepository


def main():
    # Configuración inicial
    datasource = RabbitMQDatasource()
    repository = RabbitMQRepository(datasource)

    # Casos de uso
    send_usecase = SendMessageUsecase(repository)

    try:

        def handle_response(message: Message) -> None:
            """Maneja una respuesta recibida"""
            print("\nRespuesta recibida:")
            print(f"Tipo: {message.type}")
            print(f"Payload: {message.payload}")
            print(f"Response Queue: {message.response_queue}")
            print(f"Correlation ID: {message.correlation_id}")

        # Configurar el consumidor de respuestas antes de enviar el mensaje
        print(f"\nCola de respuesta configurada: {datasource.response_queue}")
        datasource.setup_response_consumer(handle_response)

        # Ejemplo de envío de mensaje
        print("\nEnviando mensaje...")
        send_usecase.execute(
            message_type="get_user",
            payload={"user_id": "123"},
            response_callback=handle_response,
        )

        # Mantener el producer activo para recibir la respuesta
        print("\nEsperando respuestas...")
        datasource.channel.start_consuming()

    except KeyboardInterrupt:
        print("\n [*] Deteniendo producer...")
    finally:
        datasource.close()


if __name__ == "__main__":
    main()
