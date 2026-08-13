from ..models.permiso_rol import PermisoRol
from ..repositories.permiso_repository import obtenerPermiso
from ..repositories.permiso_rol_repository import (actualizarPermisoRol,
                                                   obtenerPermisoRol,
                                                   obtenerPermisosPorRol,
                                                   obtenerRolesPorPermiso)


def build_permiso_rol_entity(payload: dict) -> PermisoRol:
    valid_fields = {key: value for key, value in payload.items() if key in PermisoRol.__annotations__}
    return PermisoRol(**valid_fields)


async def _ids_permisos_activos(ids_permiso) -> set:
    if not ids_permiso:
        return set()

    permisos = await obtenerPermiso(filtros={'id': list(ids_permiso)})
    return {
        p.get('id')
        for p in permisos
        if (p.get('estado') is True or p.get('estado') == 1)
    }


async def obtener_permisos_roles(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    registros = await obtenerPermisoRol(filtros=filtros, limite=limite, offset=offset, columnas=columnas)
    if not registros:
        return registros

    # Recolectar los id de permisos asociados y quedarnos solo con los activos.
    ids_permiso = {r.get('id_permisofk') for r in registros if r.get('id_permisofk') is not None}
    ids_activos = await _ids_permisos_activos(ids_permiso)

    # Solo devolver los registros cuyo permiso asociado esté activo.
    return [r for r in registros if r.get('id_permisofk') in ids_activos]


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
    if not registros:
        return registros

    ids_permiso = {r.get('id_permisofk') for r in registros if r.get('id_permisofk') is not None}
    ids_activos = await _ids_permisos_activos(ids_permiso)

    return [r for r in registros if r.get('id_permisofk') in ids_activos]


async def obtener_roles_con_permiso(id_permiso: int):
    """Obtiene todos los roles que tienen asignado un permiso específico activo."""
    registros = await obtenerRolesPorPermiso(id_permiso)
    if not registros:
        return registros

    ids_permiso = {r.get('id_permisofk') for r in registros if r.get('id_permisofk') is not None}
    ids_activos = await _ids_permisos_activos(ids_permiso)

    return [r for r in registros if r.get('id_permisofk') in ids_activos]
