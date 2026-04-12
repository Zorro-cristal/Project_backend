from dataclasses import dataclass
from src.infraestructura.entidad.precio import Precio

@dataclass(frozen=True)
class Detalle_producto:
    cod_barra: int
    unidad_por_lote: int
    color: str
    tamanho: int
    precios: Precio[]