from typing import Optional
from pydantic import BaseModel
from src.shell.adapters.requests.local_request import (
    LocalRequest,
    LocalUpdateRequest,
)


class MesaRequest(BaseModel):
    nombre: str
    estado: Optional[bool] = True
    id_localFK: Optional[int] = None
    local: Optional[LocalRequest] = None

    class Config:
        validate_by_name = True


class MesaUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[bool] = None
    id_localFK: Optional[int] = None
    local: Optional[LocalUpdateRequest] = None

    class Config:
        validate_by_name = True
