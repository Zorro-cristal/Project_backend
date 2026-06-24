from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)

from ..services.local_service import (actualizar_local, crear_local,
                                      obtener_locales)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('local', 'editar'))], summary="Actualizar local", description="Actualiza un local existente por su ID.")
async def actualizarLocalApi(id: int, requestBody: LocalUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_local(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('local', 'editar'))], summary="Actualizar local parcialmente", description="Actualiza parcialmente un local existente por su ID.")
async def patchLocalApi(id: int, requestBody: LocalUpdateRequest):
    return await actualizarLocalApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('local', 'crear'))], summary="Crear local", description="Crea un nuevo local.")
async def agregarLocalApi(requestBody: LocalRequest):
    payload = requestBody.model_dump()
    result = await crear_local(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('local', 'leer'))], summary="Obtener locales", description="Obtiene una lista de locales con filtros opcionales.")
async def obtenerLocalesApi(
    id: Optional[str] = Query(None, description="Filtrar locales por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar locales por nombre parcial"),
    estado: Optional[bool] = Query(None, description="Filtrar locales por estado (true activo, false inactivo)"),
    direccion: Optional[str] = Query(None, description="Filtrar locales por dirección"),
    telefono: Optional[str] = Query(None, description="Filtrar locales por teléfono"),
mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=false). Por defecto solo muestra activos"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    if direccion is not None:
        filtros["direccion"] = direccion
    if telefono is not None:
        filtros["telefono"] = telefono
    # Por defecto ocultar inactivos (estado=false), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = True

    result = await obtener_locales(filtros)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('local', 'leer'))], summary="Obtener local por ID", description="Obtiene un local específico por su ID.")
async def obtenerLocalPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_locales(filtros)
    if not result:
        return {"message": f"Local con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
