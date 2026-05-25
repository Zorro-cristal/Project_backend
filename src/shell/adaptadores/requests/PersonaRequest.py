from typing import Optional
from pydantic import BaseModel

class PersonaRequest(BaseModel):
    cedula: int
    nombres: str
    apellidos: str
    estado: Optional[int] = 1
    telefono: Optional[int] = None
    direccion: Optional[str] = None
    nacionalidad: Optional[str] = None

    class Config:
        validate_by_name = True


class PersonaUpdateRequest(BaseModel):
    id: Optional[int] = None
    cedula: Optional[int] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    estado: Optional[int] = None
    telefono: Optional[int] = None
    direccion: Optional[str] = None
    nacionalidad: Optional[str] = None

    class Config:
        validate_by_name = True
