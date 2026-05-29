from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Rol:
    nombre: str
    observacion: str
    estado: int
    fecha_creado: Optional[datetime] = None
    id: Optional[int] = None
    