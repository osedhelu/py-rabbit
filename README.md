# Microservicio RabbitMQ + FastAPI

Microservicio que utiliza RabbitMQ como medio de comunicación y FastAPI para exponer endpoints REST, siguiendo una arquitectura limpia y modular.

## Características

- Arquitectura limpia y modular siguiendo Clean Architecture
- Comunicación asíncrona con RabbitMQ
- API REST con FastAPI
- Manejo de errores robusto con circuit breakers
- Logging estructurado
- Configuración mediante variables de entorno
- Pruebas unitarias y de integración
- Documentación OpenAPI
- Monitoreo y métricas
- Seguridad implementada

## Estructura del Proyecto

```
py-rabbit/
├── features/                    # Características del sistema
│   ├── rabbitmq/               # Feature de RabbitMQ
│   │   ├── api/               # Endpoints específicos de RabbitMQ
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   ├── domain/           # Lógica de negocio de RabbitMQ
│   │   │   ├── entities/    # Entidades específicas
│   │   │   └── usecases/    # Casos de uso
│   │   └── infrastructure/  # Implementaciones técnicas
│   │       ├── datasources/ # Fuentes de datos
│   │       └── repositories/ # Repositorios
│   └── users/                # Feature de Usuarios
│       ├── api/             # Endpoints de usuarios
│       ├── domain/         # Lógica de negocio de usuarios
│       └── infrastructure/ # Implementaciones técnicas
├── core/                     # Componentes centrales compartidos
│   ├── config/             # Configuraciones
│   └── utils/             # Utilidades comunes
├── tests/                  # Pruebas
│   ├── features/         # Pruebas por feature
│   └── core/            # Pruebas de componentes centrales
├── .env.example          # Variables de entorno de ejemplo
├── .gitignore
├── pyproject.toml       # Configuración del proyecto
├── README.md
└── requirements.txt     # Dependencias
```

## Requisitos

- Python 3.9+
- RabbitMQ
- pip
- Docker (opcional)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/py-rabbit.git
cd py-rabbit
```

2. Crear y activar entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Uso

1. Iniciar el servidor FastAPI:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. Iniciar el worker de RabbitMQ:
```bash
python worker.py
```

3. Acceder a la documentación de la API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuración

### RabbitMQ
```python
RABBITMQ_CONFIG = {
    "host": "localhost",
    "port": 5672,
    "username": "guest",
    "password": "guest",
    "virtual_host": "/",
    "heartbeat": 60,
    "connection_attempts": 5,
    "retry_delay": 5
}
```

### FastAPI
```python
FASTAPI_CONFIG = {
    "title": "Microservicio RabbitMQ",
    "version": "1.0.0",
    "docs_url": "/docs",
    "redoc_url": "/redoc",
    "openapi_url": "/openapi.json"
}
```

## Estructura de Mensajes RabbitMQ

```python
{
    "type": "event_type",      # Tipo de evento/acción
    "payload": {               # Datos del mensaje
        "key": "value"
    },
    "metadata": {              # Metadatos
        "timestamp": "ISO8601",
        "correlation_id": "uuid",
        "response_queue": "queue_name"
    }
}
```

## Ejemplo de Uso

```python
import requests

# Enviar mensaje
response = requests.post(
    "http://localhost:8000/rabbitmq/send",
    json={
        "type": "get_user",
        "payload": {"user_id": "123"},
        "metadata": {
            "timestamp": "2024-04-18T12:00:00Z",
            "correlation_id": "uuid",
            "response_queue": "responses"
        }
    }
)

# Obtener correlation_id
correlation_id = response.json()["correlation_id"]

# Obtener respuesta
response = requests.get(
    f"http://localhost:8000/rabbitmq/responses/{correlation_id}"
)
```

## Pruebas

Ejecutar las pruebas:
```bash
pytest
```

## Monitoreo

- Logs estructurados
- Métricas de rendimiento
- Alertas configuradas
- Trazabilidad de mensajes

## Seguridad

- Encriptación de datos sensibles
- Validación de inputs
- Rate limiting implementado
- CORS configurado

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información. 