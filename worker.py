"""
Worker que procesa mensajes de RabbitMQ para operaciones de multiplicación y suma.
Implementa dos workers independientes que consumen de colas diferentes.
"""

import signal
import sys
from typing import Any, Dict

from core.config.settings import RABBITMQ_CONFIG
from core.utils.logging import get_logger
from features.rabbitmq.rabbit_di import ContainerRabbitMQ

# Configurar logging
logger = get_logger(__name__)

# Configuración de colas
QUEUE_MULTIPLY = f"{RABBITMQ_CONFIG['queue']}_mul"
QUEUE_SUM = f"{RABBITMQ_CONFIG['queue']}_sum"


def process_multiply(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa un mensaje para realizar una multiplicación.

    Args:
        payload (Dict[str, Any]): Payload con los números a multiplicar

    Returns:
        Dict[str, Any]: Resultado de la multiplicación o error
    """
    try:
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        result = a * b
        logger.info(f"Multiplicación realizada: {a} * {b} = {result}")
        return {"result": result, "operation": "multiply"}
    except Exception as e:
        logger.error(f"Error en multiplicación: {str(e)}")
        return {"error": str(e), "operation": "multiply"}


def process_sum(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Procesa un mensaje para realizar una suma.

    Args:
        payload (Dict[str, Any]): Payload con los números a sumar

    Returns:
        Dict[str, Any]: Resultado de la suma o error
    """
    try:
        a = payload.get("a", 0)
        b = payload.get("b", 0)
        result = a + b
        logger.info(f"Suma realizada: {a} + {b} = {result}")
        return {"result": result, "operation": "sum"}
    except Exception as e:
        logger.error(f"Error en suma: {str(e)}")
        return {"error": str(e), "operation": "sum"}


class Worker:
    """
    Clase que maneja los workers de RabbitMQ.
    Implementa manejo de señales para shutdown graceful.
    """

    def __init__(self):
        """Inicializa el worker con la conexión a RabbitMQ."""
        self.rabbit_conn = ContainerRabbitMQ()
        self.server = self.rabbit_conn.conexionServer()
        self._running = True

    def setup(self):
        """Configura los servidores para las colas de multiplicación y suma."""
        try:
            # Configurar servidor de multiplicación
            self.server.create_server(QUEUE_MULTIPLY, process_multiply)
            self.server.create_server(QUEUE_SUM, process_sum)
            logger.info("Workers configurados correctamente")
        except Exception as e:
            logger.error(f"Error al configurar workers: {str(e)}")
            raise

    def start(self):
        """Inicia los workers en modo asíncrono."""
        try:
            logger.info("Iniciando workers...")
            self.server.start()
        except Exception as e:
            logger.error(f"Error al iniciar workers: {str(e)}")
            raise

    def stop(self):
        """Detiene los workers de forma segura."""
        logger.info("Deteniendo workers...")
        self.rabbit_conn.close()
        logger.info("Workers detenidos correctamente")


def handle_shutdown(signum, frame):
    """Manejador de señales para shutdown graceful."""
    logger.info("Recibida señal de terminación")
    worker.stop()
    sys.exit(0)


if __name__ == "__main__":
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        worker = Worker()
        worker.setup()
        worker.start()
    except Exception as e:
        logger.error(f"Error en worker: {str(e)}")
        sys.exit(1)
