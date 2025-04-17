import json
import os
import time
import uuid
from typing import Any, ClassVar, Optional, Protocol, TypedDict

import pika
from dotenv import load_dotenv


class RabbitMessage(TypedDict):
    """Tipo para mensajes enviados a RabbitMQ"""

    type: str
    user_id: str
    response_queue: str


class RabbitResponse(TypedDict):
    """Tipo para respuestas recibidas de RabbitMQ"""

    id: str
    name: str
    phone: str


class MessageCallback(Protocol):
    """Protocolo para callbacks de mensajes"""

    def __call__(self, ch: Any, method: Any, properties: Any, body: bytes) -> None: ...


class ResponseCallback(Protocol):
    """Protocolo para callbacks de respuestas"""

    def __call__(self, response: RabbitResponse) -> None: ...


class RabbitMQDatasource:
    _instance: ClassVar[Optional["RabbitMQDatasource"]] = None
    _initialized: bool = False
    MAX_RECONNECT_ATTEMPTS: int = 5
    RECONNECT_DELAY: int = 5  # segundos

    def __new__(cls) -> "RabbitMQDatasource":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if RabbitMQDatasource._initialized:
            return

        """Inicializa la conexión con RabbitMQ"""
        load_dotenv()
        self.url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.queue = os.getenv("RABBITMQ_QUEUE", "notifications")
        self.response_queue = f"response_queue_{uuid.uuid4()}"

        self._response_callback: Optional[ResponseCallback] = None
        self._setup_connection()
        RabbitMQDatasource._initialized = True

    def _setup_connection(self) -> None:
        """Configura la conexión con RabbitMQ"""
        attempts = 0
        while attempts < self.MAX_RECONNECT_ATTEMPTS:
            try:
                self.connection = pika.BlockingConnection(pika.URLParameters(self.url))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue)
                self.channel.queue_declare(queue=self.response_queue, exclusive=True)
                return
            except pika.exceptions.AMQPConnectionError as e:
                attempts += 1
                if attempts == self.MAX_RECONNECT_ATTEMPTS:
                    raise Exception(f"No se pudo conectar a RabbitMQ después de {attempts} intentos: {str(e)}")
                print(f"Error de conexión. Reintentando en {self.RECONNECT_DELAY} segundos...")
                time.sleep(self.RECONNECT_DELAY)

    def _ensure_connection(self) -> None:
        """Verifica y restablece la conexión si es necesario"""
        if not self.connection or self.connection.is_closed:
            print("Conexión perdida. Intentando reconectar...")
            self._setup_connection()
            if self._response_callback:
                self.setup_response_consumer(self._response_callback)

    def setup_response_consumer(self, callback: ResponseCallback) -> None:
        """Configura el consumidor de respuestas"""
        self._response_callback = callback
        self._ensure_connection()
        self.channel.basic_consume(
            queue=self.response_queue,
            on_message_callback=self._handle_response,
            auto_ack=True,
        )

    def _handle_response(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """Maneja las respuestas recibidas"""
        if self._response_callback:
            try:
                response: RabbitResponse = json.loads(body)
                self._response_callback(response)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar respuesta: {str(e)}")
            except Exception as e:
                print(f"Error al procesar respuesta: {str(e)}")

    def publish(self, message: RabbitMessage) -> None:
        """Publica un mensaje en la cola principal"""
        try:
            self._ensure_connection()
            self.channel.basic_publish(exchange="", routing_key=self.queue, body=json.dumps(message))
        except Exception as e:
            print(f"Error al publicar mensaje: {str(e)}")
            raise

    def publish_response(self, response_queue: str, message: RabbitResponse) -> None:
        """Publica una respuesta en la cola específica"""
        try:
            self._ensure_connection()
            self.channel.basic_publish(exchange="", routing_key=response_queue, body=json.dumps(message))
        except Exception as e:
            print(f"Error al publicar respuesta: {str(e)}")
            raise

    def start_consuming(self, callback: MessageCallback) -> None:
        """Inicia el consumo de mensajes hola mundo"""
        try:
            self._ensure_connection()
            self.channel.basic_consume(queue=self.queue, on_message_callback=callback, auto_ack=True)
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error al iniciar consumo: {str(e)}")
            raise

    def close(self) -> None:
        """Cierra la conexión"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            RabbitMQDatasource._initialized = False
            RabbitMQDatasource._instance = None
        except Exception as e:
            print(f"Error al cerrar conexión: {str(e)}")
            raise
