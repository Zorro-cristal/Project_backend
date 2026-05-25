from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Usuario:
    cedula: int
    nombres: int
    apellidos: str
    estado: int = 1
    telefono: Optional[int]
    direccion: Optional[str]
    nacionalidad: Optional[str]