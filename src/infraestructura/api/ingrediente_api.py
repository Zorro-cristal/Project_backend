from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.ingrediente_request import (
    IngredienteRequest, IngredienteUpdateRequest)

from ..services.ingrediente_service import (actualizar_ingrediente,
                                            crear_ingrediente,
                                            obtener_ingredientes)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('Ingredientes', 'editar'))], summary="Actualizar ingrediente", description="Actualiza un ingrediente existente por su ID.")
async def actualizarIngredienteApi(id: int, requestBody: IngredienteUpdateRequest, current_user: dict = Depends(permiso_requerido('Ingredientes', 'editar'))):
    payload = requestBody.model_dump(exclude_unset=True)
    
    # Propagar el actor autenticado antes de persistir
    actor_id = current_user.get("id")
    if actor_id is None:
        raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
    payload["actualizado_por"] = actor_id
    
    result = await actualizar_ingrediente(id, payload)
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('Ingredientes', 'editar'))], summary="Actualizar ingrediente parcialmente", description="Actualiza parcialmente un ingrediente existente por su ID.")
async def patchIngredienteApi(id: int, requestBody: IngredienteUpdateRequest, current_user: dict = Depends(permiso_requerido('Ingredientes', 'editar'))):
    return await actualizarIngredienteApi(id, requestBody, current_user)


@router.post("/", dependencies=[Depends(permiso_requerido('Ingredientes', 'crear'))], summary="Crear ingrediente", description="Crea un nuevo ingrediente.")
async def agregarIngredienteApi(requestBody: IngredienteRequest, current_user: dict = Depends(permiso_requerido('Ingredientes', 'crear'))):
    payload = requestBody.model_dump()
    
    # Propagar el actor autenticado antes de persistir
    actor_id = current_user.get("id")
    if actor_id is None:
        raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
    payload["actualizado_por"] = actor_id
    
    result = await crear_ingrediente(payload)
    return {"message": result}

@router.get("/", dependencies=[Depends(permiso_requerido('Ingredientes', 'leer'))], summary="Obtener ingredientes", description="Obtiene una lista de ingredientes con filtros opcionales.")
async def obtenerIngredientesApi(
    id: Optional[str] = Query(None, description="Filtrar ingredientes por ID"),
    cantidad: Optional[int] = Query(None, description="Filtrar ingredientes por cantidad"),
    unidad_medida: Optional[str] = Query(None, description="Filtrar ingredientes por unidad de medida"),
    id_producto_ingredientefk: Optional[int] = Query(None, description="Filtrar por producto ingrediente"),
    id_producto_finalfk: Optional[int] = Query(None, description="Filtrar por producto final"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
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

    result = await obtener_ingredientes(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}
