from typing import Optional

from fastapi import APIRouter, Query

from src.shell.flujo.compra.crearActualizarCompra import (
    actualizar_compra_por_id,
    crear_o_actualizar_compra,
)
from src.infraestructura.services.compra_service import obtener_compras
from src.shell.adapters.requests.compra_request import (
    CompraRequest,
    CompraUpdateRequest,
)

router = APIRouter()


@router.put("/{id}", summary="Actualizar compra", description="Actualiza una compra existente por su ID.")
async def actualizarCompraApi(id: int, requestBody: CompraUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_compra_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar compra parcialmente", description="Actualiza parcialmente una compra existente por su ID.")
async def patchCompraApi(id: int, requestBody: CompraUpdateRequest):
    return await actualizarCompraApi(id, requestBody)


@router.post("/", summary="Crear compra", description="Crea una nueva compra.")
async def agregarCompraApi(requestBody: CompraRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_compra(payload)
    return {"message": result}


@router.get("/", summary="Obtener compras", description="Obtiene una lista de compras con filtros opcionales.")
async def obtenerComprasApi(
    id: Optional[int] = Query(None, description="Filtrar compras por ID"),
    nro: Optional[str] = Query(None, description="Filtrar compras por número"),
    id_localFK: Optional[int] = Query(None, description="Filtrar compras por ID de local"),
    id_clienteFK: Optional[int] = Query(None, description="Filtrar compras por ID de cliente"),
    id_proveedorFK: Optional[int] = Query(None, description="Filtrar compras por ID de proveedor"),
    estado: Optional[int] = Query(None, description="Filtrar compras por estado")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nro is not None:
        filtros["nro"] = nro
    if id_localFK is not None:
        filtros["id_localFK"] = id_localFK
    if id_clienteFK is not None:
        filtros["id_clienteFK"] = id_clienteFK
    if id_proveedorFK is not None:
        filtros["id_proveedorFK"] = id_proveedorFK
    if estado is not None:
        filtros["estado"] = estado

    result = await obtener_compras(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener compra por ID", description="Obtiene una compra específica por su ID.")
async def obtenerCompraPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_compras(filtros)
    if not result:
        return {"message": f"Compra con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}
