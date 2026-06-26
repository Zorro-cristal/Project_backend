from typing import Optional

from pydantic import BaseModel


class OrdenRequest(BaseModel):
    estado: Optional[str] = 'Pendiente'
    cantidad: Optional[int] = 1
    observacion: Optional[str] = None

    id_mesafk: Optional[int] = None
    id_detalleproductofk: Optional[str] = None
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True


class OrdenUpdateRequest(BaseModel):
    estado: Optional[str] = None
    cantidad: Optional[int] = None
    observacion: Optional[str] = None

    id_mesafk: Optional[int] = None
    id_detalleproductofk: Optional[str] = None
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True

