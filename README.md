# Microservicio RabbitMQ + FastAPI

Microservicio que utiliza RabbitMQ como medio de comunicación y FastAPI para exponer endpoints REST.

## Características

- Arquitectura limpia y modular
- Comunicación asíncrona con RabbitMQ
- API REST con FastAPI
- Manejo de errores robusto
- Logging estructurado
- Configuración mediante variables de entorno

## Estructura del Proyecto

```
py-rabbit/
├── features/                    # Características del sistema
│   ├── rabbitmq/               # Feature de RabbitMQ
│   │   ├── api/               # Endpoints específicos de RabbitMQ
│   │   ├── domain/           # Lógica de negocio de RabbitMQ
│   │   └── infrastructure/  # Implementaciones técnicas
│   └── users/                # Feature de Usuarios
├── core/                     # Componentes centrales compartidos
├── tests/                  # Pruebas
├── .env.example          # Variables de entorno de ejemplo
└── requirements.txt     # Dependencias
```

## Requisitos

- Python 3.9+
- RabbitMQ
- pip

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
uvicorn src.main:app --reload
```

2. Iniciar el consumer de RabbitMQ:
```bash
python src/consumer.py
```

3. Acceder a la documentación de la API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### RabbitMQ

- `POST /rabbitmq/send`: Envía un mensaje a RabbitMQ
- `GET /rabbitmq/responses/{correlation_id}`: Obtiene una respuesta

## Ejemplo de Uso

```python
import requests

# Enviar mensaje
response = requests.post(
    "http://localhost:8000/rabbitmq/send",
    json={
        "message_type": "get_user",
        "payload": {"user_id": "123"}
    }
)

# Obtener correlation_id
correlation_id = response.json()["correlation_id"]

# Obtener respuesta
response = requests.get(
    f"http://localhost:8000/rabbitmq/responses/{correlation_id}"
)
```

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información. 