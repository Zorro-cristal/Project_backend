from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.permiso_rol_service import (
    actualizar_permiso_rol,
    crear_permiso_rol,
    obtener_permisos_roles,
    obtener_permisos_de_rol,
    obtener_roles_con_permiso,
)
from src.shell.adapters.requests.permiso_rol_request import (
    PermisoRolRequest,
    PermisoRolUpdateRequest,
)

router = APIRouter()

@router.put("/{id}", summary="Actualizar asignación de permiso a rol", description="Actualiza los niveles de acceso de un permiso en un rol.")
async def actualizarPermisoRolApi(id: int, requestBody: PermisoRolUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_permiso_rol(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar asignación parcialmente", description="Actualiza parcialmente los niveles de acceso.")
async def patchPermisoRolApi(id: int, requestBody: PermisoRolUpdateRequest):
    return await actualizarPermisoRolApi(id, requestBody)

@router.post("/", summary="Asignar permiso a rol", description="Asigna un permiso a un rol con niveles específicos de acceso.")
async def agregarPermisoRolApi(requestBody: PermisoRolRequest):
    payload = requestBody.model_dump()
    result = await crear_permiso_rol(payload)
    return {"message": result}

@router.get("/", summary="Obtener asignaciones de permisos a roles", description="Obtiene una lista de asignaciones con filtros opcionales.")
async def obtenerPermisosRolesApi(
    id: Optional[int] = Query(None, description="Filtrar por ID de asignación"),
    id_permisofk: Optional[int] = Query(None, description="Filtrar por permiso"),
    id_rolfk: Optional[int] = Query(None, description="Filtrar por rol"),
    crear: Optional[bool] = Query(None, description="Filtrar por permiso de crear"),
    editar: Optional[bool] = Query(None, description="Filtrar por permiso de editar"),
    eliminar: Optional[bool] = Query(None, description="Filtrar por permiso de eliminar"),
    leer: Optional[bool] = Query(None, description="Filtrar por permiso de lectura"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_permisofk is not None:
        filtros["id_permisofk"] = id_permisofk
    if id_rolfk is not None:
        filtros["id_rolfk"] = id_rolfk
    if crear is not None:
        filtros["crear"] = crear
    if editar is not None:
        filtros["editar"] = editar
    if eliminar is not None:
        filtros["eliminar"] = eliminar
    if leer is not None:
        filtros["leer"] = leer

    result = await obtener_permisos_roles(filtros=filtros)
    return {"message": result}

@router.get("/rol/{id_rol}", summary="Obtener permisos de un rol", description="Obtiene todos los permisos asignados a un rol específico.")
async def obtenerPermisosDeRolApi(id_rol: int):
    result = await obtener_permisos_de_rol(id_rol)
    return {"message": result}

@router.get("/permiso/{id_permiso}", summary="Obtener roles con un permiso", description="Obtiene todos los roles que tienen asignado un permiso específico.")
async def obtenerRolesConPermisoApi(id_permiso: int):
    result = await obtener_roles_con_permiso(id_permiso)
    return {"message": result}
