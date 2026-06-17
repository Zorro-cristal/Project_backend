from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.detalle_compra_request import (
    DetalleCompraRequest, DetalleCompraUpdateRequest)

from ..services.detalle_compra_service import (actualizar_detalle_compra,
                                               crear_detalle_compra,
                                               obtener_detalle_compras)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('detallecompra', 'editar'))], summary="Actualizar detalle de compra", description="Actualiza un detalle de compra existente por su ID.")
async def actualizarDetalleCompraApi(id: int, requestBody: DetalleCompraUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_detalle_compra(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('detallecompra', 'editar'))], summary="Actualizar detalle de compra parcialmente", description="Actualiza parcialmente un detalle de compra existente por su ID.")
async def patchDetalleCompraApi(id: int, requestBody: DetalleCompraUpdateRequest):
    return await actualizarDetalleCompraApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('detallecompra', 'crear'))], summary="Crear detalle de compra", description="Crea un nuevo detalle de compra.")
async def agregarDetalleCompraApi(requestBody: DetalleCompraRequest):
    payload = requestBody.model_dump()
    result = await crear_detalle_compra(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('detallecompra', 'leer'))], summary="Obtener detalles de compra", description="Obtiene una lista de detalles de compra con filtros opcionales.")
async def obtenerDetalleComprasApi(
    id: Optional[int] = Query(None, description="Filtrar detalles de compra por ID"),
    id_comprafk: Optional[int] = Query(None, description="Filtrar detalles por ID de compra"),
    id_productofk: Optional[int] = Query(None, description="Filtrar detalles por ID de producto")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_comprafk is not None:
        filtros["id_comprafk"] = id_comprafk
    if id_productofk is not None:
        filtros["id_productofk"] = id_productofk

    result = await obtener_detalle_compras(filtros)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('detallecompra', 'leer'))], summary="Obtener detalle de compra por ID", description="Obtiene un detalle de compra específico por su ID.")
async def obtenerDetalleCompraPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_detalle_compras(filtros)
    if not result:
        return {"message": f"Detalle de compra con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}


@router.get("/compra/{id_compra}/detalles", dependencies=[Depends(permiso_requerido('detallecompra', 'leer'))], summary="Obtener subproductos de compra", description="Obtiene solo los detalles de compra (detalle_compra) asociados a una compra.")
async def obtenerDetallesCompraApi(id_compra: int):
    filtros = {"id_comprafk": id_compra}
    result = await obtener_detalle_compras(filtros)
    return {"message": result}

