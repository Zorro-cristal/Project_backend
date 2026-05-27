from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.local_request import LocalRequest
from src.shell.adapters.requests.proveedor_request import ProveedorRequest
from src.shell.adapters.requests.detalle_compra_request import DetalleCompraRequest


class CompraRequest(BaseModel):
    nro: Optional[str] = None
    id_localFK: Optional[int] = None
    id_clienteFK: Optional[int] = None
    fecha: datetime
    estado: Optional[int] = 1
    fecha_edit: Optional[datetime] = None
    id_proveedorFK: Optional[int] = None
    local: Optional[LocalRequest] = None
    cliente: Optional[ClienteRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True


class CompraUpdateRequest(BaseModel):
    nro: Optional[str] = None
    id_localFK: Optional[int] = None
    id_clienteFK: Optional[int] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
    fecha_edit: Optional[datetime] = None
    id_proveedorFK: Optional[int] = None
    local: Optional[LocalRequest] = None
    cliente: Optional[ClienteRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True
