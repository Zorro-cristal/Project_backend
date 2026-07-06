from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.cuota_venta_request import (
    CuotaVentaUpdateRequest, GenerarCuotasRequest)

from ..services.cuota_venta_service import (actualizar_cuota,
                                            actualizar_estado_cuota,
                                            crear_cuotas_para_venta,
                                            obtener_info_cuota_venta,
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
        id_vendedorfk=payload.get('id_vendedorfk'),
        # compatibilidad
        id_usuariofk=payload.get('id_usuariofk'),
        descuento=payload.get('descuento', 0),
        interes=payload.get('interes', 0),
    )
    
    return {"message": cuotas}





@router.put("/{id}", dependencies=[Depends(permiso_requerido('venta', 'editar'))], summary="Actualizar cuota", description="Actualiza una cuota existente.")
async def actualizarCuotaApi(id: int, requestBody: CuotaVentaUpdateRequest):
    """Actualiza una cuota."""
    payload = requestBody.model_dump(exclude_unset=True)
    if not payload:
        raise ValueError('No hay campos para actualizar')
    
    resultado = await actualizar_cuota(id, payload)
    return {"message": resultado}


@router.post("/{id}/recalcular", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Recalcular estado de cuotas", description="Recalcula el estado de todas las cuotas usando lógica FIFO.")
async def recalcularCuotasApi(id: int, total_pagado: float = Query(..., description="Total de dinero pagado")):
    """Recalcula los estados de cuotas con FIFO."""
    resultado = await recalcular_estado_cuotas(id, total_pagado)
    return {"message": resultado}


@router.get("/{id_venta}/informacion", dependencies=[Depends(permiso_requerido('venta', 'leer'))], summary="Obtener información de cuota de venta", description="Retorna información completa de cuotas, pagos y la venta asociada.")
async def obtenerInformacionCuotaVentaApi(id_venta: int):
    """Obtiene información completa de cuotas de una venta.

    Retorna en formato requerido:
    {
        "message": {
            "cuota_venta": {...},
            "pago_venta": {...},
            "venta": {...},
            "monto_pendiente": 10000,
            "cuotas_pendientes": 2
        }
    }
    """
    resultado = await obtener_info_cuota_venta(id_venta)

    # resultado ya viene con:
    # - cuota_info: { total_cuotas, cuotas_pendientes, monto_cuota, pagos_totales, monto_pendiente, cuotas }
    # - venta
    cuota_info = resultado.get('cuota_info') or {}

    monto_pendiente = cuota_info.get('monto_pendiente', 0)
    cuotas_pendientes = cuota_info.get('cuotas_pendientes', 0)

    # cuota_info incluye:
    # - cuotas: lista de registros de cuotas (cada uno con id, monto_original, ...)
    # - total_cuotas, cuotas_pendientes, monto_cuota, pagos_totales, monto_pendiente
    cuotas_registros = cuota_info.get('cuotas', [])

    return {
        "message": {
            "cuota_venta": cuotas_registros,
            "pago_venta": [
                {
                    "pagos_totales": cuota_info.get('pagos_totales', 0)
                }
            ],
            "venta": resultado.get('venta'),
            "monto_pendiente": monto_pendiente,
            "cuotas_pendientes": cuotas_pendientes,
        }
    }



