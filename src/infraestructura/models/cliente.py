from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.persona import Persona


@dataclass(frozen=True)
class Cliente:
    estado: int = 1
    persona_fisica: int = 1
    ruc: Optional[int] = None
    razon_social: Optional[str] = None
    id_personaFK: Optional[int] = None
    id: Optional[int] = None
    persona: Optional[Persona] = None