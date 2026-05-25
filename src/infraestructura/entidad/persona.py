from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Persona:
    cedula: int
    nombres: str
    apellidos: str
    estado: int = 1
    telefono: Optional[int] = None
    direccion: Optional[str] = None
    nacionalidad: Optional[str] = None