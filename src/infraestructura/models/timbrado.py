from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class Timbrado:
    nro_timbrado: str
    fin_vigencia: datetime
    id: Optional[int] = None
