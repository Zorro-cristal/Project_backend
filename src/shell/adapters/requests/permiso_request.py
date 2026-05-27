from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PermisoRequest(BaseModel):
    nombre: str
    fecha_edit: Optional[datetime] = None

    class Config:
        validate_by_name = True


class PermisoUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    fecha_edit: Optional[datetime] = None

    class Config:
        validate_by_name = True
