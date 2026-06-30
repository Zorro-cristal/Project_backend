from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.detalle_venta_request import \
    DetalleVentaRequest
from src.shell.adapters.requests.local_request import LocalRequest


class VentaRequest(BaseModel):
    nro: Optional[str] = None
    fecha: datetime
    estado: Optional[int] = 1
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    tipo_credito: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles_venta: Optional[List[DetalleVentaRequest]] = None
#    subtotal: Optional[float] = None

    class Config:
        validate_by_name = True


class VentaUpdateRequest(BaseModel):
    nro: Optional[str] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    tipo_credito: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles_venta: Optional[List[DetalleVentaRequest]] = None
#    subtotal: Optional[float] = None

    class Config:
        validate_by_name = True


# Nuevos modelos para ventas con pagos y cuotas

class VentaContadoRequest(BaseModel):
    """Request para crear una venta al contado."""
    nro: Optional[str] = None
    fecha: datetime
    estado: Optional[int] = 1
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    tipo_credito: int = 0  # Siempre 0 para contado
    id_clientefk: int
    id_localfk: int
    id_cajafk: int
    # Campo adicional para ventas al contado
    monto_total: float
    # Detalles de la venta
    detalles_venta: Optional[List[DetalleVentaRequest]] = None
    subtotal: Optional[float] = None

    class Config:
        validate_by_name = True


class VentaCreditoRequest(BaseModel):
    """Request para crear una venta a crédito."""
    nro: Optional[str] = None
    fecha: datetime
    estado: Optional[int] = 1
    cod_usuariofk_edit: Optional[bool] = None
    empresa_id: Optional[int] = None
    clima: Optional[int] = None
    temperatura: Optional[int] = None
    humedad: Optional[int] = None
    evento: Optional[bool] = None
    tipo_credito: int = 1  # Siempre 1 para crédito
    id_clientefk: int
    id_localfk: int
    id_cajafk: int
    # Campos adicionales para ventas a crédito
    total_cuotas: int
    monto_cuota: float
    fecha_inicio: datetime
    descuento: Optional[float] = 0
    interes: Optional[int] = 0
    # Detalles de la venta
    detalles_venta: Optional[List[DetalleVentaRequest]] = None
    subtotal: Optional[float] = None

    class Config:
        validate_by_name = True

