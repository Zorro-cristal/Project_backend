from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Categoria:
    nombre: str
    estado: int= 1
    descripcion: Optional[str]= None
    id: Optional[int]= None