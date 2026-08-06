from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.permiso_request import (PermisoRequest,
                                                         PermisoUpdateRequest)

from ..services.permiso_service import (actualizar_permiso,
                                        asignar_permiso_a_todos_roles,
                                        crear_permiso, obtener_permisos)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('permiso', 'editar'))], summary="Actualizar permiso", description="Actualiza un permiso existente por su ID.")
async def actualizarPermisoApi(id: int, requestBody: PermisoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_permiso(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('permiso', 'editar'))], summary="Actualizar permiso parcialmente", description="Actualiza parcialmente un permiso existente por su ID.")
async def patchPermisoApi(id: int, requestBody: PermisoUpdateRequest):
    return await actualizarPermisoApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('permiso', 'crear'))], summary="Crear permiso", description="Crea un nuevo permiso.")
async def agregarPermisoApi(requestBody: PermisoRequest):
    payload = requestBody.model_dump()
    result = await crear_permiso(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('permiso', 'leer'))], summary="Obtener permisos", description="Obtiene una lista de permisos con filtros opcionales.")
async def obtenerPermisosApi(
    id: Optional[int] = Query(None, description="Filtrar permisos por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar permisos por nombre"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre

    result = await obtener_permisos(filtros=filtros)
    return {"message": result}


@router.get("/asignar_roles/{id_permiso}", summary="Asignar permiso a todos los roles", description="Crea los registros de permiso-rol necesarios para que un permiso quede asociado a todos los roles activos existentes.")
async def asignarPermisoARolesApi(id_permiso: int):
    result = await asignar_permiso_a_todos_roles(id_permiso)
    return {"message": result}
