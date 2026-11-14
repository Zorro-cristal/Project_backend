from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.stock_request import (StockRequest,
                                                       StockUpdateRequest)

from ..services.stock_service import (actualizar_stock, crear_stock,
                                      obtener_stocks)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('Stocks', 'editar'))], summary="Actualizar stock", description="Actualiza un stock existente por su ID.")
async def actualizarStockApi(id: int, requestBody: StockUpdateRequest, current_user: dict = Depends(permiso_requerido('Stocks', 'editar'))):
    payload = requestBody.model_dump(exclude_unset=True)
    
    # Propagar el actor autenticado antes de persistir
    actor_id = current_user.get("id")
    if actor_id is None:
        raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
    payload["actualizado_por"] = actor_id
    
    result = await actualizar_stock(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('Stocks', 'editar'))], summary="Actualizar stock parcialmente", description="Actualiza parcialmente un stock existente por su ID.")
async def patchStockApi(id: int, requestBody: StockUpdateRequest, current_user: dict = Depends(permiso_requerido('Stocks', 'editar'))):
    return await actualizarStockApi(id, requestBody, current_user)


@router.post("/", dependencies=[Depends(permiso_requerido('Stocks', 'crear'))], summary="Crear stock", description="Crea un nuevo stock.")
async def agregarStockApi(requestBody: StockRequest, current_user: dict = Depends(permiso_requerido('Stocks', 'crear'))):
    payload = requestBody.model_dump()
    
    # Propagar el actor autenticado antes de persistir
    actor_id = current_user.get("id")
    if actor_id is None:
        raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
    payload["actualizado_por"] = actor_id
    
    result = await crear_stock(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('Stocks', 'leer'))], summary="Obtener stocks", description="Obtiene una lista de stocks con filtros opcionales.")
async def obtenerStocksApi(
    id: Optional[str] = Query(None, description="Filtrar stocks por ID"),
    id_localfk: Optional[int] = Query(None, description="Filtrar stocks por ID de local asociada"),
    id_detalleproductofk: Optional[int] = Query(None, description="Filtrar stocks por ID de detalle de producto"),
    lote: Optional[str] = Query(None, description="Filtrar stocks por lote"),
    fecha_vencimiento: Optional[str] = Query(None, description="Filtrar stocks por fecha de vencimiento"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
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

    result = await obtener_stocks(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('Stocks', 'leer'))], summary="Obtener stock por ID", description="Obtiene un stock específico por su ID.")
async def obtenerStockPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_stocks(filtros)
    if not result:
        return {"message": f"Stock con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
