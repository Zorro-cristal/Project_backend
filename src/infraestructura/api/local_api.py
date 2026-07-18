from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.local_request import (LocalRequest,
                                                       LocalUpdateRequest)

from ..services.local_service import (actualizar_local, crear_local,
                                      obtener_locales)
from .schemas.relational_sanitizers import LocalListResponse

router = APIRouter()


@router.put(
    "/{id}",
    dependencies=[Depends(permiso_requerido("local", "editar"))],
    summary="Actualizar local",
    description="Actualiza un local existente por su ID.",
)
async def actualizarLocalApi(id: int, requestBody: LocalUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_local(id, payload)
    return {"message": result}


@router.patch(
    "/{id}",
    dependencies=[Depends(permiso_requerido("local", "editar"))],
    summary="Actualizar local parcialmente",
    description="Actualiza parcialmente un local existente por su ID.",
)
async def patchLocalApi(id: int, requestBody: LocalUpdateRequest):
    return await actualizarLocalApi(id, requestBody)


@router.post(
    "/",
    dependencies=[Depends(permiso_requerido("local", "crear"))],
    summary="Crear local",
    description="Crea un nuevo local.",
)
async def agregarLocalApi(requestBody: LocalRequest):
    payload = requestBody.model_dump()
    result = await crear_local(payload)
    return {"message": result}


@router.get(
    "/",
    dependencies=[Depends(permiso_requerido("local", "leer"))],
    summary="Obtener locales",
    description="Obtiene una lista de locales con filtros opcionales.",
    response_model=LocalListResponse,
)
async def obtenerLocalesApi(
    id: Optional[str] = Query(None, description="Filtrar locales por ID"),
    nombre: Optional[str] = Query(None, description="Filtrar locales por nombre parcial"),
    estado: Optional[int] = Query(None, description="Filtrar locales por estado (1 activo, 0 inactivo)"),
    direccion: Optional[str] = Query(None, description="Filtrar locales por dirección"),
    telefono: Optional[str] = Query(None, description="Filtrar locales por teléfono"),
    mostrar_inactivo: Optional[int] = Query(
        None,
        description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos",
    ),
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if nombre is not None:
        filtros["nombre"] = nombre
    if estado is not None:
        filtros["estado"] = estado
    if direccion is not None:
        filtros["direccion"] = direccion
    if telefono is not None:
        filtros["telefono"] = telefono
    if mostrar_inactivo != 1 and "estado" not in filtros:
        filtros["mostrar_inactivo"] = 0  # estado != 0

    result = await obtener_locales(filtros)
    return {"message": result}
