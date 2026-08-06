from ..models.rol import Rol
from ..repositories.permiso_rol_repository import obtenerPermisosPorRol
from ..repositories.rol_repository import actualizarRol, obtenerRol


def build_rol_entity(payload: dict) -> Rol:
    valid_fields = {key: value for key, value in payload.items() if key in Rol.__annotations__}
    return Rol(**valid_fields)


async def obtener_roles(filtros: dict = None, columnas: str = '*'):
    roles = await obtenerRol(filtros=filtros, columnas=columnas)
    if not roles:
        return roles

    # Adjuntar a cada rol los permisos asociados que estén activos (permiso.estado == 1)
    for rol in roles:
        rol['permisos'] = await _permisos_activos_de_rol(rol.get('id'))

    return roles


async def _permisos_activos_de_rol(id_rol):
    """Obtiene los permisos activos (permiso.estado == 1) asociados a un rol."""
    if id_rol is None:
        return []
    asignaciones = await obtenerPermisosPorRol(id_rol)
    return [
        a for a in asignaciones
        if a.get('permisos') is not None
        and a.get('permisos', {}).get('estado') == 1
    ]


async def obtener_rol_por_id(id_rol: int):
    """Obtiene un rol por su ID junto con sus permisos activos."""
    roles = await obtenerRol(filtros={'id': id_rol})
    if not roles:
        return None
    rol = roles[0]
    rol['permisos'] = await _permisos_activos_de_rol(rol.get('id'))
    return rol


async def crear_rol(payload: dict):
    rol = build_rol_entity(payload)
    return await actualizarRol(rol)


async def actualizar_rol(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarRol(payload, id)
