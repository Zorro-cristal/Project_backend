from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.persona_request import (PersonaRequest,
                                                         PersonaUpdateRequest)


class VendedorRequest(BaseModel):
    salario: float
    comision: float
    estado: Optional[int] = 1
    cod_num: Optional[str] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaRequest] = None

    class Config:
        validate_by_name = True


class VendedorUpdateRequest(BaseModel):
    salario: Optional[float] = None
    comision: Optional[float] = None
    estado: Optional[int] = None
    cod_num: Optional[str] = None
    id_personafk: Optional[int] = None
    persona: Optional[PersonaUpdateRequest] = None

    class Config:
        validate_by_name = True
