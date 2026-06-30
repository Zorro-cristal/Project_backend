from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class CuotaCompra:
    """Modelo para la tabla cuotas_compra.
    
    Estados de cuota:
    - 1: Pendiente
    - 2: Saldada (pagada completamente)
    - 3: Parcial (pagada parcialmente)
    """
    estado: int = 1
    monto: Optional[float] = None
    fecha: Optional[datetime] = None
    descuento: Optional[float] = None
    interes: Optional[int] = None
    id_comprafk: Optional[int] = None
    id_usuariofk: Optional[int] = None
    fecha_creado: Optional[datetime] = None
    id: Optional[int] = None
