from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.marca_request import (MarcaRequest,
                                                       MarcaUpdateRequest)

from ..services.marca_service import (actualizar_marca, crear_marca,
                                      obtener_marcas)

router = APIRouter()

@router.put("/{id}", dependencies=[Depends(permiso_requerido('marca', 'editar'))], summary="Actualizar marca", description="Actualiza una marca existente por su ID.")
async def actualizarMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_marca(id, payload)
    return {"message": result}

@router.patch("/{id}", dependencies=[Depends(permiso_requerido('marca', 'editar'))], summary="Actualizar marca parcialmente", description="Actualiza parcialmente una marca existente por su ID.")
async def patchMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    return await actualizarMarcaApi(id, requestBody)

@router.post("/", dependencies=[Depends(permiso_requerido('marca', 'crear'))], summary="Crear marca", description="Crea una nueva marca.")
async def agregarMarcaApi(requestBody: MarcaRequest):
    payload = requestBody.model_dump()
    result = await crear_marca(payload)
    return {"message": result}

@router.get("/", dependencies=[Depends(permiso_requerido('marca', 'leer'))], summary="Obtener marcas", description="Obtiene una lista de marcas con filtros opcionales.")
async def obtenerMarcasApi(
    id: Optional[str] = Query(None, description="Filtrar marcas por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar marcas por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar marcas por estado (1 para activo, 0 para inactivo)"),
    mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
    limit: int = Query(100, ge=0, description="Cantidad máxima de registros a devolver"),
    offset: int = Query(0, ge=0, description="Offset desde el cual devolver registros, por defecto 0"),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    # Por defecto ocultar inactivos (estado=0), mostrar solo activos
    if mostrar_inactivo != 1:
        filtros["estado"] = 1
    
    result = await obtener_marcas(filtros=filtros, columnas='*', limite=limit, offset=offset)
    return {"message": result}
