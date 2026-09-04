from typing import Optional

from pydantic import BaseModel

# Estados válidos para orden
# 0: 'inactivo', 1: 'pendiente', 2: 'en_proceso', 3: 'listo', 4: 'entregado'
ESTADO_ORDEN = {
    0: 'inactivo',
    1: 'pendiente',
    2: 'en_proceso',
    3: 'listo',
    4: 'entregado',
}


class OrdenRequest(BaseModel):
    estado: Optional[int] = 1  # Por defecto: pendiente (1)
    cantidad: Optional[int] = 1
    observacion: Optional[str] = None

    id_mesafk: int
    id_detalleproductofk: Optional[str] = None
    id_usuariofk: Optional[int] = None
    id_preciofk: Optional[int] = None
    tipo: int = 1  # 1 = mesa, 2 = delivery, 3 = retiro

    last_print_error: Optional[str] = None

    class Config:
        validate_by_name = True


class OrdenUpdateRequest(BaseModel):
    estado: Optional[int] = None
    cantidad: Optional[int] = None
    observacion: Optional[str] = None

    id_mesafk: Optional[int] = None
    id_detalleproductofk: Optional[str] = None
    id_usuariofk: Optional[int] = None
    id_preciofk: Optional[int] = None
    tipo: int = 1  # 1 = mesa, 2 = delivery, 3 = retiro

    estado_impresion: Optional[str] = None
    last_print_error: Optional[str] = None

    class Config:
        validate_by_name = True

