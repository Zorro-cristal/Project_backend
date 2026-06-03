from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.shell.adapters.requests.mesa_request import (MesaRequest,
                                                      MesaUpdateRequest)

from ..services.mesa_service import actualizar_mesa, crear_mesa, obtener_mesas

router = APIRouter()


@router.put("/{id}", summary="Actualizar mesa", description="Actualiza una mesa existente por su ID.")
async def actualizarMesaApi(id: int, requestBody: MesaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_mesa(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", summary="Actualizar mesa parcialmente", description="Actualiza parcialmente una mesa existente por su ID.")
async def patchMesaApi(id: int, requestBody: MesaUpdateRequest):
    return await actualizarMesaApi(id, requestBody)


@router.post("/", summary="Crear mesa", description="Crea una nueva mesa.")
async def agregarMesaApi(requestBody: MesaRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_mesa(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", summary="Obtener mesas", description="Obtiene una lista de mesas con filtros opcionales.")
async def obtenerMesasApi(
    id: Optional[str] = Query(None, description="Filtrar mesas por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar mesas por nombre parcial"),
    estado: Optional[bool] = Query(None, description="Filtrar mesas por estado (true activo, false inactivo)"),
    id_localfk: Optional[int] = Query(None, description="Filtrar mesas por ID de local asociada")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk

    result = await obtener_mesas(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener mesa por ID", description="Obtiene una mesa específica por su ID.")
async def obtenerMesaPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_mesas(filtros)
    if not result:
        return {"message": f"Mesa con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}
