from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.cliente import Cliente
from src.infraestructura.models.local import Local
from src.infraestructura.models.usuario import Usuario


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
    id_usuariofk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    usuario: Optional[Usuario] = None
    cliente: Optional[Cliente] = None
    local: Optional[Local] = None
    id: Optional[int] = None
