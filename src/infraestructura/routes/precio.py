from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.logica.precio import (actualizar_precio, crear_precio,
                                               obtener_precios)
from src.shell.adaptadores.requests.PrecioRequest import (PrecioRequest,
                                                          PrecioUpdateRequest)

router = APIRouter()

@router.put("/{id}", summary="Actualizar precio", description="Actualiza un precio existente por su ID.")
async def actualizarPrecioApi(id: int, requestBody: PrecioUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_precio(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar precio parcialmente", description="Actualiza parcialmente un precio existente por su ID.")
async def patchPrecioApi(id: int, requestBody: PrecioUpdateRequest):
    return await actualizarPrecioApi(id, requestBody)

@router.post("/", summary="Crear precio", description="Crea un nuevo precio.")
async def agregarPrecioApi(requestBody: PrecioRequest):
    payload = requestBody.model_dump()
    result = await crear_precio(payload)
    return {"message": result}

@router.get("/", summary="Obtener precios", description="Obtiene una lista de precios con filtros opcionales.")
async def obtenerPreciosApi(
    id: Optional[str] = Query(None, description="Filtrar precios por ID"),
    producto_id: Optional[int] = Query(None, description="Filtrar precios por ID de producto"),
    valido_desde: Optional[str] = Query(None, description="Filtrar precios válidos desde una fecha de inicio"),
    valido_hasta: Optional[str] = Query(None, description="Filtrar precios válidos hasta una fecha de fin")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if producto_id is not None:
        filtros["producto_id"] = producto_id
    if valido_desde is not None:
        filtros["valido_desde"] = valido_desde
    if valido_hasta is not None:
        filtros["valido_hasta"] = valido_hasta

    result = await obtener_precios(filtros=filtros, columnas='*, productos(producto_id:id, producto_nombre:nombre)')
    return {"message": result}