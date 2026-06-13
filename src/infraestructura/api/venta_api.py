from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.shell.adapters.requests.venta_request import (VentaRequest,
                                                       VentaUpdateRequest)

from ..services.venta_service import (actualizar_venta, crear_venta,
                                      obtener_detalle_venta_por_venta_id,
                                      obtener_venta_por_id_con_detalles,
                                      obtener_venta_por_id_sin_detalles,
                                      obtener_ventas)

router = APIRouter()


@router.put("/{id}", summary="Actualizar venta", description="Actualiza una venta existente por su ID.")
async def actualizarVentaApi(id: int, requestBody: VentaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_venta(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", summary="Actualizar venta parcialmente", description="Actualiza parcialmente una venta existente por su ID.")
async def patchVentaApi(id: int, requestBody: VentaUpdateRequest):
    return await actualizarVentaApi(id, requestBody)


@router.post("/", summary="Crear venta", description="Crea una nueva venta.")
async def agregarVentaApi(requestBody: VentaRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_venta(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", summary="Obtener ventas", description="Obtiene una lista de ventas con filtros opcionales.")
async def obtenerVentasApi(
    id: Optional[str] = Query(None, description="Filtrar ventas por ID"),
    nro: Optional[str] = Query(None, description="Filtrar ventas por número"),
    fecha: Optional[str] = Query(None, description="Filtrar ventas por fecha"),
    estado: Optional[int] = Query(None, description="Filtrar ventas por estado"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar ventas por ID de cliente"),
    id_localfk: Optional[int] = Query(None, description="Filtrar ventas por ID de local"),
    id_cajafk: Optional[int] = Query(None, description="Filtrar ventas por ID de caja")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nro is not None:
        filtros["nro"] = nro
    if fecha is not None:
        filtros["fecha"] = fecha
    if estado is not None:
        filtros["estado"] = estado
    if id_clientefk is not None:
        filtros["id_clientefk"] = id_clientefk
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk
    if id_cajafk is not None:
        filtros["id_cajafk"] = id_cajafk

    result = await obtener_ventas(filtros)

    return {"message": result}


@router.get("/{id}", summary="Obtener venta por ID", description="Obtiene una venta específica por su ID. Usa include=detalleVenta para incluir detalles.")
async def obtenerVentaPorIdApi(
    id: int,
    include: Optional[str] = Query(None, description="include=detalleVenta para incluir detalle_venta")
):
    filtros = {"id": id}

    if include == "detalleVenta":
        venta = await obtener_venta_por_id_con_detalles(filtros)
    else:
        venta = await obtener_venta_por_id_sin_detalles(filtros)

    if not venta:
        return {"message": f"Venta con ID {id} no encontrada"}

    return {"message": venta}



@router.get("/{id}/detalleVenta", summary="Obtener detalles de venta", description="Obtiene solo el detalle_venta asociado a una venta.")
async def obtenerDetalleVentaPorVentaIdApi(id: int):
    filtros = {"id_ventafk": id}
    result = await obtener_detalle_venta_por_venta_id(filtros)
    return {"message": result if result else []}



