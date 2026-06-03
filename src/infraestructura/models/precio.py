from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Precio:
    monto: int
    valido_desde: datetime
    valido_hasta: Optional[datetime]= None
    id: Optional[int]= None

@dataclass(frozen=True)
class Detalles_precio:
    id_detalleproductofk: int
    id_preciofk: int