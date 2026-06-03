from typing import Optional

from fastapi import APIRouter, Query

from ..services.detalles_producto_service import (
    actualizar_detalles_producto, crear_detalles_producto,
    obtener_detalles_productos)
from src.shell.adapters.requests.detalles_producto_request import (
    DetalleProductoRequest, DetalleProductoUpdateRequest)

router = APIRouter()

@router.put("/{cod_barra}", summary="Actualizar detalle de producto", description="Actualiza un detalle de producto existente por su código de barra.")
async def actualizarDetalleProductoApi(cod_barra: int, requestBody: DetalleProductoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_detalles_producto(cod_barra, payload)
    return {"message": result}

@router.patch("/{cod_barra}", summary="Actualizar detalle de producto parcialmente", description="Actualiza parcialmente un detalle de producto existente por su código de barra.")
async def patchDetalleProductoApi(cod_barra: int, requestBody: DetalleProductoUpdateRequest):
    return await actualizarDetalleProductoApi(cod_barra, requestBody)

@router.post("/", summary="Crear detalle de producto", description="Crea un nuevo detalle de producto.")
async def agregarDetalleProductoApi(requestBody: DetalleProductoRequest):
    payload = requestBody.model_dump()
    result = await crear_detalles_producto(payload)
    return {"message": result}

@router.get("/", summary="Obtener detalles de productos", description="Obtiene una lista de detalles de productos con filtros opcionales.")
async def obtenerDetallesProductosApi(
    id: Optional[str] = Query(None, description="Filtrar detalles de productos por ID"),
    color: Optional[str] = Query(None, description="Filtrar detalles de productos por color"),
    tamanho: Optional[int] = Query(None, description="Filtrar detalles de productos por tamaño"),
    cod_barra: Optional[int] = Query(None, description="Filtrar detalles de productos por código de barra"),
    unidad_por_lote: Optional[int] = Query(None, description="Filtrar detalles de productos por unidades por lote")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if color is not None:
        filtros["color"] = color
    if tamanho is not None:
        filtros["tamanho"] = tamanho
    if cod_barra is not None:
        filtros["cod_barra"] = cod_barra
    if unidad_por_lote is not None:
        filtros["unidad_por_lote"] = unidad_por_lote
    
    result = await obtener_detalles_productos(filtros)
    return {"message": result}
