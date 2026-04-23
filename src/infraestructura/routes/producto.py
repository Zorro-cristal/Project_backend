from fastapi import APIRouter, HTTPException
from src.shell.adaptadores.requests.ProductoRequest import ProductoRequest, ProductoUpdateRequest
from src.infraestructura.logica.producto import (actualizar_producto, crear_producto, obtener_productos)

router = APIRouter()

@router.put("/{id}")
async def actualizarProductoApi(id: int, requestBody: ProductoUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_producto(id, payload)
    return {"message": result}

@router.patch("/{id}")
async def patchProductoApi(id: int, requestBody: ProductoUpdateRequest):
    return await actualizarProductoApi(id, requestBody)

@router.post("/")
async def agregarProductoApi(requestBody: ProductoRequest):
    payload = requestBody.model_dump()
    result = await crear_producto(payload)
    return {"message": result}

@router.get("/")
async def obtenerProductosApi():
    result = await obtener_productos()
    return {"message": result}
