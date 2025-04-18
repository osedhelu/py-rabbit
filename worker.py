import logging

from core.config.settings import RABBITMQ_CONFIG
from features.rabbitmq.rabbitmq_manager import RabbitMQManager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
RABBITMQ_QUEUE = RABBITMQ_CONFIG["queue"]


def process_payload(payload):
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
    server.start(RABBITMQ_QUEUE, process_payload)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down...")
