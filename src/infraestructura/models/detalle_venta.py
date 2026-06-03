from dataclasses import dataclass
from typing import Optional

from .producto import Producto
from .venta import Venta


@dataclass(frozen=True)
class Detalle_venta:
    cantidad: int
    precio: float
    descuento: Optional[float] = None
    id_productofk: Optional[int] = None
    id_ventafk: Optional[int] = None
    producto: Optional[Producto] = None
    venta: Optional[Venta] = None
    id: Optional[int] = None
