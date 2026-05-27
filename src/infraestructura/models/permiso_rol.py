from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PermisoRol:
    crear: bool
    editar: bool
    eliminar: bool
    leer: bool
    id_permisoFK: int
    id_rolFK: int
    id: Optional[int] = None
