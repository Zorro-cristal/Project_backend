from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.categoria_request import (
    CategoriaRequest, CategoriaUpdateRequest)

from ..services.categoria_service import (actualizar_categoria,
                                          crear_categoria, obtener_categorias)

router = APIRouter()

@router.put("/{id}", dependencies=[Depends(permiso_requerido('categoria', 'editar'))], summary="Actualizar categoría", description="Actualiza una categoría existente por su ID.")
async def actualizarCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_categoria(id, payload)
    return {"message": result}

@router.patch("/{id}", dependencies=[Depends(permiso_requerido('categoria', 'editar'))], summary="Actualizar categoría parcialmente", description="Actualiza parcialmente una categoría existente por su ID.")
async def patchCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    return await actualizarCategoriaApi(id, requestBody)

@router.post("/", dependencies=[Depends(permiso_requerido('categoria', 'crear'))], summary="Crear categoría", description="Crea una nueva categoría.")
async def agregarCategoriaApi(requestBody: CategoriaRequest):
    payload = requestBody.model_dump()
    result = await crear_categoria(payload)
    return {"message": result}

@router.get("/", dependencies=[Depends(permiso_requerido('categoria', 'leer'))], summary="Obtener categorías", description="Obtiene una lista de categorías con filtros opcionales.")
async def obtenerCategoriasApi(
    id: Optional[str] = Query(None, description="Filtrar categorias por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar categorías por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar productos por estado (1 para activo, 0 para inactivo)"),
mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    filtros= {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    # Por defecto ocultar inactivos (estado=0), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = 1
    result = await obtener_categorias(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}
