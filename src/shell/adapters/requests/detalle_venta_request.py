from typing import Optional
from pydantic import BaseModel
from src.shell.adapters.requests.producto_request import ProductoRequest


class DetalleVentaRequest(BaseModel):
    cantidad: int
    precio: float
    descuento: Optional[float] = None
    id_productofk: Optional[int] = None
    id_ventafk: Optional[int] = None
    producto: Optional[ProductoRequest] = None

    class Config:
        validate_by_name = True


class DetalleVentaUpdateRequest(BaseModel):
    cantidad: Optional[int] = None
    precio: Optional[float] = None
    descuento: Optional[float] = None
    id_productofk: Optional[int] = None
    id_ventafk: Optional[int] = None
    producto: Optional[ProductoRequest] = None

    class Config:
        validate_by_name = True
