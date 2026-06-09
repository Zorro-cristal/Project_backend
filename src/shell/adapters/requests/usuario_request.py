from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.persona_request import (PersonaRequest,
                                                         PersonaUpdateRequest)


class UsuarioRequest(BaseModel):
    alias: str
    contra: str
    estado: Optional[int] = 1
    id_rolfk: Optional[int] = None
    id_personafk: Optional[int] = None  # FK directa a persona existente
    persona: Optional[PersonaRequest] = None  # Objeto persona (se crea o actualiza si no existe)

    class Config:
        validate_by_name = True

class UsuarioUpdateRequest(BaseModel):
    alias: Optional[str] = None
    contra: Optional[str] = None
    estado: Optional[int] = None
    id_rolfk: Optional[int] = None
    id_personafk: Optional[int] = None  # FK directa a persona existente
    persona: Optional[PersonaUpdateRequest] = None

    class Config:
        validate_by_name = True

