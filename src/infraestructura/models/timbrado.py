from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Timbrado:
    nro_timbrado: int
    fin_vigencia: datetime
    actualizado_por: int= None
    id: Optional[int] = None
