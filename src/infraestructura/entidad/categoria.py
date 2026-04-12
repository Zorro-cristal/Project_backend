from dataclasses import dataclass

@dataclass(frozen=True)
class Categoria:
    id: int
    nombre: str
    descripcion: Optional[str]= None
    estado: Optional[int]= 1