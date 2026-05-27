from typing import Optional
from pydantic import BaseModel


class LocalRequest(BaseModel):
    nombre: str
    estado: Optional[bool] = True
    direccion: Optional[str] = None
    telefono: Optional[str] = None

    class Config:
        validate_by_name = True


class LocalUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[bool] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None

    class Config:
        validate_by_name = True
