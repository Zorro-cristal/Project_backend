from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Precio:
    id: int
    monto: int
    valido_desde: datetime
    valido_hasta: Optional[datetime]= None