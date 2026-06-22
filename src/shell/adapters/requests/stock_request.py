from datetime import datetime
from typing import Optional

from pydantic import AliasChoices, BaseModel, Field

from src.shell.adapters.requests.detalles_producto_request import (
    DetalleProductoRequest, DetalleProductoUpdateRequest)
from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)


class StockRequest(BaseModel):
    model_config = {'validate_by_name': True}
    
    cant_deposito: int
    cant_mostrador: int
    precio: float
    cant_reservado: int = Field(default=0, validation_alias=AliasChoices('cant_reservado', 'cant_reservada'))
    lote: str = ''
    id_localfk: Optional[int] = None
    id_detalleproductofk: Optional[str] = None
    local: Optional[LocalRequest] = None
    detalles_producto: Optional[DetalleProductoRequest] = None
    fecha_vencimiento: Optional[datetime] = None


class StockUpdateRequest(BaseModel):
    model_config = {'validate_by_name': True}
    
    cant_deposito: Optional[int] = None
    cant_mostrador: Optional[int] = None
    precio: Optional[float] = None
    cant_reservado: Optional[int] = Field(default=None, validation_alias=AliasChoices('cant_reservado', 'cant_reservada'))
    lote: Optional[str] = None
    id_localfk: Optional[int] = None
    id_detalleproductofk: Optional[str] = None
    local: Optional[LocalUpdateRequest] = None
    detalles_producto: Optional[DetalleProductoUpdateRequest] = None
    fecha_vencimiento: Optional[datetime] = None
