from typing import Optional
from pydantic import BaseModel, Field

class IngredienteRequest(BaseModel):
    cantidad: int
    unidad_medida: str
    producto_id_ingrediente: int = Field(..., alias="Productos_id_ingrediente")
    producto_id_final: int = Field(..., alias="Productos_id_final")

    class Config:
        validate_by_name = True


class IngredienteUpdateRequest(BaseModel):
    cantidad: Optional[int] = None
    unidad_medida: Optional[str] = None
    producto_id_ingrediente: Optional[int] = Field(None, alias="Productos_id_ingrediente")
    producto_id_final: Optional[int] = Field(None, alias="Productos_id_final")

    class Config:
        validate_by_name = True
