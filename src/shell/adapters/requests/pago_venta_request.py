from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PagoVentaRequest(BaseModel):
    """Request para registrar un pago de venta."""
    tipo: int  # 1: Cuota, 2: Entrega
    monto: float
    fecha: Optional[datetime] = None
    id_ventafk: int
    id_cajafk: int
    id_vendedorfk: Optional[int] = None
    # Compatibilidad
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True


class PagoVentaUpdateRequest(BaseModel):
    """Request para actualizar un pago de venta."""
    tipo: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None

    class Config:
        validate_by_name = True


class RegistroPagoContadoRequest(BaseModel):
    """Request para registrar pago de venta al contado."""
    id_venta: int
    monto_total: float
    id_cajafk: int
    id_vendedorfk: Optional[int] = None
    # Compatibilidad
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True


class RegistroPagoCuotaRequest(BaseModel):
    """Request para registrar pago de cuota."""
    id_venta: int
    monto: float
    id_cajafk: int
    id_vendedorfk: Optional[int] = None
    # Compatibilidad
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True
