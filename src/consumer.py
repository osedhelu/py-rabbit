import json
from domain.datasource.rabbitmq_datasource import RabbitMQDatasource
from domain.providers.user_provider import UserProvider
from domain.repository.user_repository import UserRepository
from domain.usecase.user_usecase import UserUsecase


def main():
    # Inicializar componentes
    datasource = RabbitMQDatasource()
    provider = UserProvider()
    repository = UserRepository(datasource, provider)
    usecase = UserUsecase(repository)

    def message_callback(ch, method, properties, body):
        """Callback para procesar mensajes recibidos"""
        try:
            message = json.loads(body)
            usecase.process_user_request(message)
        except json.JSONDecodeError:
            print(" [x] Error al decodificar el mensaje JSON")
        except Exception as e:
            print(f" [x] Error al procesar el mensaje: {str(e)}")

    try:
        print(" [*] Esperando solicitudes. Presiona CTRL+C para salir")
        datasource.start_consuming(message_callback)
    except KeyboardInterrupt:
        print(" [*] Deteniendo consumidor...")
    finally:
        datasource.close()


if __name__ == "__main__":
    main()
