import json
import logging
import os

import pika
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RabbitMQServer:
    def __init__(self, channel: pika.adapters.blocking_connection.BlockingChannel):
        self.channel = channel

    def start(self, queue, process_payload):
        self.channel.queue_declare(queue=queue)
        try:

            def callback(ch, method, props, body):
                try:
                    # Procesar el mensaje
                    payload = json.loads(body)
                    result = process_payload(payload)
                    response = json.dumps(result)

                    # Verificar que props.reply_to existe
                    if props.reply_to:
                        ch.basic_publish(
                            exchange="",
                            routing_key=props.reply_to,
                            properties=pika.BasicProperties(correlation_id=props.correlation_id),
                            body=response.encode(),
                        )

                    # Confirmar el mensaje
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                    logger.info(f"Processed message: {payload}")

                except Exception as e:
                    logger.error(f"Error in callback: {str(e)}")
                    # En caso de error, también confirmamos el mensaje para no bloquearlo
                    ch.basic_ack(delivery_tag=method.delivery_tag)

            # Configurar el consumo de mensajes
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

            logger.info(f" [*] Waiting for messages in queue '{RABBITMQ_QUEUE}'. To exit press CTRL+C")
            self.channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
