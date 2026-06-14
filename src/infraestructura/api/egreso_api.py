from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.shell.adapters.requests.egreso_request import (EgresoRequest,
                                                        EgresoUpdateRequest)

from ..services.egreso_service import (actualizar_egreso, crear_egreso,
                                       obtener_egreso_por_id,
                                       obtener_egreso_por_id_con_caja,
                                       obtener_egresos)

router = APIRouter()


@router.put("/{id}", summary="Actualizar egreso", description="Actualiza un egreso existente por su ID.")
async def actualizarEgresoApi(id: int, requestBody: EgresoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_egreso(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", summary="Actualizar egreso parcialmente", description="Actualiza parcialmente un egreso existente por su ID.")
async def patchEgresoApi(id: int, requestBody: EgresoUpdateRequest):
    return await actualizarEgresoApi(id, requestBody)


@router.post("/", summary="Crear egreso", description="Crea un nuevo egreso.")
async def agregarEgresoApi(requestBody: EgresoRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_egreso(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", summary="Obtener egresos", description="Obtiene una lista de egresos con filtros opcionales.")
async def obtenerEgresosApi(
    id: Optional[int] = Query(None, description="Filtrar egresos por ID"),
    monto: Optional[float] = Query(None, description="Filtrar egresos por monto"),
    descripcion: Optional[str] = Query(None, description="Filtrar egresos por descripción"),
    estado: Optional[int] = Query(None, description="Filtrar egresos por estado"),
    fecha: Optional[str] = Query(None, description="Filtrar egresos por fecha"),
    id_cajafk: Optional[int] = Query(None, description="Filtrar egresos por ID de caja")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if monto is not None:
        filtros["monto"] = monto
    if descripcion is not None:
        filtros["descripcion"] = descripcion
    if estado is not None:
        filtros["estado"] = estado
    if fecha is not None:
        filtros["fecha"] = fecha
    if id_cajafk is not None:
        filtros["id_cajafk"] = id_cajafk

    result = await obtener_egresos(filtros)

    return {"message": result}


@router.get("/{id}", summary="Obtener egreso por ID", description="Obtiene un egreso específico por su ID. Usa include=caja para incluir caja.")
async def obtenerEgresoPorIdApi(
    id: int,
    include: Optional[str] = Query(None, description="include=caja para incluir caja")
):
    filtros = {"id": id}

    if include == "caja":
        egreso = await obtener_egreso_por_id_con_caja(filtros)
    else:
        egreso = await obtener_egreso_por_id(filtros)

    if not egreso:
        return {"message": f"Egreso con ID {id} no encontrado"}

    return {"message": egreso}
