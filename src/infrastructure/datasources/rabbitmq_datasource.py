import json
import os
import time
import uuid
from typing import Any, ClassVar, Optional

import pika
from dotenv import load_dotenv

from src.domain.entities.message import Message
from src.domain.repositories.message_repository import MessageCallback


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

        load_dotenv()
        self.url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.queue = os.getenv("RABBITMQ_QUEUE", "notifications")
        self.response_queue = f"response_queue_{uuid.uuid4()}"
        self._response_callback: Optional[MessageCallback] = None
        self._setup_connection()
        RabbitMQDatasource._initialized = True

    def _setup_connection(self) -> None:
        """Configura la conexión con RabbitMQ"""
        attempts = 0
        while attempts < self.MAX_RECONNECT_ATTEMPTS:
            try:
                self.connection = pika.BlockingConnection(pika.URLParameters(self.url))
                self.channel = self.connection.channel()
                self.channel.basic_qos(prefetch_count=1)

                # Primero intentamos obtener las propiedades de la cola existente
                try:
                    self.channel.queue_declare(queue=self.queue, passive=True)
                    print(f"Usando cola existente: {self.queue}")
                except pika.exceptions.ChannelClosedByBroker:
                    # Si la cola no existe, la creamos con las propiedades deseadas
                    self.channel.queue_declare(queue=self.queue, durable=True)
                    print(f"Cola creada: {self.queue}")

                # Declarar la cola de respuesta (siempre exclusiva)
                print(f"Configurando cola de respuesta: {self.response_queue}")
                self.channel.queue_declare(queue=self.response_queue, exclusive=True)
                print(f"Cola de respuesta configurada: {self.response_queue}")
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

    def _to_message(self, body: bytes) -> Message:
        """Convierte bytes a Message"""
        data = json.loads(body)
        return Message(
            type=data.get("type", ""),
            payload=data.get("payload", {}),
            response_queue=data.get("response_queue"),
            correlation_id=data.get("correlation_id"),
        )

    def _to_bytes(self, message: Message) -> bytes:
        """Convierte Message a bytes"""
        return json.dumps(
            {
                "type": message.type,
                "payload": message.payload,
                "response_queue": message.response_queue,
                "correlation_id": message.correlation_id,
            }
        ).encode()

    def setup_response_consumer(self, callback: MessageCallback) -> None:
        """Configura el consumidor de respuestas"""
        self._response_callback = callback
        self._ensure_connection()
        self.channel.basic_consume(queue=self.response_queue, on_message_callback=self._handle_response, auto_ack=False)

    def _handle_response(self, ch: Any, method: Any, properties: Any, body: bytes) -> None:
        """Maneja las respuestas recibidas"""
        if self._response_callback:
            try:
                message = self._to_message(body)
                self._response_callback(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                print(f"Error al procesar respuesta: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag)

    def publish(self, message: Message) -> None:
        """Publica un mensaje"""
        try:
            self._ensure_connection()
            message_dict = {
                "type": message.type,
                "payload": message.payload,
                "response_queue": message.response_queue,
                "correlation_id": message.correlation_id,
            }
            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue,
                body=json.dumps(message_dict),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
        except Exception as e:
            print(f"Error al publicar mensaje: {str(e)}")
            raise

    def publish_response(self, response: Message) -> None:
        """Publica una respuesta"""
        try:
            self._ensure_connection()
            if not response.response_queue:
                raise ValueError("response_queue es requerido para respuestas")

            self.channel.basic_publish(
                exchange="",
                routing_key=response.response_queue,
                body=self._to_bytes(response),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )
        except Exception as e:
            print(f"Error al publicar respuesta: {str(e)}")
            raise

    def consume(self, callback: MessageCallback) -> None:
        """Consume mensajes"""
        try:
            self._ensure_connection()
            self.channel.basic_consume(
                queue=self.queue,
                on_message_callback=lambda ch, method, properties, body: (
                    self._handle_consume(ch, method, properties, body, callback)
                ),
                auto_ack=False,
            )
            self.channel.start_consuming()
        except Exception as e:
            print(f"Error al iniciar consumo: {str(e)}")
            raise

    def _handle_consume(self, ch: Any, method: Any, properties: Any, body: bytes, callback: MessageCallback) -> None:
        """Maneja el consumo de mensajes"""
        try:
            message = self._to_message(body)
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error al procesar mensaje: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

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
