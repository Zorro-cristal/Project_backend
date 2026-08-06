from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.orden_request import (OrdenRequest,
                                                       OrdenUpdateRequest)

from ..services.orden_service import (actualizar_orden_por_id, crear_orden,
                                      obtener_ordenes)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('orden', 'editar'))], summary="Actualizar orden", description="Actualiza una orden existente por su ID.")
async def actualizarOrdenApi(id: int, requestBody: OrdenUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_orden_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('orden', 'editar'))], summary="Actualizar orden parcialmente", description="Actualiza parcialmente una orden existente por su ID.")
async def patchOrdenApi(id: int, requestBody: OrdenUpdateRequest):
    return await actualizarOrdenApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('orden', 'crear'))], summary="Crear orden", description="Crea una nueva orden.")
async def agregarOrdenApi(requestBody: OrdenRequest,
                          background_tasks: BackgroundTasks):
    payload = requestBody.model_dump()
    result = await crear_orden(payload, background_tasks=background_tasks)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('orden', 'leer'))], summary="Obtener órdenes", description="Obtiene una lista de órdenes con filtros opcionales.")
async def obtenerOrdenesApi(
id: Optional[str] = Query(None, description="Filtrar orden por ID"),
    estado: Optional[int] = Query(None, description="Filtrar por estado (0:inactivo, 1:pendiente, 2:en_proceso, 3:listo, 4:entregado)"),
    id_mesafk: Optional[int] = Query(None, description="Filtrar por ID de mesa"),
    id_detalleproductofk: Optional[str] = Query(None, description="Filtrar por ID detalle_producto (cod_barra)"),
):
    filtros = {}
    if id is not None:
        filtros['id'] = id
    if estado is not None:
        filtros['estado'] = estado
    if id_mesafk is not None:
        filtros['id_mesafk'] = id_mesafk
    if id_detalleproductofk is not None:
        filtros['id_detalleproductofk'] = id_detalleproductofk

    result = await obtener_ordenes(filtros)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('orden', 'leer'))], summary="Obtener orden por ID", description="Obtiene una orden específica por su ID.")
async def obtenerOrdenPorIdApi(id: int):
    filtros = {'id': id}
    result = await obtener_ordenes(filtros)
    if not result:
        return {"message": f"Orden con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}

