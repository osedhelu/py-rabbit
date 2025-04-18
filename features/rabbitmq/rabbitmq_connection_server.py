import json

import pika

from core.utils.logging import get_logger

logger = get_logger(__name__)


class RabbitMQServer:
    def __init__(self, channel: pika.adapters.blocking_connection.BlockingChannel):
        self.channel = channel

    def create_server(self, queue, process_payload) -> None:
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
            self.channel.basic_consume(queue=queue, on_message_callback=callback)

            logger.info(f" [*] Waiting for messages in queue '{queue}'. To exit press CTRL+C")

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Error connecting to RabbitMQ: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")

    def start(self) -> None:
        try:
            logger.info("Starting RabbitMQ server")
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
