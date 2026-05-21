from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class RolRequest(BaseModel):
    nombre: str
    observacion: Optional[str] = None
    estado: int = 1
    fecha_creacion: Optional[datetime] = None

    class Config:
        validate_by_name = True

class RolUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    observacion: Optional[str] = None
    estado: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        validate_by_name = True
