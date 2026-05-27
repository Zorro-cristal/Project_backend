from typing import Optional
from pydantic import BaseModel
from src.shell.adapters.requests.usuario_request import (
    UsuarioRequest,
    UsuarioUpdateRequest,
)
from datetime import datetime


class CajaRequest(BaseModel):
    monto_apertura: float
    fecha_creacion: datetime
    monto_cierre: Optional[float] = None
    fecha_cierre: Optional[datetime] = None
    id_usuarioFK: Optional[int] = None
    usuario: Optional[UsuarioRequest] = None

    class Config:
        validate_by_name = True


class CajaUpdateRequest(BaseModel):
    monto_apertura: Optional[float] = None
    fecha_creacion: Optional[datetime] = None
    monto_cierre: Optional[float] = None
    fecha_cierre: Optional[datetime] = None
    id_usuarioFK: Optional[int] = None
    usuario: Optional[UsuarioUpdateRequest] = None

    class Config:
        validate_by_name = True
