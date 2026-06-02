from typing import Optional
from pydantic import BaseModel
from src.shell.adapters.requests.persona_request import (
    PersonaRequest,
    PersonaUpdateRequest,
)

class ClienteRequest(BaseModel):
    persona_fisica: Optional[int] = 1
    ruc: Optional[int] = None
    razon_social: Optional[str] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaRequest] = None

    class Config:
        validate_by_name = True


class ClienteUpdateRequest(BaseModel):
    ruc: Optional[int] = None
    razon_social: Optional[str] = None
    persona_fisica: Optional[int] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaUpdateRequest] = None

    class Config:
        validate_by_name = True
