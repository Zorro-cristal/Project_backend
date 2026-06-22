from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.stock_request import StockRequest


class DetalleCompraRequest(BaseModel):
    cantidad: int
    precio: float
    id_comprafk: Optional[int] = None
    id_stockfk: Optional[int] = None
    stock: Optional[StockRequest] = None

    class Config:
        validate_by_name = True


class DetalleCompraUpdateRequest(BaseModel):
    cantidad: Optional[int] = None
    precio: Optional[float] = None
    id_comprafk: Optional[int] = None
    id_stockfk: Optional[int] = None
    stock: Optional[StockRequest] = None

    class Config:
        validate_by_name = True
