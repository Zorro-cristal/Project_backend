from typing import Optional, List
from pydantic import BaseModel, Field

class PrecioResponse(BaseModel):
    monto: int
    valido_desde: str
    valido_hasta: Optional[str] = None
    id: Optional[int] = None

class DetalleProductoRequest(BaseModel):
    unidad_por_lote: int
    color: str
    tamanho: int
    precios: List[PrecioResponse] = []
    cod_barra: Optional[int] = None
    
    class Config:
        validate_by_name = True


class DetalleProductoUpdateRequest(BaseModel):
    unidad_por_lote: Optional[int] = None
    color: Optional[str] = None
    tamanho: Optional[int] = None
    precios: Optional[List[PrecioResponse]] = None
    cod_barra: Optional[int] = None

    class Config:
        validate_by_name = True
