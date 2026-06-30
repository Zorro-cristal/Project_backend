from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.pago_venta_request import (
    PagoVentaRequest, PagoVentaUpdateRequest, RegistroPagoContadoRequest,
    RegistroPagoCuotaRequest)

from ..services.pago_venta_service import (anular_pago,
                                           obtener_pagos_por_venta,
                                           obtener_total_pagado,
                                           recalcular_saldos, registrar_pago,
                                           registrar_pago_contado,
                                           registrar_pago_cuota)

router = APIRouter()


@router.post("/", dependencies=[Depends(permiso_requerido('pago', 'crear'))], summary="Registrar pago", description="Registra un pago para una venta.")
async def registrarPagoApi(requestBody: PagoVentaRequest):
    """Registra un pago."""
    payload = requestBody.model_dump(exclude_unset=True)
    
    resultado = await registrar_pago(
        id_venta=payload['id_ventafk'],
        monto=payload['monto'],
        tipo=payload['tipo'],
        id_cajafk=payload['id_cajafk'],
        fecha=payload.get('fecha'),
        id_usuariofk=payload.get('id_usuariofk'),
    )
    
    return {"message": resultado}


@router.post("/contado", dependencies=[Depends(permiso_requerido('pago', 'crear'))], summary="Registrar pago de contado", description="Registra el pago completo para una venta al contado.")
async def registrarPagoContadoApi(requestBody: RegistroPagoContadoRequest):
    """Registra pago de contado."""
    payload = requestBody.model_dump(exclude_unset=True)
    
    resultado = await registrar_pago_contado(
        id_venta=payload['id_venta'],
        monto_total=payload['monto_total'],
        id_cajafk=payload['id_cajafk'],
        id_usuariofk=payload.get('id_usuariofk'),
    )
    
    # Recalcular saldos automáticamente (marca cuotas como pagadas)
    await recalcular_saldos(payload['id_venta'])
    
    return {"message": resultado}


@router.post("/cuota", dependencies=[Depends(permiso_requerido('pago', 'crear'))], summary="Registrar pago de cuota", description="Registra un pago de cuota para una venta a crédito.")
async def registrarPagoCuotaApi(requestBody: RegistroPagoCuotaRequest):
    """Registra pago de cuota."""
    payload = requestBody.model_dump(exclude_unset=True)
    
    resultado = await registrar_pago_cuota(
        id_venta=payload['id_venta'],
        monto=payload['monto'],
        id_cajafk=payload['id_cajafk'],
        id_usuariofk=payload.get('id_usuariofk'),
    )
    
    # Recalcular saldos automáticamente (marca cuotas como pagadas por cantidad)
    await recalcular_saldos(payload['id_venta'])
    
    return {"message": resultado}


@router.get("/{id}/pagos", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Obtener pagos", description="Obtiene todos los pagos de una venta.")
async def obtenerPagosPorVentaApi(id: int):
    """Obtiene los pagos de una venta."""
    pagos = await obtener_pagos_por_venta(id)
    return {"message": pagos if pagos else []}


@router.get("/{id}/total", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Obtener total pagado", description="Obtiene el total pagado de una venta.")
async def obtenerTotalPagadoApi(id: int):
    """Obtiene el total pagado."""
    total = await obtener_total_pagado(id)
    return {"message": {"id_venta": id, "total_pagado": total}}


@router.patch("/{id}/anular", dependencies=[Depends(permiso_requerido('pago', 'eliminar'))], summary="Anular pago", description="Anula un pago (cambia estado a inactivo).")
async def anularPagoApi(id: int):
    """Anula un pago."""
    # Primero obtener la venta asociada para recalcular después
    from ..repositories.pago_venta_repository import obtenerPagoVenta
    pago = await obtenerPagoVenta({'id': id})
    
    resultado = await anular_pago(id)
    
    # Recalcular saldos si existe la venta
    if pago and pago[0].get('id_ventafk'):
        await recalcular_saldos(pago[0]['id_ventafk'])
    
    return {"message": resultado}


@router.post("/{id}/recalcular-saldos", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Recalcular saldos", description="Recalcula los saldos de una venta usando lógica FIFO.")
async def recalcularSaldosApi(id: int):
    """Recalcula los saldos."""
    resultado = await recalcular_saldos(id)
    return {"message": resultado}
