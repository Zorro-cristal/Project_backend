from typing import Optional

from fastapi import APIRouter, Query

from src.shell.flujo.caja.crearActualizarCaja import (
    actualizar_caja_por_id,
    crear_o_actualizar_caja,
)
from src.infraestructura.services.caja_service import obtener_cajas
from src.shell.adapters.requests.caja_request import (
    CajaRequest,
    CajaUpdateRequest,
)

router = APIRouter()


@router.put("/{id}", summary="Actualizar caja", description="Actualiza una caja existente por su ID.")
async def actualizarCajaApi(id: int, requestBody: CajaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_caja_por_id(id, payload)
    return {"message": result}


@router.patch("/{id}", summary="Actualizar caja parcialmente", description="Actualiza parcialmente una caja existente por su ID.")
async def patchCajaApi(id: int, requestBody: CajaUpdateRequest):
    return await actualizarCajaApi(id, requestBody)


@router.post("/", summary="Crear caja", description="Crea una nueva caja.")
async def agregarCajaApi(requestBody: CajaRequest):
    payload = requestBody.model_dump()
    result = await crear_o_actualizar_caja(payload)
    return {"message": result}


@router.get("/", summary="Obtener cajas", description="Obtiene una lista de cajas con filtros opcionales.")
async def obtenerCajasApi(
    id: Optional[str] = Query(None, description="Filtrar cajas por ID"),
    id_usuariofk: Optional[int] = Query(None, description="Filtrar cajas por ID de usuario asociado"),
    fecha_creacion: Optional[str] = Query(None, description="Filtrar cajas por fecha de creación"),
    fecha_cierre: Optional[str] = Query(None, description="Filtrar cajas por fecha de cierre")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_usuariofk is not None:
        filtros["id_usuariofk"] = id_usuariofk
    if fecha_creacion is not None:
        filtros["fecha_creacion"] = fecha_creacion
    if fecha_cierre is not None:
        filtros["fecha_cierre"] = fecha_cierre

    result = await obtener_cajas(filtros)
    return {"message": result}


@router.get("/{id}", summary="Obtener caja por ID", description="Obtiene una caja específica por su ID.")
async def obtenerCajaPorIdApi(id: int):
    filtros = {"id": id}
    result = await obtener_cajas(filtros)
    if not result:
        return {"message": f"Caja con ID {id} no encontrada"}
    return {"message": result[0] if isinstance(result, list) else result}
