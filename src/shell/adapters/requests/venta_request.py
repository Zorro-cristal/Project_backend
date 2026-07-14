from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.shell.adapters.requests.cliente_request import ClienteRequest
from src.shell.adapters.requests.detalle_venta_request import \
    DetalleVentaRequest
from src.shell.adapters.requests.local_request import LocalRequest


# =============================================================================
# Modelo Base - Campos comunes para todas las ventas
# =============================================================================
class VentaBase(BaseModel):
    """Base model con campos comunes. No usar directamente."""
    fecha: datetime
    estado: Optional[int] = 1
    evento_festivo: Optional[bool] = None
    tipo_credito: Optional[int] = None
    total_cuotas: Optional[int] = None
    monto_entrega: Optional[float] = 0
    cod_num: Optional[str] = None
    id_vendedorfk: Optional[int] = None
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None

    # Para POST /venta (evitar depender de ordenes.id_mesafk)
    # Si viene desde el front, se usa para calcular ventas.ocupacion.
    id_mesafk: Optional[int] = None

    cliente: Optional[ClienteRequest] = None
    local: Optional[LocalRequest] = None
    detalles_venta: Optional[List[DetalleVentaRequest]] = None
    # Campos para venta a crédito
    fecha_inicio: Optional[datetime] = None
    # subtotal se calcula en el servicio, no se recibe en entrada
    # Los datos de clima (clima, temperatura, humedad y métricas adicionales) se obtienen automáticamente en el backend
    velocidad_viento: Optional[float] = None
    lluvia: Optional[float] = None
    precipitaciones: Optional[float] = None
    probabilidad_precipitaciones: Optional[float] = None

    class Config:
        validate_by_name = True


# =============================================================================
# Modelos específicos para cada tipo de operación
# =============================================================================
class VentaUpdateRequest(VentaBase):
    """Request para actualizar venta - todos los campos opcionales."""
    fecha: Optional[datetime] = None
    cod_num: Optional[str] = None


class VentaCreditoRequest(VentaBase):
    """Request para venta a crédito (tipo_credito=1).
    
    Requiere campos adicionales para generar las cuotas.
    """
    tipo_credito: int = Field(default=1, frozen=True)  # Siempre 1
    id_clientefk: int
    id_localfk: int
    id_cajafk: int
    total_cuotas: int = Field(description="Total de cuotas a generar")
    monto_cuota: float = Field(description="Monto de cada cuota")
    fecha_inicio: datetime = Field(description="Fecha de la primera cuota")
    descuento: Optional[float] = 0
    interes: Optional[int] = 0
