from dataclasses import dataclass
from src.infraestructura.entidad.categoria import Categoria
from src.infraestructura.entidad.marca import Marca
from src.infraestructura.entidad.detalle_producto import Detalle_producto

@dataclass(frozen=True)
class Producto:
    id: int
    nombre: str
    descripcion: Optional[str]= None
    estado: Optional[int]= 1
    impuesto: int
    pesable: bool
    perecedero: Optional[bool]= false
    costeo: int
    unidad_medida: str
    es_ingrediente: Optional[bool]= true
    categoria: Categoria
    marca: Marca
    detalles_producto: Detalle_producto[]