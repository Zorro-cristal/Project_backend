from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.producto import Producto
from src.infraestructura.models.venta import Venta


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
