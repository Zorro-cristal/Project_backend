from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Rol:
    nombre: str
    observacion: str
    estado: int
    fecha_creacion: datetime
    