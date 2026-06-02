from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Ingrediente:
    # Para POST /ingrediente, el ID suele generarse en BD (serial/identity),
    # por eso no debe ser obligatorio en el payload.
    id: Optional[int] = None
    cantidad: int = 0
    unidad_medida: str = ""
    id_producto_ingredientefk: int = 0
    id_producto_finalfk: int = 0
