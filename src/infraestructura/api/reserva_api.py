from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.shell.adapters.requests.reserva_request import (ReservaRequest,
                                                         ReservaUpdateRequest)

from ..services.reserva_service import (actualizar_reserva, crear_reserva,
                                        obtener_reservas)

router = APIRouter()


@router.put("/{id}", summary="Actualizar reserva", description="Actualiza una reserva existente por su ID.")
async def actualizarReservaApi(id: int, requestBody: ReservaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_reserva(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", summary="Actualizar reserva parcialmente", description="Actualiza parcialmente una reserva existente por su ID.")
async def patchReservaApi(id: int, requestBody: ReservaUpdateRequest):
    return await actualizarReservaApi(id, requestBody)


@router.post("/", summary="Crear reserva", description="Crea una nueva reserva.")
async def agregarReservaApi(requestBody: ReservaRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_reserva(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", summary="Obtener reservas", description="Obtiene una lista de reservas con filtros opcionales.")
async def obtenerReservasApi(
    id: Optional[int] = Query(None, description="Filtrar reservas por ID"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar por ID de cliente"),
    fecha_reserva: Optional[str] = Query(None, description="Filtrar por fecha de reserva (string)"),
):
    filtros = {}
    if id is not None:
        filtros['id'] = id
    if estado is not None:
        filtros['estado'] = estado
    if id_clientefk is not None:
        filtros['id_clientefk'] = id_clientefk
    if fecha_reserva is not None:
        filtros['fecha_reserva'] = fecha_reserva

    result = await obtener_reservas(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener reserva por ID", description="Obtiene una reserva específica por su ID.")
async def obtenerReservaPorIdApi(id: int):
    filtros = {'id': id}
    result = await obtener_reservas(filtros)
    if not result:
        return {"message": f"Reserva con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}

