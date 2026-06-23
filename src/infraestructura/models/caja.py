
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from .usuario import Usuario

if TYPE_CHECKING:
    from .compra import Compra
    from .egreso import Egreso
    from .venta import Venta


@dataclass(frozen=True)
class Caja:
    monto_apertura: float
    fecha_creado: datetime
    monto_cierre: Optional[float]= None
    fecha_cierre: Optional[datetime] = None
    id_usuariofk: Optional[int]= None
    usuario: Optional[Usuario] = None
    egreso: Optional["Egreso"] = None
    compra: Optional["Compra"] = None
    venta: Optional["Venta"] = None
    id: Optional[int] = None
