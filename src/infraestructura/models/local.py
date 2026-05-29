
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Local:
    nombre: str
    estado: bool
    direccion: Optional[str] = None
    telefono: Optional[str] = None

    id: Optional[int] = None