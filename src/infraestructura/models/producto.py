from dataclasses import dataclass
from typing import Optional

from src.infraestructura.models.categoria import Categoria
from src.infraestructura.models.detalle_producto import Detalle_producto
from src.infraestructura.models.ingrediente import Ingrediente
from src.infraestructura.models.marca import Marca


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
    detalles_producto: Optional[list[Detalle_producto]] = None
    ingredientes: Optional[list[Ingrediente]] = None
    id: Optional[int] = None