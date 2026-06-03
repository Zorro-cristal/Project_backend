from dataclasses import dataclass
from typing import Optional

from .categoria import Categoria
from .detalles_producto import detalles_producto
from .ingrediente import Ingrediente
from .marca import Marca


@dataclass(frozen=True)
class Producto:
    nombre: str
    impuesto: int
    pesable: bool
    costeo: int
    unidad_medida: str
    id_categoriafk: int
    id_marcafk: int
    descripcion: Optional[str] = None
    estado: int = 1
    perecedero: bool = False
    es_ingrediente: Optional[bool] = None
    es_comida: Optional[bool] = None
    categoria: Optional[Categoria] = None
    marca: Optional[Marca] = None
    detalles_producto: Optional[list[detalles_producto]] = None
    ingredientes: Optional[list[Ingrediente]] = None
    id: Optional[int] = None