from typing import Optional

from pydantic import BaseModel, Field


class ProductoRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    estado: int = 1
    impuesto: int
    pesable: bool
    perecedero: bool = False
    costeo: int
    unidad_medida: str
    es_ingrediente: Optional[bool] = None

    # Keep original aliases (capitalization varies in client payload)
    id_categoriafk: int = Field(..., alias="id_categoriafk")
    id_marcafk: int = Field(..., alias="id_marcafk")

    class Config:
        validate_by_name = True


class ProductoUpdateRequest(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[int] = None
    impuesto: Optional[int] = None
    pesable: Optional[bool] = None
    perecedero: Optional[bool] = None
    costeo: Optional[int] = None
    unidad_medida: Optional[str] = None
    es_ingrediente: Optional[bool] = None
    id_categoriafk: Optional[int] = Field(None, alias="id_categoriafk")
    id_marcafk: Optional[int] = Field(None, alias="id_marcafk")

    class Config:
        validate_by_name = True

