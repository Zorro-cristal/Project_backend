from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.ingrediente_service import (
    actualizar_ingrediente, crear_ingrediente, obtener_ingredientes)
from src.shell.adapters.requests.ingrediente_request import (
    IngredienteRequest, IngredienteUpdateRequest)

router = APIRouter()


@router.put("/{id}", summary="Actualizar ingrediente", description="Actualiza un ingrediente existente por su ID.")
async def actualizarIngredienteApi(id: int, requestBody: IngredienteUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_ingrediente(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar ingrediente parcialmente", description="Actualiza parcialmente un ingrediente existente por su ID.")
async def patchIngredienteApi(id: int, requestBody: IngredienteUpdateRequest):
    return await actualizarIngredienteApi(id, requestBody)


@router.post("/", summary="Crear ingrediente", description="Crea un nuevo ingrediente.")
async def agregarIngredienteApi(requestBody: IngredienteRequest):
    payload = requestBody.model_dump()
    result = await crear_ingrediente(payload)
    return {"message": result}


@router.get("/", summary="Obtener ingredientes", description="Obtiene una lista de ingredientes con filtros opcionales.")
async def obtenerIngredientesApi(
    id: Optional[str] = Query(None, description="Filtrar ingredientes por ID"),
    cantidad: Optional[int] = Query(None, description="Filtrar ingredientes por cantidad"),
    unidad_medida: Optional[str] = Query(None, description="Filtrar ingredientes por unidad de medida"),
    id_producto_ingredientefk: Optional[int] = Query(None, description="Filtrar por producto ingrediente"),
    id_producto_finalfk: Optional[int] = Query(None, description="Filtrar por producto final"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if cantidad is not None:
        filtros["cantidad"] = cantidad
    if unidad_medida is not None:
        filtros["unidad_medida"] = unidad_medida
    if id_producto_ingredientefk is not None:
        filtros["id_producto_ingredientefk"] = id_producto_ingredientefk
    if id_producto_finalfk is not None:
        filtros["id_producto_finalfk"] = id_producto_finalfk

    result = await obtener_ingredientes(filtros)
    return {"message": result}
