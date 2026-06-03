from ..repositories.rol_repository import actualizarRol, obtenerRol
from ..models.rol import Rol


def build_rol_entity(payload: dict) -> Rol:
    valid_fields = {key: value for key, value in payload.items() if key in Rol.__annotations__}
    return Rol(**valid_fields)


async def obtener_roles(filtros: dict = None, columnas: str = '*'):
    return await obtenerRol(filtros=filtros, columnas=columnas)


async def crear_rol(payload: dict):
    rol = build_rol_entity(payload)
    return await actualizarRol(rol)


async def actualizar_rol(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarRol(payload, id)
