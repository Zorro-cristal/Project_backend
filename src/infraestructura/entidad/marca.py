from dataclasses import dataclass

@dataclass(frozen=True)
class Marca:
    id: int
    nombre: str
    estado: Optional[int]= 1
    