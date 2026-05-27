from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.permiso_service import (
    actualizar_permiso,
    crear_permiso,
    obtener_permisos,
)
from src.shell.adapters.requests.permiso_request import (
    PermisoRequest,
    PermisoUpdateRequest,
)

router = APIRouter()

@router.put("/{id}", summary="Actualizar permiso", description="Actualiza un permiso existente por su ID.")
async def actualizarPermisoApi(id: int, requestBody: PermisoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_permiso(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar permiso parcialmente", description="Actualiza parcialmente un permiso existente por su ID.")
async def patchPermisoApi(id: int, requestBody: PermisoUpdateRequest):
    return await actualizarPermisoApi(id, requestBody)

@router.post("/", summary="Crear permiso", description="Crea un nuevo permiso.")
async def agregarPermisoApi(requestBody: PermisoRequest):
    payload = requestBody.model_dump()
    result = await crear_permiso(payload)
    return {"message": result}

@router.get("/", summary="Obtener permisos", description="Obtiene una lista de permisos con filtros opcionales.")
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
