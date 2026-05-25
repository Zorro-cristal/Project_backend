from dataclasses import dataclass
from typing import Optional

from src.infraestructura.entidad.persona import Persona
from src.infraestructura.entidad.rol import Rol


@dataclass(frozen=True)
class Usuario:
    alias: str
    contra: str
    estado: int = 1
    Roles_id: int = None
    rol: Optional[Rol] = None
    id_personaFK: Optional[int] = None
    persona: Optional[Persona] = None
    id: Optional[int] = None