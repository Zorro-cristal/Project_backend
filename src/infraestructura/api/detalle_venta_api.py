from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.detalle_venta_request import (
    DetalleVentaRequest, DetalleVentaUpdateRequest)

from ..services.detalle_venta_service import (actualizar_detalle_venta,
                                              crear_detalle_venta,
                                              obtener_detalle_ventas)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('detalleventa', 'editar'))], summary="Actualizar detalle de venta", description="Actualiza un detalle de venta existente por su ID.")
async def actualizarDetalleVentaApi(id: int, requestBody: DetalleVentaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_detalle_venta(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('detalleventa', 'editar'))], summary="Actualizar detalle de venta parcialmente", description="Actualiza parcialmente un detalle de venta existente por su ID.")
async def patchDetalleVentaApi(id: int, requestBody: DetalleVentaUpdateRequest):
    return await actualizarDetalleVentaApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('detalleventa', 'crear'))], summary="Crear detalle de venta", description="Crea un nuevo detalle de venta.")
async def agregarDetalleVentaApi(requestBody: DetalleVentaRequest):
    payload = requestBody.model_dump()
    result = await crear_detalle_venta(payload)
    return {"message": result}

@router.get("/", dependencies=[Depends(permiso_requerido('detalleventa', 'leer'))], summary="Obtener detalles de venta", description="Obtiene una lista de detalles de venta con filtros opcionales.")
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


@router.get("/{id}", dependencies=[Depends(permiso_requerido('detalleventa', 'leer'))], summary="Obtener detalle de venta por ID", description="Obtiene un detalle de venta específico por su ID.")
async def obtenerDetalleVentaPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_detalle_ventas(filtros)
    if not result:
        return {"message": f"Detalle de venta con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
