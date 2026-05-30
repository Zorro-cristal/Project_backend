from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PermisoRol:
    crear: bool
    editar: bool
    eliminar: bool
    leer: bool
    id_permisofk: int
    id_rolfk: int
    id: Optional[int] = None
