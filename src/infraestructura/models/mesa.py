
from dataclasses import dataclass
from typing import Optional

from .local import Local


@dataclass(frozen=True)
class Mesa:
    nombre: str
    estado: bool
    capacidad: int
    id_localfk: Optional[int]= None
    local: Optional[Local]= None
    id: Optional[int] = None