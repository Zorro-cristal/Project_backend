from typing import Optional
from pydantic import BaseModel

class UsuarioRequest(BaseModel):
    alias: str
    contra: str
    estado: Optional[int] = 1

    class Config:
        validate_by_name = True

class UsuarioUpdateRequest(BaseModel):
    alias: Optional[str] = None
    contra: Optional[str] = None
    estado: Optional[int] = None

    class Config:
        validate_by_name = True
