from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PagoCompraRequest(BaseModel):
    """Request para registrar un pago de compra."""
    tipo: int  # 1: Cuota, 2: Entrega
    monto: float
    fecha: Optional[datetime] = None
    id_comprafk: int
    id_cajafk: int

    class Config:
        validate_by_name = True


class PagoCompraUpdateRequest(BaseModel):
    """Request para actualizar un pago de compra."""
    tipo: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None

    class Config:
        validate_by_name = True
