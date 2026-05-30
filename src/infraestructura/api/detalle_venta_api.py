from typing import Optional

from fastapi import APIRouter, Query

from src.shell.flujo.detalle_venta.crearActualizarDetalleVenta import (
    actualizar_detalle_venta_por_id,
    crear_o_actualizar_detalle_venta,
)
from src.infraestructura.services.detalle_venta_service import obtener_detalle_ventas
from src.shell.adapters.requests.detalle_venta_request import (
    DetalleVentaRequest,
    DetalleVentaUpdateRequest,
)

router = APIRouter()


@router.put("/{id}", summary="Actualizar detalle de venta", description="Actualiza un detalle de venta existente por su ID.")
async def actualizarDetalleVentaApi(id: int, requestBody: DetalleVentaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_detalle_venta_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar detalle de venta parcialmente", description="Actualiza parcialmente un detalle de venta existente por su ID.")
async def patchDetalleVentaApi(id: int, requestBody: DetalleVentaUpdateRequest):
    return await actualizarDetalleVentaApi(id, requestBody)


@router.post("/", summary="Crear detalle de venta", description="Crea un nuevo detalle de venta.")
async def agregarDetalleVentaApi(requestBody: DetalleVentaRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_detalle_venta(payload)
    return {"message": result}


@router.get("/", summary="Obtener detalles de venta", description="Obtiene una lista de detalles de venta con filtros opcionales.")
async def obtenerDetalleVentasApi(
    id: Optional[int] = Query(None, description="Filtrar detalles de venta por ID"),
    id_productofk: Optional[int] = Query(None, description="Filtrar detalles por ID de producto"),
    id_ventafk: Optional[int] = Query(None, description="Filtrar detalles por ID de venta")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_productofk is not None:
        filtros["id_productofk"] = id_productofk
    if id_ventafk is not None:
        filtros["id_ventafk"] = id_ventafk

    result = await obtener_detalle_ventas(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener detalle de venta por ID", description="Obtiene un detalle de venta específico por su ID.")
async def obtenerDetalleVentaPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_detalle_ventas(filtros)
    if not result:
        return {"message": f"Detalle de venta con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
