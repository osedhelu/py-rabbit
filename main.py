import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from features.rabbitmq.rabbitmq_manager import RabbitMQManager

load_dotenv()

FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
FASTAPI_DEBUG = os.getenv("FASTAPI_DEBUG", "True") == "True"
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE")
app = FastAPI()
rabbitmq = RabbitMQManager().conexionClient()


@app.post("/process/")
def process(payload: dict):
    message = json.dumps(payload)
    response = rabbitmq.call(RABBITMQ_QUEUE, message)
    return {"result": response}
