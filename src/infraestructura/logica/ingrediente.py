from src.infraestructura.database.ingrediente import actualizarIngrediente, obtenerIngrediente
from src.infraestructura.entidad.ingrediente import Ingrediente


def build_ingrediente_entity(payload: dict) -> Ingrediente:
    valid_fields = {key: value for key, value in payload.items() if key in Ingrediente.__annotations__}
    return Ingrediente(**valid_fields)


async def obtener_ingredientes(filtros: dict = None, columnas: str = '*'):
    return await obtenerIngrediente(filtros=filtros, columnas=columnas)


async def crear_ingrediente(payload: dict):
    ingrediente = build_ingrediente_entity(payload)
    return await actualizarIngrediente(ingrediente)


async def actualizar_ingrediente(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarIngrediente(payload, id)
