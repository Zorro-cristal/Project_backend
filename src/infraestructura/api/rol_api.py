from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.rol_service import (
    actualizar_rol,
    crear_rol,
    obtener_roles,
)
from src.shell.adapters.requests.rol_request import (
    RolRequest,
    RolUpdateRequest,
)

router = APIRouter()


@router.put("/{id}", summary="Actualizar rol", description="Actualiza un rol existente por su ID.")
async def actualizarRolApi(id: int, requestBody: RolUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_rol(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar rol parcialmente", description="Actualiza parcialmente un rol existente por su ID.")
async def patchRolApi(id: int, requestBody: RolUpdateRequest):
    return await actualizarRolApi(id, requestBody)


@router.post("/", summary="Crear rol", description="Crea un nuevo rol.")
async def agregarRolApi(requestBody: RolRequest):
    payload = requestBody.model_dump()
    result = await crear_rol(payload)
    return {"message": result}


@router.get("/", summary="Obtener roles", description="Obtiene una lista de roles con filtros opcionales.")
async def obtenerRolesApi(
    id: Optional[str] = Query(None, description="Filtrar roles por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar roles por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar roles por estado (1 activo, 0 inactivo)"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado

    result = await obtener_roles(filtros)
    return {"message": result}
