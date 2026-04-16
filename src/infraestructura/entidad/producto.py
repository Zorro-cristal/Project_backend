from dataclasses import dataclass
from typing import Optional

from src.infraestructura.entidad.categoria import Categoria
from src.infraestructura.entidad.detalle_producto import Detalle_producto
from src.infraestructura.entidad.marca import Marca

@dataclass(frozen=True)
class Producto:
    nombre: str
    impuesto: int
    pesable: bool
    costeo: int
    unidad_medida: str
    categoria_id: int
    marca_id: int
    descripcion: Optional[str] = None
    estado: int = 1
    perecedero: bool = False
    es_ingrediente: Optional[bool] = None
    categoria: Optional[Categoria] = None
    marca: Optional[Marca] = None
    detalles_producto: Optional[list[Detalle_producto]] = None
    id: Optional[int] = None