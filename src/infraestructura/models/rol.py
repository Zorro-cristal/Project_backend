from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Rol:
    nombre: str
    observacion: str
    estado: int
    fecha_create: Optional[datetime] = None
    id_rol: Optional[int] = None
    