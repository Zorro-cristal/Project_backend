from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Permiso:
    nombre: str
    crear: bool
    editar: bool
    eliminar: bool
    leer: bool
    id_rolFK: int
    id: Optional[int] = None