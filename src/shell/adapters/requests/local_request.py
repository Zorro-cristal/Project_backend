from typing import Optional

from pydantic import BaseModel


class LocalRequest(BaseModel):
    nombre: str
    estado: Optional[int] = 1
    cod_num: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None

    class Config:
        validate_by_name = True



class LocalUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[int] = None
    cod_num: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None

    class Config:
        validate_by_name = True
