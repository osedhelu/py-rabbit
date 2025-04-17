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

    try:
        # Ejemplo de uso
        def handle_response(response):
            print("\nInformación del usuario recibida:")
            print(f"ID: {response.get('id')}")
            print(f"Nombre: {response.get('name')}")
            print(f"Teléfono: {response.get('phone')}")

        # Solicitar información de usuario
        usecase.get_user_info("456", handle_response)

        # Mantener el producer activo para recibir la respuesta
        datasource.channel.start_consuming()

    except KeyboardInterrupt:
        print("\n [*] Deteniendo producer...")
    finally:
        datasource.close()


if __name__ == "__main__":
    main()
