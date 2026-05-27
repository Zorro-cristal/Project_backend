from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from src.shell.adapters.requests.usuario_request import UsuarioRequest
from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.local_request import LocalRequest
from src.shell.adapters.requests.detalle_venta_request import DetalleVentaRequest


class VentaRequest(BaseModel):
    nro: Optional[str] = None
    fecha: datetime
    estado: Optional[int] = 1
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
    usuario: Optional[UsuarioRequest] = None
    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles: Optional[List[DetalleVentaRequest]] = None

    class Config:
        validate_by_name = True


class VentaUpdateRequest(BaseModel):
    nro: Optional[str] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
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
    usuario: Optional[UsuarioRequest] = None
    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles: Optional[List[DetalleVentaRequest]] = None

    class Config:
        validate_by_name = True
