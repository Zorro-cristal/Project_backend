from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.rol_request import (RolRequest,
                                                     RolUpdateRequest)

from ..services.rol_service import actualizar_rol, crear_rol, obtener_roles

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('rol', 'editar'))], summary="Actualizar rol", description="Actualiza un rol existente por su ID.")
async def actualizarRolApi(id: int, requestBody: RolUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_rol(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('rol', 'editar'))], summary="Actualizar rol parcialmente", description="Actualiza parcialmente un rol existente por su ID.")
async def patchRolApi(id: int, requestBody: RolUpdateRequest):
    return await actualizarRolApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('rol', 'crear'))], summary="Crear rol", description="Crea un nuevo rol.")
async def agregarRolApi(requestBody: RolRequest):
    payload = requestBody.model_dump()
    result = await crear_rol(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('rol', 'leer'))], summary="Obtener roles", description="Obtiene una lista de roles con filtros opcionales.")
async def obtenerRolesApi(
    id: Optional[str] = Query(None, description="Filtrar roles por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar roles por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar roles por estado (1 activo, 0 inactivo)"),
mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    # Por defecto ocultar inactivos (estado=0), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = 1

    result = await obtener_roles(filtros)
    return {"message": result}
