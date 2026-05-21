from dataclasses import dataclass

@dataclass(frozen=True)
class Ingrediente:
    id: int
    cantidad: int
    unidad_medida: str
    producto_id_ingrediente: int
    producto_id_final: int