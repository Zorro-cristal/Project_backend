from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.reserva_request import (ReservaRequest,
                                                         ReservaUpdateRequest)

from ..services.reserva_service import (actualizar_reserva, crear_reserva,
                                        obtener_reservas)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('reserva', 'editar'))], summary="Actualizar reserva", description="Actualiza una reserva existente por su ID.")
async def actualizarReservaApi(id: int, requestBody: ReservaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_reserva(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}

@router.patch("/{id}", dependencies=[Depends(permiso_requerido('reserva', 'editar'))], summary="Actualizar reserva parcialmente", description="Actualiza parcialmente una reserva existente por su ID.")
async def patchReservaApi(id: int, requestBody: ReservaUpdateRequest):
    return await actualizarReservaApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('reserva', 'crear'))], summary="Crear reserva", description="Crea una nueva reserva.")
async def agregarReservaApi(requestBody: ReservaRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_reserva(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('reserva', 'leer'))], summary="Obtener reservas", description="Obtiene una lista de reservas con filtros opcionales.")
async def obtenerReservasApi(
    id: Optional[int] = Query(None, description="Filtrar reservas por ID"),
    estado: Optional[int] = Query(None, description="Filtrar por estado"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar por ID de cliente"),
    fecha_reserva: Optional[str] = Query(None, description="Filtrar por fecha de reserva (string)"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    filtros = {}
    if id is not None:
        filtros['id'] = id
    if estado is not None:
        filtros['estado'] = estado
    if id_clientefk is not None:
        filtros['id_clientefk'] = id_clientefk
    # Si viene como YYYY-MM-DD aplicamos rango de día completo.
    # Si viene como timestamp completo, cae al filtro exacto.
    if fecha_reserva is not None:
        fecha_reserva = fecha_reserva.strip()
        if len(fecha_reserva) == 10 and fecha_reserva[4] == '-' and fecha_reserva[7] == '-':
            # gte/lt para capturar cualquier hora en esa fecha (UTC o la zona de BD)
            filtros['fecha_reserva_inicio'] = f"{fecha_reserva}T00:00:00+00:00"
            filtros['fecha_reserva_fin'] = f"{fecha_reserva}T23:59:59.999+00:00"
        else:
            filtros['fecha_reserva'] = fecha_reserva


    result = await obtener_reservas(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('reserva', 'leer'))], summary="Obtener reserva por ID", description="Obtiene una reserva específica por su ID.")
async def obtenerReservaPorIdApi(id: int):
    filtros = {'id': id}
    result = await obtener_reservas(filtros)
    if not result:
        return {"message": f"Reserva con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}

