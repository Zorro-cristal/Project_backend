from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Permiso:
    nombre: str
    fecha_edit: Optional[datetime] = None
    id: Optional[int] = None