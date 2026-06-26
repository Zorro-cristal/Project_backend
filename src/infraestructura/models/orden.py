
from dataclasses import dataclass
from typing import Optional

from .mesa import Mesa


@dataclass(frozen=True)
class Orden:
    estado: str = "Pendiente"
    cantidad: int = 1
    observacion: Optional[str] = None
    id_mesafk: Optional[int]= None
    id_detalleproductofk: Optional[str]= None
    id_usuariofk: Optional[int] = None
    mesa: Optional[Mesa]= None
    id: Optional[int] = None
