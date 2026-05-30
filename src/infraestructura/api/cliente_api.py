from typing import Optional

from fastapi import APIRouter, Query

from src.shell.flujo.cliente.crearActualizarCliente import (
    actualizar_cliente_por_id,
    crear_o_actualizar_cliente,
)
from src.infraestructura.services.cliente_service import obtener_clientes
from src.shell.adapters.requests.cliente_request import (
    ClienteRequest,
    ClienteUpdateRequest,
)

router = APIRouter()

@router.put("/{id}", summary="Actualizar cliente", description="Actualiza un cliente existente por su ID.")
async def actualizarClienteApi(id: int, requestBody: ClienteUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_cliente_por_id(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar cliente parcialmente", description="Actualiza parcialmente un cliente existente por su ID.")
async def patchClienteApi(id: int, requestBody: ClienteUpdateRequest):
    return await actualizarClienteApi(id, requestBody)

@router.post("/", summary="Crear cliente", description="Crea un nuevo cliente.")
async def agregarClienteApi(requestBody: ClienteRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_cliente(payload)
    return {"message": result}

@router.get("/", summary="Obtener clientes", description="Obtiene una lista de clientes con filtros opcionales.")
async def obtenerClientesApi(
    id: Optional[str] = Query(None, description="Filtrar clientes por ID"),
    ruc: Optional[int] = Query(None, description="Filtrar clientes por RUC"),
    razon_social: Optional[str] = Query(None, description="Filtrar clientes por razón social parcial"),
    estado: Optional[int] = Query(None, description="Filtrar clientes por estado (1 activo, 0 inactivo)"),
    persona_fisica: Optional[int] = Query(None, description="Filtrar clientes por tipo de persona física"),
    id_personafk: Optional[int] = Query(None, description="Filtrar clientes por ID de persona asociada")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if ruc is not None:
        filtros["ruc"] = ruc
    if razon_social is not None:
        filtros["razon_social"] = razon_social
    if estado is not None:
        filtros["estado"] = estado
    if persona_fisica is not None:
        filtros["persona_fisica"] = persona_fisica
    if id_personafk is not None:
        filtros["id_personafk"] = id_personafk

    result = await obtener_clientes(filtros)
    return {"message": result}
