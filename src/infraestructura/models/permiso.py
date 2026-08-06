from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Permiso:
    nombre: str
    estado: int
    id: Optional[int] = None