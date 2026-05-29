from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.persona import Persona
from src.infraestructura.models.rol import Rol


@dataclass(frozen=True)
class Usuario:
    alias: str
    contra: str
    estado: int = 1
    id: int = None

    # FK requerida por la tabla `usuarios` (NOT NULL)
    id_rolfk: Optional[int] = None

    # Mantener rol como referencia opcional (no se usará para insertar si no se convierte a FK)
    rol: Optional[Rol] = None

    # Nombre de columna alineado con tu esquema (Supabase)
    id_personafk: Optional[int] = None
    persona: Optional[Persona] = None
    id: Optional[int] = None


