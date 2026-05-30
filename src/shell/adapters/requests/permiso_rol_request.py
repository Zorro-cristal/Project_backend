from typing import Optional
from pydantic import BaseModel

class PermisoRolRequest(BaseModel):
    crear: bool = False
    editar: bool = False
    eliminar: bool = False
    leer: bool = False
    id_permisofk: int
    id_rolfk: int

    class Config:
        validate_by_name = True


class PermisoRolUpdateRequest(BaseModel):
    crear: Optional[bool] = None
    editar: Optional[bool] = None
    eliminar: Optional[bool] = None
    leer: Optional[bool] = None
    id_permisofk: Optional[int] = None
    id_rolfk: Optional[int] = None

    class Config:
        validate_by_name = True
