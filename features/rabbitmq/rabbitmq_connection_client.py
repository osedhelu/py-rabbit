"""
Módulo que implementa el cliente RabbitMQ para enviar mensajes y recibir respuestas.
"""

import logging
import time
import uuid
from typing import Optional

import pika
from pika.exceptions import AMQPChannelError, AMQPConnectionError, StreamLostError

from features.rabbitmq.conexion import RabbitMQConnection

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """
    Cliente RabbitMQ que envía mensajes y espera respuestas.
    """

    def __init__(self, rabbit_conn: RabbitMQConnection):
        """
        Inicializa el cliente RabbitMQ.

        Args:
            rabbit_conn (RabbitMQConnection): Instancia de la conexión RabbitMQ.
        """
        self.rabbit_conn = rabbit_conn
        self.channel = None
        self.connection = None
        self.callback_queue = None
        self.response = None
        self.corr_id = None
        self._setup_connection()

    def _setup_connection(self):
        """Configura la conexión inicial y la cola de callback"""
        if not self.rabbit_conn.is_connected():
            if not self.rabbit_conn.connect():
                raise ConnectionError("No se pudo establecer la conexión inicial con RabbitMQ")

        self.channel = self.rabbit_conn.channel

        # Declarar cola de callback
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        """Callback que procesa la respuesta recibida"""
        if self.corr_id == props.correlation_id:
            self.response = body

    def ensure_connection(self):
        """Asegura que la conexión esté activa, reconectando si es necesario"""
        if not self.rabbit_conn.is_connected():
            logger.warning("La conexión a RabbitMQ está cerrada. Intentando reconectar...")
            if self.rabbit_conn.reconnect():
                self._setup_connection()
                logger.info("Reconexión a RabbitMQ exitosa")
                return True
            else:
                logger.error("No se pudo reconectar a RabbitMQ")
                return False
        return True

    def call(self, routing_key: str, message: str, max_retries: int = 3) -> Optional[str]:
        """
        Envía un mensaje y espera la respuesta con reintentos.

        Args:
            routing_key (str): Clave de enrutamiento para el mensaje
            message (str): Mensaje a enviar
            max_retries (int): Número máximo de reintentos

        Returns:
            Optional[str]: Respuesta recibida o None si falla después de los reintentos

        Raises:
            ConnectionError: Si no se puede establecer la conexión después de los reintentos
        """
        retries = 0
        last_error = None

        while retries < max_retries:
            try:
                if not self.ensure_connection():
                    raise ConnectionError("No se pudo establecer conexión con RabbitMQ")

                self.response = None
                self.corr_id = str(uuid.uuid4())

                logger.info(f"Enviando mensaje (intento {retries + 1}/{max_retries})")
                self.channel.basic_publish(
                    exchange="",
                    routing_key=routing_key,
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.corr_id,
                        delivery_mode=2,  # Hacer el mensaje persistente
                    ),
                    body=message.encode(),
                )

                # Esperamos la respuesta con timeout
                timeout = 60  # 60 segundos de timeout
                start_time = time.time()

                while self.response is None:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Tiempo de espera agotado para la respuesta")

                    try:
                        self.rabbit_conn.process_data_events(time_limit=0.5)
                    except (AMQPConnectionError, AMQPChannelError, StreamLostError) as e:
                        logger.error(f"Error al procesar eventos: {str(e)}")
                        if not self.ensure_connection():
                            raise ConnectionError("No se pudo reconectar después del error") from e
                        break

                if self.response:
                    return self.response.decode()
                else:
                    retries += 1
                    logger.warning(f"No se recibió respuesta. Reintento {retries}/{max_retries}")
                    time.sleep(2)  # Espera antes de reintentar

            except (AMQPConnectionError, AMQPChannelError, StreamLostError) as e:
                retries += 1
                last_error = e
                logger.error(f"Error de conexión: {str(e)}. Reintento {retries}/{max_retries}")
                time.sleep(2)
                if not self.ensure_connection():
                    raise ConnectionError("No se pudo reconectar después del error") from e

            except TimeoutError as e:
                retries += 1
                last_error = e
                logger.error(f"Timeout esperando respuesta: {str(e)}. Reintento {retries}/{max_retries}")
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error inesperado: {str(e)}")
                raise

        if last_error:
            raise ConnectionError(
                f"No se pudo completar la operación después de {max_retries} intentos: {str(last_error)}"
            ) from last_error
        return None
