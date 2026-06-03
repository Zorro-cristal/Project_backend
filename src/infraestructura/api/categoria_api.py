from typing import Optional

from fastapi import APIRouter, Query

from ..services.categoria_service import (actualizar_categoria,
                                                  crear_categoria,
                                                  obtener_categorias)
from src.shell.adapters.requests.categoria_request import (
    CategoriaRequest, CategoriaUpdateRequest)

router = APIRouter()

@router.put("/{id}", summary="Actualizar categoría", description="Actualiza una categoría existente por su ID.")
async def actualizarCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_categoria(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar categoría parcialmente", description="Actualiza parcialmente una categoría existente por su ID.")
async def patchCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    return await actualizarCategoriaApi(id, requestBody)

@router.post("/", summary="Crear categoría", description="Crea una nueva categoría.")
async def agregarCategoriaApi(requestBody: CategoriaRequest):
    payload = requestBody.model_dump()
    result = await crear_categoria(payload)
    return {"message": result}

@router.get("/", summary="Obtener categorías", description="Obtiene una lista de categorías con filtros opcionales.")
async def obtenerCategoriasApi(
    id: Optional[str] = Query(None, description="Filtrar categorias por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar categorías por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar productos por estado (1 para activo, 0 para inactivo)"),
):
    filtros= {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    result = await obtener_categorias(filtros)
    return {"message": result}