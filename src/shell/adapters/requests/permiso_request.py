from typing import Optional
from pydantic import BaseModel

class PermisoRequest(BaseModel):
    nombre: str
    crear: bool = False
    editar: bool = False
    eliminar: bool = False
    leer: bool = False
    id_rolFK: int

    class Config:
        validate_by_name = True


class PermisoUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    crear: Optional[bool] = None
    editar: Optional[bool] = None
    eliminar: Optional[bool] = None
    leer: Optional[bool] = None
    id_rolFK: Optional[int] = None

    class Config:
        validate_by_name = True
