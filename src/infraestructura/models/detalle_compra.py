from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.producto import Producto
from src.infraestructura.models.compra import Compra


@dataclass(frozen=True)
class Detalle_compra:
    cantidad: int
    precio: float
    id_comprafk: Optional[int] = None
    id_productofk: Optional[int] = None
    producto: Optional[Producto] = None
    compra: Optional[Compra] = None
    id: Optional[int] = None
