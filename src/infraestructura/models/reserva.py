from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.cliente import Cliente


@dataclass(frozen=True)
class Reserva:
    fecha_reserva: str
    cantidad_personas: int
    observacion: str = ""
    estado: str = "Activo"
    id_clientefk: Optional[int] = None
    cliente: Optional[Cliente] = None
    id: Optional[int] = None