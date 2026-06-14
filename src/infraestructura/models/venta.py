from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .caja import Caja
from .cliente import Cliente
from .local import Local
from .usuario import Usuario


@dataclass(frozen=True)
class Venta:
    nro: Optional[str] = None
    fecha: datetime = None
    estado: int = 1
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    cliente: Optional[Cliente] = None
    local: Optional[Local] = None
    caja: Optional[Caja] = None
    id: Optional[int] = None
