from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.cliente import Cliente
from src.infraestructura.models.local import Local
from src.infraestructura.models.proveedor import Proveedor


@dataclass(frozen=True)
class Compra:
    nro: Optional[str] = None
    id_localFK: Optional[int] = None
    id_clienteFK: Optional[int] = None
    fecha: datetime = None
    estado: int = 1
    fecha_edit: Optional[datetime] = None
    id_proveedorFK: Optional[int] = None
    local: Optional[Local] = None
    cliente: Optional[Cliente] = None
    proveedor: Optional[Proveedor] = None
    id: Optional[int] = None
