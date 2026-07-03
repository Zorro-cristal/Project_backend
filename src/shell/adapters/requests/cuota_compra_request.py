from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CuotaCompraUpdateRequest(BaseModel):
    """Request para actualizar una cuota de compra."""
    estado: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    descuento: Optional[float] = None
    interes: Optional[int] = None

    class Config:
        validate_by_name = True
