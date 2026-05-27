
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.persona import Persona


@dataclass(frozen=True)
class Proveedor:
    razon_social: str
    ruc: int
    estado: bool
    correo: Optional[str] = None
    id_personaFK: Optional[int] = None
    persona: Optional[Persona] = None
    fecha_edit: Optional[datetime] = None
    id: Optional[int] = None