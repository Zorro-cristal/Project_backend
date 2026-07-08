from dataclasses import dataclass
from datetime import datetime, time
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
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    velocidad_viento: Optional[float] = None
    lluvia: Optional[float] = None
    precipitaciones: Optional[float] = None
    probabilidad_precipitaciones: Optional[float] = None
    evento_festivo: Optional[bool] = None
    ocupacion: Optional[time] = None
    tipo_credito: Optional[int] = None
    total_cuotas: Optional[int] = None
    monto_entrega: Optional[float] = 0
    cod_num: Optional[str] = None
    id_vendedorfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    cliente: Optional[Cliente] = None
    local: Optional[Local] = None
    caja: Optional[Caja] = None
    subtotal: Optional[float] = None
    id: Optional[int] = None
