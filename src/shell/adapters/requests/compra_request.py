from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.shell.adapters.requests.caja_request import CajaRequest
from src.shell.adapters.requests.detalle_compra_request import \
    DetalleCompraRequest
from src.shell.adapters.requests.local_request import LocalRequest
from src.shell.adapters.requests.proveedor_request import ProveedorRequest


class CompraRequest(BaseModel):
    nro: Optional[str] = None
    id_localfk: int = None
    id_cajafk: Optional[int] = None
    fecha: datetime
    estado: Optional[int] = 1
    tipo_credito: Optional[int] = 1
    id_proveedorfk: Optional[int] = None
    local: Optional[LocalRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    caja: Optional[CajaRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True


class CompraUpdateRequest(BaseModel):
    nro: Optional[str] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
    tipo_credito: Optional[int] = None
    id_proveedorfk: Optional[int] = None
    local: Optional[LocalRequest] = None
    proveedor: Optional[ProveedorRequest] = None
    caja: Optional[CajaRequest] = None
    detalles: Optional[List[DetalleCompraRequest]] = None

    class Config:
        validate_by_name = True

