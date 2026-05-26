from src.infraestructura.repositories.permiso_repository import actualizarPermiso, obtenerPermiso
from src.infraestructura.models.permiso import Permiso


def build_permiso_entity(payload: dict) -> Permiso:
    valid_fields = {key: value for key, value in payload.items() if key in Permiso.__annotations__}
    return Permiso(**valid_fields)


async def obtener_permisos(filtros: dict = None, columnas: str = '*'):
    return await obtenerPermiso(filtros=filtros, columnas=columnas)


async def crear_permiso(payload: dict):
    permiso = build_permiso_entity(payload)
    return await actualizarPermiso(permiso)


async def actualizar_permiso(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPermiso(payload, id)
