# Py-Rabbit

Implementación de un sistema de mensajería usando RabbitMQ siguiendo los principios de Clean Architecture.

## Estructura del Proyecto

```
py-rabbit/
├── src/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── message.py        # Entidad Message
│   │   ├── repositories/
│   │   │   └── message_repository.py  # Interfaz del repositorio
│   │   └── usecases/
│   │       ├── send_message_usecase.py    # Caso de uso para enviar mensajes
│   │       └── receive_message_usecase.py # Caso de uso para recibir mensajes
│   └── infrastructure/
│       ├── datasources/
│       │   └── rabbitmq_datasource.py     # Implementación de RabbitMQ
│       └── repositories/
│           └── rabbitmq_repository.py     # Implementación del repositorio
├── producer.py        # Script para enviar mensajes
├── consumer.py        # Script para recibir mensajes
└── setup.py          # Configuración del proyecto
```

## Características

- Implementación de Clean Architecture
- Patrón Singleton para la conexión RabbitMQ
- Manejo automático de reconexiones
- Sistema de colas de respuesta
- Tipado estático con Python
- Manejo de errores robusto

## Requisitos

- Python 3.9+
- RabbitMQ
- Dependencias:
  - pika
  - python-dotenv

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd py-rabbit
```

2. Crear y activar un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate     # En Windows
```

3. Instalar dependencias:
```bash
pip install -e .
```

## Configuración

Crear un archivo `.env` en la raíz del proyecto:
```env
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_QUEUE=notifications
```

## Uso

### Producer (Enviar mensajes)

El producer envía mensajes y espera respuestas:

```bash
python producer.py
```

Características:
- Envía mensajes cada 5 segundos
- Configura automáticamente una cola de respuesta exclusiva
- Maneja las respuestas recibidas
- Reconexión automática en caso de fallos

### Consumer (Recibir mensajes)

El consumer recibe mensajes y envía respuestas:

```bash
python consumer.py
```

Características:
- Recibe mensajes de forma continua
- Procesa mensajes según su tipo
- Envía respuestas a la cola especificada
- Manejo de errores robusto

## Arquitectura

### Clean Architecture

El proyecto sigue los principios de Clean Architecture:

1. **Domain Layer**:
   - Entities: `Message`
   - Repositories: `MessageRepository` (interfaz)
   - Use Cases: `SendMessageUsecase`, `ReceiveMessageUsecase`

2. **Infrastructure Layer**:
   - Datasources: `RabbitMQDatasource`
   - Repositories: `RabbitMQRepository`

### Flujo de Mensajes

1. **Envío de Mensaje**:
   - Producer crea un mensaje con tipo y payload
   - Se genera un ID de correlación único
   - Se incluye la cola de respuesta del producer
   - El mensaje se envía a la cola principal

2. **Recepción de Mensaje**:
   - Consumer recibe el mensaje
   - Procesa el mensaje según su tipo
   - Crea una respuesta con el mismo ID de correlación
   - Envía la respuesta a la cola especificada

3. **Recepción de Respuesta**:
   - Producer recibe la respuesta en su cola exclusiva
   - Procesa la respuesta usando el callback

## Manejo de Errores

- Reconexión automática a RabbitMQ
- Manejo de colas existentes
- Validación de mensajes y respuestas
- Logs detallados para depuración

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 