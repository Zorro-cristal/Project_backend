from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.infraestructura.models.usuario import Usuario
from src.infraestructura.models.cliente import Cliente
from src.infraestructura.models.local import Local


@dataclass(frozen=True)
class Venta:
    nro: Optional[str] = None
    fecha: datetime = None
    estado: int = 1
    cod_usuarioFK_edit: Optional[bool] = None
    fecha_edit: Optional[datetime] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    id_usuarioFK: Optional[int] = None
    id_clienteFK: Optional[int] = None
    id_localFK: Optional[int] = None
    usuario: Optional[Usuario] = None
    cliente: Optional[Cliente] = None
    local: Optional[Local] = None
    id: Optional[int] = None
