from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.detalle_venta_request import \
    DetalleVentaRequest
from src.shell.adapters.requests.local_request import LocalRequest
from src.shell.adapters.requests.usuario_request import UsuarioRequest


class VentaRequest(BaseModel):
    nro: Optional[str] = None
    fecha: datetime
    estado: Optional[int] = 1
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    id_usuariofk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
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
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    id_usuariofk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    usuario: Optional[UsuarioRequest] = None
    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles: Optional[List[DetalleVentaRequest]] = None

    class Config:
        validate_by_name = True

