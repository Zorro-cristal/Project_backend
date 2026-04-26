from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.infraestructura.logica.producto import (actualizar_producto,
                                                 crear_producto,
                                                 obtener_productos)
from src.shell.adaptadores.requests.ProductoRequest import (
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
    categoria_id: Optional[int] = Query(None, description="Filtrar productos por ID de categoría"),
    marca_id: Optional[int] = Query(None, description="Filtrar productos por ID de marca"),
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
    if categoria_id is not None:
        filtros["categoria_id"] = categoria_id
    if marca_id is not None:
        filtros["marca_id"] = marca_id
    if pesable is not None:
        filtros["pesable"] = pesable
    if perecedero is not None:
        filtros["perecedero"] = perecedero

    result = await obtener_productos(filtros, '*, marcas(marca_id:id, marca_nombre:nombre, marca_estado:estado)')