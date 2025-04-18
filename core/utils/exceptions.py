class RabbitMQError(Exception):
    """Excepción base para errores de RabbitMQ"""

    pass


class ConnectionError(RabbitMQError):
    """Error de conexión con RabbitMQ"""

    pass


class MessageError(RabbitMQError):
    """Error al procesar un mensaje"""

    pass


class ResponseError(RabbitMQError):
    """Error al procesar una respuesta"""

    pass


class QueueError(RabbitMQError):
    """Error al manejar una cola"""

    pass
