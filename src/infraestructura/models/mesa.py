
from dataclasses import dataclass
from typing import Optional

from .cliente import Cliente
from .local import Local


@dataclass(frozen=True)
class Mesa:
    nombre: str
    estado: int
    capacidad: int
    id_localfk: Optional[int] = None
    local: Optional[Local] = None
    id_clientefk: Optional[int] = None
    cliente: Optional[Cliente] = None
    id: Optional[int] = None
