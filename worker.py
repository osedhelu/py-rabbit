import logging

from core.config.settings import RABBITMQ_CONFIG
from features.rabbitmq.rabbitmq_manager import RabbitMQManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
RABBITMQ_QUEUE = RABBITMQ_CONFIG["queue"]


def process_payloadmul(payload):
    try:
        # Ejemplo: suma dos números
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        return {"mult": a * b}
    except Exception as e:
        logger.error(f"Error processing payload: {str(e)}")
        return {"error": str(e)}


def process_payloadsum(payload):
    try:
        # Ejemplo: suma dos números
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        return {"sum": a + b}
    except Exception as e:
        logger.error(f"Error processing payload: {str(e)}")
        return {"error": str(e)}


def main():
    server = RabbitMQManager().conexionServer()
    server.create_server(f"{RABBITMQ_QUEUE}_mul", process_payloadmul)
    server.create_server(f"{RABBITMQ_QUEUE}_sum", process_payloadsum)
    server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
