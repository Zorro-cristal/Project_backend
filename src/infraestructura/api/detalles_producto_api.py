from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.detalles_producto_request import (
    DetalleProductoRequest, DetalleProductoUpdateRequest)

from ..services.detalles_producto_service import (actualizar_detalles_producto,
                                                  crear_detalles_producto,
                                                  obtener_detalles_productos)

router = APIRouter()

@router.put("/{cod_barra}", dependencies=[Depends(permiso_requerido('detallesproducto', 'editar'))], summary="Actualizar detalle de producto", description="Actualiza un detalle de producto existente por su código de barra.")
async def actualizarDetalleProductoApi(cod_barra: int, requestBody: DetalleProductoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_detalles_producto(cod_barra, payload)
    return {"message": result}

@router.patch("/{cod_barra}", dependencies=[Depends(permiso_requerido('detallesproducto', 'editar'))], summary="Actualizar detalle de producto parcialmente", description="Actualiza parcialmente un detalle de producto existente por su código de barra.")
async def patchDetalleProductoApi(cod_barra: int, requestBody: DetalleProductoUpdateRequest):
    return await actualizarDetalleProductoApi(cod_barra, requestBody)

@router.post("/", dependencies=[Depends(permiso_requerido('detallesproducto', 'crear'))], summary="Crear detalle de producto", description="Crea un nuevo detalle de producto.")
async def agregarDetalleProductoApi(requestBody: DetalleProductoRequest):
    payload = requestBody.model_dump()
    result = await crear_detalles_producto(payload)
    return {"message": result}

@router.get("/{cod_barra}", dependencies=[Depends(permiso_requerido('detallesproducto', 'leer'))], summary="Obtener detalle de producto por código de barra", description="Obtiene el detalle de producto asociado a un código de barra e incluye producto y precios.")
async def obtenerDetalleProductoPorCodBarraApi(cod_barra: str):
    result = await obtener_detalles_productos(
        filtros={"cod_barra": cod_barra},
        include_producto=True,
        include_precios=True,
        filtros_producto=None
    )
    return {"message": result}

@router.get("/", dependencies=[Depends(permiso_requerido('detallesproducto', 'leer'))], summary="Obtener detalles de productos", description="Obtiene una lista de detalles de productos con filtros opcionales.")
async def obtenerDetallesProductosApi(
    q: Optional[str] = Query(None, description="Buscar en nombre de producto (contiene)"),
    es_comida: Optional[bool] = Query(None, description="Filtrar productos por es_comida=true/false"),
    id: Optional[str] = Query(None, description="Filtrar detalles de productos por ID"),
    color: Optional[str] = Query(None, description="Filtrar detalles de productos por color"),
    tamanho: Optional[int] = Query(None, description="Filtrar detalles de productos por tamaño"),
    cod_barra: Optional[int] = Query(None, description="Filtrar detalles de productos por código de barra"),
    unidad_por_lote: Optional[int] = Query(None, description="Filtrar detalles de productos por unidades por lote"),
    include: Optional[str] = Query(None, description="include=producto para incluir datos del producto, include=precios para incluir precios asociados")
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
    
    # Nuevo: filtros por producto
    filtros_producto = {}
    if q is not None:
        filtros_producto["q"] = q
    if es_comida is not None:
        filtros_producto["es_comida"] = es_comida
    
    # Determinar qué inclusiones solicitar
    include_producto = include == "producto" or (include and "producto" in include)
    include_precios = include == "precios" or (include and "precios" in include)
    
    result = await obtener_detalles_productos(
        filtros, 
        include_producto=include_producto,
        include_precios=include_precios,
        filtros_producto=filtros_producto
    )
    return {"message": result}
