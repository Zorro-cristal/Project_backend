from dataclasses import dataclass
from typing import Optional

from src.infraestructura.entidad.persona import Persona


@dataclass(frozen=True)
class Cliente:
    ruc: int
    razon_social: str
    estado: int = 1
    persona_fisica: int = 1
    id_personaFK: Optional[int] = None
    id: Optional[int] = None
    persona: Optional[Persona] = None