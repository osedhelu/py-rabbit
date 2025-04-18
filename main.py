"""
API principal que expone endpoints para operaciones de multiplicación y suma.
Utiliza RabbitMQ para procesar las operaciones de forma asíncrona.
"""

import json
import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.config.settings import RABBITMQ_CONFIG
from core.utils.logging import setup_logging
from features.rabbitmq.rabbit_di import ContainerRabbitMQ

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Configuración de colas
QUEUE_MULTIPLY = f"{RABBITMQ_CONFIG['queue']}_mul"
QUEUE_SUM = f"{RABBITMQ_CONFIG['queue']}_sum"

# Inicializar FastAPI
app = FastAPI(
    title="RabbitMQ Operations API", description="API para operaciones matemáticas usando RabbitMQ", version="1.0.0"
)

# Inicializar conexión RabbitMQ
rabbit_manager = ContainerRabbitMQ()


class OperationRequest(BaseModel):
    """Modelo para las peticiones de operaciones."""

    a: float
    b: float


class OperationResponse(BaseModel):
    """Modelo para las respuestas de operaciones."""

    result: float
    operation: str


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación."""
    try:
        if not rabbit_manager.connection.is_connected():
            if not rabbit_manager.connection.connect():
                raise HTTPException(status_code=500, detail="No se pudo establecer conexión con RabbitMQ")
        logger.info("API iniciada correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar la API: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación."""
    try:
        rabbit_manager.close()
        logger.info("API detenida correctamente")
    except Exception as e:
        logger.error(f"Error al detener la API: {str(e)}")


@app.post("/multiply/", response_model=OperationResponse)
async def multiply(request: OperationRequest) -> dict[str, Any]:
    """
    Endpoint para realizar multiplicaciones.

    Args:
        request (OperationRequest): Petición con los números a multiplicar

    Returns:
        dict[str, Any]: Resultado de la multiplicación

    Raises:
        HTTPException: Si hay error en la operación
    """
    try:
        payload = {"a": request.a, "b": request.b}
        response = rabbit_manager.conexionClient().call(QUEUE_MULTIPLY, json.dumps(payload), max_retries=5)

        if not response:
            raise HTTPException(status_code=500, detail="No se recibió respuesta del worker")

        result = json.loads(response)
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Error en la multiplicación: {result['error']}")

        return {"result": result["result"], "operation": "multiply"}
    except ConnectionError as e:
        logger.error(f"Error de conexión en multiplicación: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error de conexión con RabbitMQ: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error inesperado en multiplicación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la operación: {str(e)}") from e


@app.post("/sum/", response_model=OperationResponse)
async def sum(request: OperationRequest) -> dict[str, Any]:
    """
    Endpoint para realizar sumas.

    Args:
        request (OperationRequest): Petición con los números a sumar

    Returns:
        dict[str, Any]: Resultado de la suma

    Raises:
        HTTPException: Si hay error en la operación
    """
    try:
        payload = {"a": request.a, "b": request.b}
        response = rabbit_manager.conexionClient().call(QUEUE_SUM, json.dumps(payload), max_retries=5)

        if not response:
            raise HTTPException(status_code=500, detail="No se recibió respuesta del worker")

        result = json.loads(response)
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Error en la suma: {result['error']}")

        return {"result": result["result"], "operation": "sum"}
    except ConnectionError as e:
        logger.error(f"Error de conexión en suma: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Error de conexión con RabbitMQ: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error inesperado en suma: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en la operación: {str(e)}") from e
