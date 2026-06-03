
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.local import Local


@dataclass(frozen=True)
class Stock:
    cant_deposito: int
    cant_mostrador: int
    precio: float
    cant_reservado: int
    lote: str
    id_localfk: Optional[int]= None
    id_detalleproductofk: Optional[str]= None
    local: Optional[Local]= None
    fecha_vencimiento: Optional[datetime] = None
    id: Optional[int] = None