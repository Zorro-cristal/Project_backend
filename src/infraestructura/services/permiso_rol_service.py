from ..models.permiso_rol import PermisoRol
from ..repositories.permiso_rol_repository import (actualizarPermisoRol,
                                                   obtenerPermisoRol,
                                                   obtenerPermisosPorRol,
                                                   obtenerRolesPorPermiso)


def build_permiso_rol_entity(payload: dict) -> PermisoRol:
    valid_fields = {key: value for key, value in payload.items() if key in PermisoRol.__annotations__}
    return PermisoRol(**valid_fields)


async def obtener_permisos_roles(filtros: dict = None, columnas: str = '*'):
    registros = await obtenerPermisoRol(filtros=filtros, columnas="*, permisos(estado)")
    if not registros:
        return registros
    # Solo devolver los registros cuyo permiso asociado esté activo (estado == 1)
    return [
        r for r in registros
        if r.get('permisos') is not None
        and r.get('permisos', {}).get('estado') == 1
    ]


async def crear_permiso_rol(payload: dict):
    """Asigna un permiso a un rol con niveles específicos de acceso."""
    permiso_rol = build_permiso_rol_entity(payload)
    return await actualizarPermisoRol(permiso_rol)


async def actualizar_permiso_rol(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPermisoRol(payload, id)


async def obtener_permisos_de_rol(id_rol: int):
    """Obtiene todos los permisos asignados a un rol específico (solo permisos activos)."""
    registros = await obtenerPermisosPorRol(id_rol)
    return [
        r for r in registros
        if r.get('permisos') is not None
        and r.get('permisos', {}).get('estado') == 1
    ]


async def obtener_roles_con_permiso(id_permiso: int):
    """Obtiene todos los roles que tienen asignado un permiso específico activo."""
    registros = await obtenerRolesPorPermiso(id_permiso)
    return [
        r for r in registros
        if r.get('permisos') is not None
        and r.get('permisos', {}).get('estado') == 1
    ]
