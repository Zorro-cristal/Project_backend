from typing import Optional

from pydantic import BaseModel


class PermisoRequest(BaseModel):
    nombre: str

    class Config:
        validate_by_name = True


class PermisoUpdateRequest(BaseModel):
    nombre: Optional[str] = None

    class Config:
        validate_by_name = True

