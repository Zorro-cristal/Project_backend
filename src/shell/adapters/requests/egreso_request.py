from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.caja_request import CajaRequest


class EgresoRequest(BaseModel):
    monto: float
    descripcion: str
    estado: Optional[int] = 1
    fecha: datetime
    id_cajafk: Optional[int] = None
    caja: Optional[CajaRequest] = None

    class Config:
        validate_by_name = True


class EgresoUpdateRequest(BaseModel):
    monto: Optional[float] = None
    descripcion: Optional[str] = None
    estado: Optional[int] = None
    fecha: Optional[datetime] = None
    id_cajafk: Optional[int] = None
    caja: Optional[CajaRequest] = None

    class Config:
        validate_by_name = True
