from typing import Optional

from fastapi import APIRouter, Query

from ..services.compra_service import (
    crear_compra,
    actualizar_compra,
    obtener_compra_solo,
    obtener_compras,
)
from src.shell.adapters.requests.compra_request import (CompraRequest,
                                                        CompraUpdateRequest)
from src.shell.flujo.compra.consultarCompra import obtener_compra_con_detalles

router = APIRouter()


@router.put("/{id}", summary="Actualizar compra", description="Actualiza una compra existente por su ID.")
async def actualizarCompraApi(id: int, requestBody: CompraUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_compra(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar compra parcialmente", description="Actualiza parcialmente una compra existente por su ID.")
async def patchCompraApi(id: int, requestBody: CompraUpdateRequest):
    return await actualizarCompraApi(id, requestBody)


@router.post("/", summary="Crear compra", description="Crea una nueva compra.")
async def agregarCompraApi(requestBody: CompraRequest):
    payload = requestBody.model_dump()
    result = await crear_compra(payload)
    return {"message": result}


@router.get("/", summary="Obtener compras", description="Obtiene una lista de compras con filtros opcionales.")
async def obtenerComprasApi(
    id: Optional[int] = Query(None, description="Filtrar compras por ID"),
    nro: Optional[str] = Query(None, description="Filtrar compras por número"),
    id_localfk: Optional[int] = Query(None, description="Filtrar compras por ID de local"),
    id_clientefk: Optional[int] = Query(None, description="Filtrar compras por ID de cliente"),
    id_proveedorfk: Optional[int] = Query(None, description="Filtrar compras por ID de proveedor"),
    estado: Optional[int] = Query(None, description="Filtrar compras por estado")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nro is not None:
        filtros["nro"] = nro
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk
    if id_clientefk is not None:
        filtros["id_clientefk"] = id_clientefk
    if id_proveedorfk is not None:
        filtros["id_proveedorfk"] = id_proveedorfk
    if estado is not None:
        filtros["estado"] = estado

    result = await obtener_compras(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener compra por ID", description="Obtiene una compra específica por su ID.")
async def obtenerCompraPorIdApi(
    id: int,
    include: Optional[str] = Query(None, description="Incluye datos adicionales. Soporta: detalleCompra"),
):
    if include == "detalleCompra":
        result = await obtener_compra_con_detalles(id)
    else:
        result = await obtener_compra_solo(id)

    if not result:
        return {"message": f"Compra con ID {id} no encontrada"}
    return {"message": result}


@router.get("/{id}/detalleCompra", summary="Obtener detalles de compra", description="Obtiene solo los detalle_compra asociados a una compra.")
async def obtenerDetalleCompraPorIdApi(id: int):
    result = await obtener_compra_con_detalles(id, solo_detalles=True)
    return {"message": result}


