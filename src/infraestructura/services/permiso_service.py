from ..models.permiso import Permiso
from ..repositories.permiso_repository import actualizarPermiso, obtenerPermiso
from ..repositories.permiso_rol_repository import (actualizarPermisoRol,
                                                   obtenerPermisoRol)
from ..services.rol_service import obtener_roles


def build_permiso_entity(payload: dict) -> Permiso:
    valid_fields = {key: value for key, value in payload.items() if key in Permiso.__annotations__}
    return Permiso(**valid_fields)


async def obtener_permisos(filtros: dict = None, columnas: str = '*', limite: int = 100, offset: int = 0):
    return await obtenerPermiso(filtros=filtros, limite=limite, offset=offset, columnas=columnas)


async def crear_permiso(payload: dict):
    permiso = build_permiso_entity(payload)
    return await actualizarPermiso(permiso)


async def actualizar_permiso(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPermiso(payload, id)


async def asignar_permiso_a_todos_roles(id_permiso: int):
    """Asigna un permiso a todos los roles activos existentes.

    Crea únicamente los registros de `permisos_roles` que falten para garantizar
    que el permiso quede asociado a todos los roles activos. Los niveles de acceso
    (crear, editar, eliminar, leer) se crean en `False` por defecto.
    """
    # 1. Validar que el permiso exista.
    permisos = await obtenerPermiso(filtros={'id': id_permiso})
    if not permisos:
        raise ValueError(f"No existe un permiso con id {id_permiso}")

    # 2. Obtener todos los roles activos.
    roles = await obtener_roles(filtros={'estado': 1})

    # 3. Obtener las asignaciones existentes para este permiso.
    asignaciones = await obtenerPermisoRol(filtros={'id_permisofk': id_permiso})
    roles_asignados = {a.get('id_rolfk') for a in asignaciones if a.get('id_rolfk') is not None}

    creados = []
    for rol in roles:
        id_rol = rol.get('id')
        if id_rol is None or id_rol in roles_asignados:
            continue

        nuevo = {
            'id_permisofk': id_permiso,
            'id_rolfk': id_rol,
            'crear': False,
            'editar': False,
            'eliminar': False,
            'leer': False,
        }
        registro = await actualizarPermisoRol(nuevo)
        creados.append(registro)
        roles_asignados.add(id_rol)

    return {
        'id_permiso': id_permiso,
        'registros_creados': creados,
        'total_roles': len(roles),
        'total_creados': len(creados),
    }
