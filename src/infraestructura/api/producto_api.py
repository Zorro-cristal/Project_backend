from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.producto_service import (
    actualizar_producto, crear_producto, obtener_detallesProducto,
    obtener_producto, obtener_productos)
from src.shell.adapters.requests.producto_request import (
    ProductoRequest, ProductoUpdateRequest)

router = APIRouter()


@router.put("/{id}", summary="Actualizar producto", description="Actualiza un producto existente por su ID.")
async def actualizarProductoApi(id: int, requestBody: ProductoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_producto(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar producto parcialmente", description="Actualiza parcialmente un producto existente por su ID.")
async def patchProductoApi(id: int, requestBody: ProductoUpdateRequest):
    return await actualizarProductoApi(id, requestBody)

@router.post("/", summary="Crear producto", description="Crea un nuevo producto.")
async def agregarProductoApi(requestBody: ProductoRequest):
    payload = requestBody.model_dump()
    result = await crear_producto(payload)
    return {"message": result}

@router.get("/", summary="Obtener productos", description="Obtiene una lista de productos con filtros opcionales.")
async def obtenerProductosApi(
    id: Optional[str] = Query(None, description="Filtrar productos por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar productos por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar productos por estado (1 para activo, 0 para inactivo)"),
    id_categoriafk: Optional[int] = Query(None, description="Filtrar productos por ID de categoría"),
    id_marcafk: Optional[int] = Query(None, description="Filtrar productos por ID de marca"),
    pesable: Optional[bool] = Query(None, description="Filtrar productos que son pesables"),
    perecedero: Optional[bool] = Query(None, description="Filtrar productos que son perecederos"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    if id_categoriafk is not None:
        filtros["id_categoriafk"] = id_categoriafk
    if id_marcafk is not None:
        filtros["id_marcafk"] = id_marcafk
    if pesable is not None:
        filtros["pesable"] = pesable
    if perecedero is not None:
        filtros["perecedero"] = perecedero

    result = await obtener_productos(filtros, '*, marcas(id_marcafk:id, marca_nombre:nombre, marca_estado:estado)')
    return {"message": result}


@router.get("/{id}", summary="Obtener producto", description="Obtiene un producto por su ID.")
async def obtenerProductoApi(
    id: int,
    include: Optional[str] = Query(None, description="Incluye datos adicionales. Soporta: detallesProducto"),
):
    if include == "detallesProducto":
        result = await obtener_producto(id, include_detallesProducto=True)
    else:
        result = await obtener_producto(id, include_detallesProducto=False)
    return {"message": result}


@router.get("/{id}/detallesProducto", summary="Obtener detallesProducto", description="Obtiene solo los detallesProducto (detalles_producto) de un producto.")
async def obtenerDetallesProductoApi(id: int):
    result = await obtener_detallesProducto(id)
    return {"message": result}

