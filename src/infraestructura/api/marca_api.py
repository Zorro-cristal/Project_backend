from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.services.marca_service import (actualizar_marca, crear_marca,
                                              obtener_marcas)
from src.shell.adapters.requests.marca_request import (MarcaRequest,
                                                         MarcaUpdateRequest)

router = APIRouter()

@router.put("/{id}", summary="Actualizar marca", description="Actualiza una marca existente por su ID.")
async def actualizarMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_marca(id, payload)
    return {"message": result}

@router.patch("/{id}", summary="Actualizar marca parcialmente", description="Actualiza parcialmente una marca existente por su ID.")
async def patchMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    return await actualizarMarcaApi(id, requestBody)

@router.post("/", summary="Crear marca", description="Crea una nueva marca.")
async def agregarMarcaApi(requestBody: MarcaRequest):
    payload = requestBody.model_dump()
    result = await crear_marca(payload)
    return {"message": result}

@router.get("/", summary="Obtener marcas", description="Obtiene una lista de marcas con filtros opcionales.")
async def obtenerMarcasApi(
    id: Optional[str] = Query(None, description="Filtrar marcas por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar marcas por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar marcas por estado (1 para activo, 0 para inactivo)")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    
    result = await obtener_marcas(filtros)
    return {"message": result}
