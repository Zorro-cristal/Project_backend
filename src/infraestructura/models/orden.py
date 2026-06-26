
from dataclasses import dataclass
from typing import Optional

from .mesa import Mesa
from .precio import Precio
from .usuario import Usuario

@dataclass(frozen=True)
class Orden:
    estado: int = 1
    cantidad: int = 1
    observacion: Optional[str] = None
    id_mesafk: Optional[int]= None
    id_detalleproductofk: Optional[str]= None
    id_usuariofk: Optional[int] = None
    id_preciofk: Optional[int] = None
    mesa: Optional[Mesa]= None
    precio: Optional[Precio]= None
    usuario: Optional[Usuario]= None
    id: Optional[int] = None
