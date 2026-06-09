from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.usuario import Usuario

from .cliente import Cliente
from .local import Local
from .proveedor import Proveedor


@dataclass(frozen=True)
class Compra:
    nro: Optional[str] = None
    id_localfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_usuariofk: Optional[int] = None
    fecha: datetime = None
    estado: int = 1
    id_proveedorfk: Optional[int] = None
    local: Optional[Local] = None
    cliente: Optional[Cliente] = None
    proveedor: Optional[Proveedor] = None
    usuario: Optional[Usuario]= None
    id: Optional[int] = None
