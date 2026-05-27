from src.infraestructura.repositories.local_repository import actualizarLocal, obtenerLocal
from src.infraestructura.models.local import Local


def build_local_entity(payload: dict) -> Local:
    valid_fields = {key: value for key, value in payload.items() if key in Local.__annotations__}
    return Local(**valid_fields)


async def obtener_locales(filtros: dict = None, columnas: str = '*'):
    return await obtenerLocal(filtros=filtros, columnas=columnas)


async def crear_local(payload: dict):
    local = build_local_entity(payload)
    return await actualizarLocal(local)


async def actualizar_local(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    return await actualizarLocal(payload, id)
