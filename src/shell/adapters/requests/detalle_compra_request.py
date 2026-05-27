from typing import Optional
from pydantic import BaseModel
from src.shell.adapters.requests.producto_request import ProductoRequest


class DetalleCompraRequest(BaseModel):
    cantidad: int
    precio: float
    id_compraFK: Optional[int] = None
    id_productoFK: Optional[int] = None
    producto: Optional[ProductoRequest] = None

    class Config:
        validate_by_name = True


class DetalleCompraUpdateRequest(BaseModel):
    cantidad: Optional[int] = None
    precio: Optional[float] = None
    id_compraFK: Optional[int] = None
    id_productoFK: Optional[int] = None
    producto: Optional[ProductoRequest] = None

    class Config:
        validate_by_name = True
