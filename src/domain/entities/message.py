from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Message:
    """Entidad base para mensajes"""

    type: str
    payload: dict[str, Any]
    response_queue: Optional[str] = None
    correlation_id: Optional[str] = None
