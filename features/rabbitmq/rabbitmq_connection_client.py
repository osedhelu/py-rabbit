import logging
import time
import uuid

import pika
from dotenv import load_dotenv
from pika.exceptions import AMQPChannelError, AMQPConnectionError, StreamLostError

from features.rabbitmq.conexion import RabbitMQConnection

load_dotenv()


logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self, rabbit_conn: RabbitMQConnection):
        self.rabbit_conn = rabbit_conn
        self.channel = rabbit_conn.channel
        self.connection = rabbit_conn.connection

        # Declarar cola de callback
        result = self.channel.queue_declare(queue="", exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def ensure_connection(self):
        """Asegura que la conexión esté activa, reconectando si es necesario"""
        if not self.connection or not self.connection.is_open:
            logger.warning("La conexión a RabbitMQ está cerrada. Intentando reconectar...")
            if self.rabbit_conn.reconnect():
                self.connection = self.connection
                self.channel = self.channel

                # Re-declarar cola de callback
                result = self.channel.queue_declare(queue="", exclusive=True)
                self.callback_queue = result.method.queue
                self.channel.basic_consume(
                    queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True
                )
                logger.info("Reconexión a RabbitMQ exitosa")
                return True
            else:
                logger.error("No se pudo reconectar a RabbitMQ")
                return False
        return True

    def call(self, routing_key, message, max_retries=3):
        """Envía un mensaje con patrón RPC y maneja reconexiones automáticas"""
        retries = 0

        while retries < max_retries:
            try:
                if not self.ensure_connection():
                    raise ConnectionError("No se pudo establecer conexión con RabbitMQ")

                self.response = None
                self.corr_id = str(uuid.uuid4())

                self.channel.basic_publish(
                    exchange="",
                    routing_key=routing_key,
                    properties=pika.BasicProperties(
                        reply_to=self.callback_queue,
                        correlation_id=self.corr_id,
                    ),
                    body=message.encode(),
                )

                # Esperamos la respuesta con timeout
                timeout = 30  # 30 segundos de timeout
                start_time = time.time()

                while self.response is None:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Tiempo de espera agotado para la respuesta")

                    try:
                        self.connection.process_data_events(time_limit=1.0)
                    except Exception as e:
                        logger.error(f"Error al procesar eventos: {str(e)}")
                        break

                if self.response:
                    return self.response.decode()
                else:
                    retries += 1
                    logger.warning(f"No se recibió respuesta. Reintento {retries}/{max_retries}")
                    time.sleep(2)  # Espera antes de reintentar

            except (AMQPConnectionError, AMQPChannelError, StreamLostError, ConnectionError) as e:
                retries += 1
                logger.error(f"Error de conexión: {str(e)}. Reintento {retries}/{max_retries}")
                # Esperamos antes de intentar reconectar
                time.sleep(2)
                self.ensure_connection()

            except Exception as e:
                logger.error(f"Error inesperado: {str(e)}")
                raise

        raise ConnectionError(f"No se pudo completar la operación después de {max_retries} intentos")
