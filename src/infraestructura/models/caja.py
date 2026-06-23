
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .usuario import Usuario
from .egreso import Egreso
from .venta import Venta
from .compra import Compra


@dataclass(frozen=True)
class Caja:
    monto_apertura: float
    fecha_creacion: datetime
    monto_cierre: Optional[float]= None
    fecha_cierre: Optional[datetime] = None
    id_usuariofk: Optional[int]= None
    usuario: Optional[Usuario] = None
    egreso: Optional[Egreso] = None
    compra: Optional[Compra] = None
    venta: Optional[Venta] = None
    id: Optional[int] = None