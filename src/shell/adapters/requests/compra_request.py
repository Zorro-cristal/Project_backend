from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.detalle_compra_request import \
    DetalleCompraRequest
from src.shell.adapters.requests.local_request import LocalRequest
from src.shell.adapters.requests.proveedor_request import ProveedorRequest
from src.shell.adapters.requests.usuario_request import UsuarioRequest


class CompraRequest(BaseModel):
    nro: Optional[str] = None
    id_localfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_usuariofk: Optional[int] = None
    fecha: datetime
    estado: Optional[int] = 1
    id_proveedorfk: Optional[int] = None
    local: Optional[LocalRequest] = None
    cliente: Optional[ClienteRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    usuario: Optional[UsuarioRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True


class CompraUpdateRequest(BaseModel):
    nro: Optional[str] = None
    id_localfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_usuariofk: Optional[int] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
    id_proveedorfk: Optional[int] = None
    local: Optional[LocalRequest] = None
    cliente: Optional[ClienteRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    usuario: Optional[UsuarioRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True

