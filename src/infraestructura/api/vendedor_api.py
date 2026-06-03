from typing import Optional

from fastapi import APIRouter, Query

from src.shell.flujo.vendedor.crearActualizarVendedor import (
    actualizar_vendedor_por_id,
    crear_o_actualizar_vendedor,
)
from ..services.vendedor_service import obtener_vendedores
from src.shell.adapters.requests.vendedor_request import (
    VendedorRequest,
    VendedorUpdateRequest,
)

router = APIRouter()


@router.put("/{id}", summary="Actualizar vendedor", description="Actualiza un vendedor existente por su ID.")
async def actualizarVendedorApi(id: int, requestBody: VendedorUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_vendedor_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar vendedor parcialmente", description="Actualiza parcialmente un vendedor existente por su ID.")
async def patchVendedorApi(id: int, requestBody: VendedorUpdateRequest):
    return await actualizarVendedorApi(id, requestBody)


@router.post("/", summary="Crear vendedor", description="Crea un nuevo vendedor.")
async def agregarVendedorApi(requestBody: VendedorRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_vendedor(payload)
    return {"message": result}


@router.get("/", summary="Obtener vendedores", description="Obtiene una lista de vendedores con filtros opcionales.")
async def obtenerVendedoresApi(
    id: Optional[str] = Query(None, description="Filtrar vendedores por ID"),
    salario: Optional[float] = Query(None, description="Filtrar vendedores por salario mínimo"),
    comision: Optional[float] = Query(None, description="Filtrar vendedores por comisión"),
    estado: Optional[bool] = Query(None, description="Filtrar vendedores por estado (true activo, false inactivo)"),
    id_personafk: Optional[int] = Query(None, description="Filtrar vendedores por ID de persona asociada")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if salario is not None:
        filtros["salario"] = salario
    if comision is not None:
        filtros["comision"] = comision
    if estado is not None:
        filtros["estado"] = estado
    if id_personafk is not None:
        filtros["id_personafk"] = id_personafk

    result = await obtener_vendedores(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener vendedor por ID", description="Obtiene un vendedor específico por su ID.")
async def obtenerVendedorPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_vendedores(filtros)
    if not result:
        return {"message": f"Vendedor con ID {id} no encontrado"}
    return {"message": result[0] if isinstance(result, list) else result}
