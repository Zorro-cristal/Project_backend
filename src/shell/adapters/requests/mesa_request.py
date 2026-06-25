from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)


class MesaRequest(BaseModel):
    nombre: str
    capacidad: int
    estado: Optional[int] = 1
    id_localfk: int  # Required: NOT NULL in database schema
    local: Optional[LocalRequest] = None

    class Config:
        validate_by_name = True


class MesaUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    capacidad: Optional[int] = None
    estado: Optional[int] = None
    id_localfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    ocupado_desde: Optional[str] = None
    local: Optional[LocalUpdateRequest] = None

    class Config:
        validate_by_name = True
