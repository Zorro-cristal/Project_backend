from dataclasses import dataclass
from typing import Optional

from .precio import Precio


@dataclass(frozen=True)
class detalles_producto:
    unidad_por_lote: int
    color: str
    tamanho: int
    precios: list[Precio]
    cod_barra: Optional[int] = None
    id_productofk: Optional[int] = None
