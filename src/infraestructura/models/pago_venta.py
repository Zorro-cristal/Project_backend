from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class PagoVenta:
    """Modelo para la tabla pagos_venta.
    
    Tipos de pago (PagoVenta.tipo):
    - 1: Cuota
    - 2: Entrega
    
    Nota:
    - Para ventas al contado, el servicio guarda `tipo = NULL` (no se usa 1 o 2).
    
    Estados:
    - 1: Activo
    - 0: Inactivo/Anulado
    """
    estado: int = 1
    tipo: Optional[int] = None
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    id_ventafk: Optional[int] = None
    id_cajafk: Optional[int] = None
    fecha_creado: Optional[datetime] = None
    id: Optional[int] = None
