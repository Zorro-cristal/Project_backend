from typing import Optional

from pydantic import BaseModel, Field


class IngredienteRequest(BaseModel):
    cantidad: int
    unidad_medida: str
    id_producto_ingredientefk: int = Field(..., alias="Productos_id_ingrediente")
    id_producto_finalfk: int = Field(..., alias="Productos_id_final")

    class Config:
        validate_by_name = True


class IngredienteUpdateRequest(BaseModel):
    cantidad: Optional[int] = None
    unidad_medida: Optional[str] = None
    id_producto_ingredientefk: Optional[int] = Field(None, alias="Productos_id_ingrediente")
    id_producto_finalfk: Optional[int] = Field(None, alias="Productos_id_final")

    class Config:
        validate_by_name = True
