from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.detalles_producto_request import (
    DetalleProductoRequest, DetalleProductoUpdateRequest)
from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)


class StockRequest(BaseModel):
    cant_deposito: int
    cant_mostrador: int
    precio: float
    cant_reservado: int
    lote: str
    id_localfk: Optional[int] = None
    id_detalleProductofk: Optional[int] = None
    local: Optional[LocalRequest] = None
    detalles_producto: Optional[DetalleProductoRequest] = None
    fecha_vencimiento: Optional[datetime] = None

    class Config:
        validate_by_name = True


class StockUpdateRequest(BaseModel):
    cant_deposito: Optional[int] = None
    cant_mostrador: Optional[int] = None
    precio: Optional[float] = None
    cant_reservado: Optional[int] = None
    lote: Optional[str] = None
    id_localfk: Optional[int] = None
    id_detalleProductofk: Optional[int] = None
    local: Optional[LocalUpdateRequest] = None
    detalles_producto: Optional[DetalleProductoUpdateRequest] = None
    fecha_vencimiento: Optional[datetime] = None

    class Config:
        validate_by_name = True
