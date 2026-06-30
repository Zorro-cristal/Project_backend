from typing import Optional

from pydantic import BaseModel

from src.shell.adapters.requests.producto_request import ProductoRequest


# =============================================================================
# Modelo Base - Campos comunes
# =============================================================================
class DetalleVentaBase(BaseModel):
    """Base model con campos comunes."""
    precio: float
    descuento: Optional[float] = None
    id_detalleproductofk: Optional[str] = None
    id_ventafk: Optional[int] = None
    producto: Optional[ProductoRequest] = None
    # subtotal se calcula en el servicio, no se recibe en entrada

    class Config:
        validate_by_name = True


# =============================================================================
# Modelos específicos
# =============================================================================

class DetalleVentaRequest(DetalleVentaBase):
    """Request para crear detalle de venta."""
    cantidad: int


class DetalleVentaUpdateRequest(DetalleVentaBase):
    """Request para actualizar detalle de venta - todos los campos opcionales."""
    cantidad: Optional[int] = None
    precio: Optional[float] = None
