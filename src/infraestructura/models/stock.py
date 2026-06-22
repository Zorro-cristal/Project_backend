
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .local import Local


@dataclass(frozen=True)
class Stock:
    cant_deposito: int
    cant_mostrador: int
    precio: float
    cant_reservado: int = 0
    lote: Optional[str] = None
    id_localfk: Optional[int]= None
    id_detalleproductofk: Optional[str]= None
    local: Optional[Local]= None
    fecha_vencimiento: Optional[datetime] = None
    id: Optional[int] = None
