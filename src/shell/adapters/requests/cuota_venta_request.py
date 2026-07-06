from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CuotaVentaRequest(BaseModel):
    """Request para crear una cuota de venta."""
    estado: Optional[int] = 1
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    descuento: Optional[float] = None
    interes: Optional[int] = None
    id_ventafk: Optional[int] = None
    id_vendedorfk: Optional[int] = None
    # Compatibilidad
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True


class CuotaVentaUpdateRequest(BaseModel):
    """Request para actualizar una cuota de venta."""
    estado: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    descuento: Optional[float] = None
    interes: Optional[int] = None

    class Config:
        validate_by_name = True


class GenerarCuotasRequest(BaseModel):
    """Request para generar cuotas automáticamente."""
    total_cuotas: int
    monto_cuota: float
    fecha_inicio: datetime
    descuento: Optional[float] = 0
    interes: Optional[int] = 0
    id_vendedorfk: Optional[int] = None
    # Compatibilidad
    id_usuariofk: Optional[int] = None

    class Config:
        validate_by_name = True
