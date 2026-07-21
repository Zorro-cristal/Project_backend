from dataclasses import dataclass
from datetime import time
from typing import Optional

from src.infraestructura.models.cliente import Cliente


@dataclass(frozen=True)
class Reserva:
    fecha_reserva: str
    cantidad_personas: int
    observacion: str = ""
    estado: int = 1
    tiempo_estimado: Optional[time] = None
    tiempo_ocupacion: Optional[time] = None
    id_clientefk: Optional[int] = None
    cliente: Optional[Cliente] = None
    id: Optional[int] = None