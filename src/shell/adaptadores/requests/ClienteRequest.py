from typing import Optional
from pydantic import BaseModel
from src.shell.adaptadores.requests.PersonaRequest import (
    PersonaRequest,
    PersonaUpdateRequest,
)

class ClienteRequest(BaseModel):
    ruc: int
    razon_social: str
    estado: Optional[int] = 1
    persona_fisica: Optional[int] = 1
    id_personaFK: Optional[int] = None
    persona: Optional[PersonaRequest] = None

    class Config:
        validate_by_name = True


class ClienteUpdateRequest(BaseModel):
    ruc: Optional[int] = None
    razon_social: Optional[str] = None
    estado: Optional[int] = None
    persona_fisica: Optional[int] = None
    id_personaFK: Optional[int] = None
    persona: Optional[PersonaUpdateRequest] = None

    class Config:
        validate_by_name = True
