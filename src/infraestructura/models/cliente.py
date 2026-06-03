from dataclasses import dataclass
from typing import Optional

from .persona import Persona


@dataclass(frozen=True)
class Cliente:
    persona_fisica: int = 1
    ruc: Optional[int] = None
    razon_social: Optional[str] = None
    id_personafk: Optional[int] = None
    id: Optional[int] = None
    persona: Optional[Persona] = None