
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.usuario import Usuario


@dataclass(frozen=True)
class Caja:
    monto_apertura: float
    fecha_creacion: datetime
    monto_cierre: Optional[float]= None
    fecha_cierre: Optional[datetime] = None
    id_usuariofk: Optional[int]= None
    usuario: Optional[Usuario] = None
    id: Optional[int] = None