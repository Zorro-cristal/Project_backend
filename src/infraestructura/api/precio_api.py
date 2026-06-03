from typing import Optional

from fastapi import APIRouter, Query

from src.shell.adapters.requests.precio_request import (PrecioRequest,
                                                        PrecioUpdateRequest)

from ..services.precio_service import (actualizar_precio, crear_precio,
                                       obtener_precios)

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

    # Relación indirecta: precios -> detalles_precio -> detalles_producto -> productos.
    # La tabla intermedia que mapea productos es `detalles_producto` (por `detalles_precio.detalles_producto_cod`).
    # Nota: el FK directo en bdd.sql es detalles_precio -> precios, detalles_precio -> productos(vía id_productofk),
    # y detalles_precio -> detalles_producto.
    # Este select intenta traer el producto a través de los datos del detalle.
    result = await obtener_precios(
        filtros=filtros,
        columnas='*, detalles_precio(*, detalles_producto(*, productos(*)))'
    )
    return {"message": result}
