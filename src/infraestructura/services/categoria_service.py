
from src.infraestructura.repositories.categoria_repository import actualizarCategoria, obtenerCategoria
from src.infraestructura.models.categoria import Categoria


def build_categoria_entity(payload: dict) -> Categoria:
    valid_fields = {key: value for key, value in payload.items() if key in Categoria.__annotations__}
    return Categoria(**valid_fields)

async def obtener_categorias(filtros: dict = None, columnas: str= "*"):
    return await obtenerCategoria(filtros=filtros, columnas=columnas)


async def crear_categoria(payload: dict):
    categoria = build_categoria_entity(payload)
    return await actualizarCategoria(categoria)


async def actualizar_categoria(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarCategoria(payload, id)
