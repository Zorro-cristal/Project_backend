from typing import Optional

from fastapi import APIRouter, Query

from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)

from ..services.local_service import (actualizar_local, crear_local,
                                      obtener_locales)

router = APIRouter()


@router.put("/{id}", summary="Actualizar local", description="Actualiza un local existente por su ID.")
async def actualizarLocalApi(id: int, requestBody: LocalUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_local(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar local parcialmente", description="Actualiza parcialmente un local existente por su ID.")
async def patchLocalApi(id: int, requestBody: LocalUpdateRequest):
    return await actualizarLocalApi(id, requestBody)


@router.post("/", summary="Crear local", description="Crea un nuevo local.")
async def agregarLocalApi(requestBody: LocalRequest):
    payload = requestBody.model_dump()
    result = await crear_local(payload)
    return {"message": result}


@router.get("/", summary="Obtener locales", description="Obtiene una lista de locales con filtros opcionales.")
async def obtenerLocalesApi(
    id: Optional[str] = Query(None, description="Filtrar locales por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar locales por nombre parcial"),
    estado: Optional[bool] = Query(None, description="Filtrar locales por estado (true activo, false inactivo)"),
    direccion: Optional[str] = Query(None, description="Filtrar locales por dirección"),
    telefono: Optional[str] = Query(None, description="Filtrar locales por teléfono")
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

    result = await obtener_locales(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener local por ID", description="Obtiene un local específico por su ID.")
async def obtenerLocalPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_locales(filtros)
    if not result:
        return {"message": f"Local con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
