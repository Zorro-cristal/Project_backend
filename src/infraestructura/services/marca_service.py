
from src.infraestructura.repositories.marca_repository import actualizarMarca, obtenerMarca
from src.infraestructura.models.marca import Marca

def build_marca_entity(payload: dict) -> Marca:
    valid_fields = {key: value for key, value in payload.items() if key in Marca.__annotations__}
    return Marca(**valid_fields)


async def obtener_marcas(filtros: dict= None, columnas: str = '*'):
    return await obtenerMarca(columnas=columnas, filtros=filtros)


async def crear_marca(payload: dict):
    marca = build_marca_entity(payload)
    return await actualizarMarca(marca)


async def actualizar_marca(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarMarca(payload, id)
