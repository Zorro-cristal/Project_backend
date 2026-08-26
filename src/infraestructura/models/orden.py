
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .mesa import Mesa
from .precio import Precio
from .usuario import Usuario


class PrintStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    IMPRESO = "IMPRESO"
    FALLO = "FALLO"


@dataclass(frozen=True)
class Orden:
    estado: int = 1
    cantidad: int = 1
    observacion: Optional[str] = None
    id_mesafk: Optional[int]= None
    id_detalleproductofk: Optional[str]= None
    id_usuariofk: Optional[int] = None
    id_preciofk: Optional[int] = None
    estado_impresion: PrintStatus = PrintStatus.PENDIENTE
    IMPRESO_at: Optional[str] = None
    last_print_error: Optional[str] = None
    mesa: Optional[Mesa]= None
    precio: Optional[Precio]= None
    usuario: Optional[Usuario]= None
    id: Optional[int] = None
