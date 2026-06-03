from typing import Optional

from fastapi import APIRouter, Query

from ..services.stock_service import (
    crear_stock,
    actualizar_stock,
    obtener_stocks,
)
from src.shell.adapters.requests.stock_request import (StockRequest,
                                                       StockUpdateRequest)

router = APIRouter()


@router.put("/{id}", summary="Actualizar stock", description="Actualiza un stock existente por su ID.")
async def actualizarStockApi(id: int, requestBody: StockUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_stock(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar stock parcialmente", description="Actualiza parcialmente un stock existente por su ID.")
async def patchStockApi(id: int, requestBody: StockUpdateRequest):
    return await actualizarStockApi(id, requestBody)


@router.post("/", summary="Crear stock", description="Crea un nuevo stock.")
async def agregarStockApi(requestBody: StockRequest):
    payload = requestBody.model_dump()
    result = await crear_stock(payload)
    return {"message": result}


@router.get("/", summary="Obtener stocks", description="Obtiene una lista de stocks con filtros opcionales.")
async def obtenerStocksApi(
    id: Optional[str] = Query(None, description="Filtrar stocks por ID"),
    id_localfk: Optional[int] = Query(None, description="Filtrar stocks por ID de local asociada"),
    id_detalleproductofk: Optional[int] = Query(None, description="Filtrar stocks por ID de detalle de producto"),
    lote: Optional[str] = Query(None, description="Filtrar stocks por lote"),
    fecha_vencimiento: Optional[str] = Query(None, description="Filtrar stocks por fecha de vencimiento")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_localfk is not None:
        filtros["id_localfk"] = id_localfk
    if id_detalleproductofk is not None:
        filtros["id_detalleproductofk"] = id_detalleproductofk
    if lote is not None:
        filtros["lote"] = lote
    if fecha_vencimiento is not None:
        filtros["fecha_vencimiento"] = fecha_vencimiento

    result = await obtener_stocks(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener stock por ID", description="Obtiene un stock específico por su ID.")
async def obtenerStockPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_stocks(filtros)
    if not result:
        return {"message": f"Stock con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
