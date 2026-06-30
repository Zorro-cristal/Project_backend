from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.cuota_venta_request import (
    CuotaVentaUpdateRequest, GenerarCuotasRequest)

from ..services.cuota_venta_service import (actualizar_estado_cuota,
                                            crear_cuotas_para_venta,
                                            obtener_cuotas_por_venta,
                                            recalcular_estado_cuotas)

router = APIRouter()


@router.post("/{id}/generar-cuotas", dependencies=[Depends(permiso_requerido('venta', 'crear'))], summary="Generar cuotas", description="Genera cuotas automáticamente para una venta a crédito.")
async def generarCuotasApi(id: int, requestBody: GenerarCuotasRequest):
    """Genera cuotas para una venta."""
    payload = requestBody.model_dump()
    
    cuotas = await crear_cuotas_para_venta(
        id_venta=id,
        total_cuotas=payload['total_cuotas'],
        monto_cuota=payload['monto_cuota'],
        fecha_inicio=payload['fecha_inicio'],
        id_usuariofk=payload.get('id_usuariofk'),
        descuento=payload.get('descuento', 0),
        interes=payload.get('interes', 0),
    )
    
    return {"message": cuotas}


@router.get("/{id}/cuotas", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Obtener cuotas", description="Obtiene las cuotas de una venta.")
async def obtenerCuotasPorVentaApi(id: int):
    """Obtiene las cuotas de una venta."""
    cuotas = await obtener_cuotas_por_venta(id)
    return {"message": cuotas if cuotas else []}


@router.put("/{id}", dependencies=[Depends(permiso_requerido('venta', 'editar'))], summary="Actualizar cuota", description="Actualiza una cuota existente.")
async def actualizarCuotaApi(id: int, requestBody: CuotaVentaUpdateRequest):
    """Actualiza una cuota."""
    payload = requestBody.model_dump(exclude_unset=True)
    if not payload:
        raise ValueError('No hay campos para actualizar')
    
    resultado = await actualizar_estado_cuota(id, payload.get('estado', 1))
    return {"message": resultado}


@router.post("/{id}/recalcular", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Recalcular estado de cuotas", description="Recalcula el estado de todas las cuotas usando lógica FIFO.")
async def recalcularCuotasApi(id: int, total_pagado: float = Query(..., description="Total de dinero pagado")):
    """Recalcula los estados de cuotas con FIFO."""
    resultado = await recalcular_estado_cuotas(id, total_pagado)
    return {"message": resultado}
