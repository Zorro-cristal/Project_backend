from dataclasses import dataclass
from typing import Optional
from src.infraestructura.models.precio import Precio

@dataclass(frozen=True)
class Detalle_producto:
    unidad_por_lote: int
    color: str
    tamanho: int
    precios: list[Precio]
    cod_barra: Optional[int]= None