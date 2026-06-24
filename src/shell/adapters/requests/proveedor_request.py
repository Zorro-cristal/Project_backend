from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.persona_request import (PersonaRequest,
                                                         PersonaUpdateRequest)


class ProveedorRequest(BaseModel):
    razon_social: str
    ruc: int
    estado: Optional[int] = 1
    correo: Optional[str] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaRequest] = None

    class Config:
        validate_by_name = True


class ProveedorUpdateRequest(BaseModel):
    razon_social: Optional[str] = None
    ruc: Optional[int] = None
    estado: Optional[int] = None
    correo: Optional[str] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaUpdateRequest] = None

    class Config:
        validate_by_name = True
