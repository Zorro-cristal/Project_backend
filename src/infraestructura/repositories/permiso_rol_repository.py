from typing import Optional, Union

from src.infraestructura.models.permiso_rol import PermisoRol
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb, normalizar_booleanos


async def obtenerPermisoRol(filtros: Optional[dict] = None, limite: int = 100, offset: int = 0, columnas: str = "*"):
    return await get('permisos_roles', filtros, limite, offset, columns=columnas)


async def actualizarPermisoRol(datos: Union[PermisoRol, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos)
    
    # Normalizar los booleanos (crear, editar, eliminar, leer) a BIT (0 o 1)
    payload = normalizar_booleanos(
        payload,
        ['crear', 'editar', 'eliminar', 'leer'],
        on_insert=id is None,
    )

    if id is None:
        return await insert('permisos_roles', payload)
    return await update('permisos_roles', id, payload)


async def obtenerPermisosPorRol(id_rol: int):
    """Obtiene todos los permisos asignados a un rol específico."""
    return await get('permisos_roles', {'id_rolFK': id_rol}, limit=1000, columns="*, permisos(nombre)")


async def obtenerRolesPorPermiso(id_permiso: int):
    """Obtiene todos los roles que tienen asignado un permiso específico."""
    return await get('permisos_roles', {'id_permisoFK': id_permiso}, limit=1000, columns="*, roles(nombre)")
