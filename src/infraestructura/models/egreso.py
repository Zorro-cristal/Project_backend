from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .caja import Caja

@dataclass(frozen=True)
class Egreso:
    monto: float
    descripcion: str
    estado: int = 1
    fecha: datetime = None
    id_cajafk: Optional[int] = None
    caja: Optional[Caja] = None