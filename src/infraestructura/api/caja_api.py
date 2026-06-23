from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.caja_request import (CajaRequest,
                                                      CajaUpdateRequest)

from ..services.caja_service import (actualizar_caja, crear_caja,
                                     obtener_caja_por_id_con_movimientos,
                                     obtener_cajas)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('caja', 'editar'))], summary="Actualizar caja", description="Actualiza una caja existente por su ID.")
async def actualizarCajaApi(id: int, requestBody: CajaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    try:
        result = await actualizar_caja(id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('caja', 'editar'))], summary="Actualizar caja parcialmente", description="Actualiza parcialmente una caja existente por su ID.")
async def patchCajaApi(id: int, requestBody: CajaUpdateRequest):
    return await actualizarCajaApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('caja', 'crear'))], summary="Crear caja", description="Crea una nueva caja.")
async def agregarCajaApi(requestBody: CajaRequest):
    payload = requestBody.model_dump()
    try:
        result = await crear_caja(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('caja', 'leer'))], summary="Obtener cajas", description="Obtiene una lista de cajas con filtros opcionales.")
async def obtenerCajasApi(
    id: Optional[str] = Query(None, description="Filtrar cajas por ID"),
    id_usuariofk: Optional[int] = Query(None, description="Filtrar cajas por ID de usuario asociado"),
    fecha_creado: Optional[str] = Query(None, description="Filtrar cajas por fecha de creación"),
    fecha_cierre: Optional[str] = Query(None, description="Filtrar cajas por fecha de cierre")
):
    filtros = {}
    if id is not None:
        filtros["id"] = id
    if id_usuariofk is not None:
        filtros["id_usuariofk"] = id_usuariofk
    if fecha_creado is not None:
        filtros["fecha_creado"] = fecha_creado
    if fecha_cierre is not None:
        filtros["fecha_cierre"] = fecha_cierre

    result = await obtener_cajas(filtros)
    return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('caja', 'leer'))], summary="Obtener caja por ID", description="Obtiene una caja específica por su ID. Usa include=movimientos para incluir egresos, compras y ventas.")
async def obtenerCajaPorIdApi(
    id: int,
    include: Optional[str] = Query(None, description="include=movimientos para incluir egresos, compras y ventas")
):
    filtros = {"id": id}

    if include == "movimientos":
        result = await obtener_caja_por_id_con_movimientos(filtros)
    else:
        result = await obtener_cajas(filtros)
        if result:
            result = result[0] if isinstance(result, list) else result

    if not result:
        return {"message": f"Caja con ID {id} no encontrada"}
    return {"message": result}
