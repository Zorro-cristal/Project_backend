from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.cliente_request import (ClienteRequest,
                                                         ClienteUpdateRequest)

from ..services.cliente_service import (actualizar_cliente, crear_cliente,
                                        obtener_clientes)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('cliente', 'editar'))], summary="Actualizar cliente", description="Actualiza un cliente existente por su ID.")
async def actualizarClienteApi(id: int, requestBody: ClienteUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_cliente(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('cliente', 'editar'))], summary="Actualizar cliente parcialmente", description="Actualiza parcialmente un cliente existente por su ID.")
async def patchClienteApi(id: int, requestBody: ClienteUpdateRequest):
    return await actualizarClienteApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('cliente', 'crear'))], summary="Crear cliente", description="Crea un nuevo cliente.")
async def agregarClienteApi(requestBody: ClienteRequest):
    payload = requestBody.model_dump()
    result = await crear_cliente(payload)
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('cliente', 'leer'))], summary="Obtener clientes", description="Obtiene una lista de clientes con filtros opcionales.")
async def obtenerClientesApi(
    nombre_completo: Optional[str] = Query(None, description="Buscar por nombre completo de la persona asociada (nombre o apellido, contiene)"),
    id: Optional[str] = Query(None, description="Filtrar clientes por ID"),
    ruc: Optional[int] = Query(None, description="Filtrar clientes por RUC"),
    razon_social: Optional[str] = Query(None, description="Filtrar clientes por razón social parcial"),
    persona_fisica: Optional[int] = Query(None, description="Filtrar clientes por tipo de persona física"),
    id_personafk: Optional[int] = Query(None, description="Filtrar clientes por ID de persona asociada"),
    estado: Optional[int] = Query(None, description="Filtrar clientes por estado (1 para activo, 0 para inactivo)"),
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    filtros = {}
    if nombre_completo is not None:
        filtros["nombre_completo"] = nombre_completo
    if id is not None:
        filtros["id"] = id
    if ruc is not None:
        filtros["ruc"] = ruc
    if razon_social is not None:
        filtros["razon_social"] = razon_social
    if persona_fisica is not None:
        filtros["persona_fisica"] = persona_fisica
    if id_personafk is not None:
        filtros["id_personafk"] = id_personafk
    if estado is not None:
        filtros["estado"] = estado

    result = await obtener_clientes(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}
