from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.usuario import Usuario

from .caja import Caja
from .local import Local
from .proveedor import Proveedor


@dataclass
class Compra:
    nro: Optional[str] = None
    id_localfk: int = None
    id_cajafk: Optional[int] = None
    fecha: datetime = None
    estado: int = 1
    tipo_credito: int = 1
    total_cuotas: Optional[int] = None
    # monto_entrega: adelanto pagado al momento de la compra (reduce la deuda que se reparte en cuotas)
    monto_entrega: Optional[float] = 0
    id_proveedorfk: Optional[int] = None
    local: Optional[Local] = None
    proveedor: Optional[Proveedor] = None
    caja: Optional[Caja]= None
    id: Optional[int] = None
