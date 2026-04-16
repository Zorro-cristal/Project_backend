from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Marca:
    nombre: str
    estado: int= 1
    id: Optional[int]= None
    