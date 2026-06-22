from dataclasses import dataclass
from typing import Optional

from .stock import Stock
from .compra import Compra


@dataclass(frozen=True)
class Detalle_compra:
    cantidad: int
    precio: float
    id_comprafk: Optional[int] = None
    id_stockfk: Optional[int] = None
    stock: Optional[Stock] = None
    compra: Optional[Compra] = None
    id: Optional[int] = None
