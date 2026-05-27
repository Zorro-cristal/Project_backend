from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from src.shell.adapters.requests.local_request import (
    LocalRequest,
    LocalUpdateRequest,
)
from src.shell.adapters.requests.detalle_producto_request import (
    DetalleProductoRequest,
    DetalleProductoUpdateRequest,
)


class StockRequest(BaseModel):
    cant_deposito: int
    cant_mostrador: int
    precio: float
    cant_reservado: int
    lote: str
    id_localFK: Optional[int] = None
    id_detalleProductoFK: Optional[int] = None
    local: Optional[LocalRequest] = None
    detalle_producto: Optional[DetalleProductoRequest] = None
    fecha_vencimiento: Optional[datetime] = None

    class Config:
        validate_by_name = True


class StockUpdateRequest(BaseModel):
    cant_deposito: Optional[int] = None
    cant_mostrador: Optional[int] = None
    precio: Optional[float] = None
    cant_reservado: Optional[int] = None
    lote: Optional[str] = None
    id_localFK: Optional[int] = None
    id_detalleProductoFK: Optional[int] = None
    local: Optional[LocalUpdateRequest] = None
    detalle_producto: Optional[DetalleProductoUpdateRequest] = None
    fecha_vencimiento: Optional[datetime] = None

    class Config:
        validate_by_name = True
