from typing import Optional
from pydantic import BaseModel

class PermisoRolRequest(BaseModel):
    crear: bool = False
    editar: bool = False
    eliminar: bool = False
    leer: bool = False
    id_permisoFK: int
    id_rolFK: int

    class Config:
        validate_by_name = True


class PermisoRolUpdateRequest(BaseModel):
    crear: Optional[bool] = None
    editar: Optional[bool] = None
    eliminar: Optional[bool] = None
    leer: Optional[bool] = None
    id_permisoFK: Optional[int] = None
    id_rolFK: Optional[int] = None

    class Config:
        validate_by_name = True
