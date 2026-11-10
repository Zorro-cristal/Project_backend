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


@router.post(
    "/",
    dependencies=[Depends(permiso_requerido('pago', 'crear'))],
    summary="Registrar pago",
    description="Registra un pago para una venta.",
)
async def registrarPagoApi(requestBody: PagoVentaRequest, current_user: dict = Depends(permiso_requerido('Pagos_venta', 'crear'))):
    """Registra un pago."""
    payload = requestBody.model_dump(exclude_unset=True)

    # Propagar el actor autenticado antes de persistir (no debe ser editable por cliente)
    if "actualizado_por" not in payload or payload["actualizado_por"] is None:
        id_usuariofk = current_user.get("id")
        if id_usuariofk is None:
            raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
        payload["actualizado_por"] = id_usuariofk

    resultado = await registrar_pago(
        id_venta=payload['id_ventafk'],
        monto=payload['monto'],
        tipo=payload['tipo'],
        id_cajafk=payload['id_cajafk'],
        fecha=payload.get('fecha'),
        id_vendedorfk=payload.get('id_vendedorfk'),
        # compatibilidad
        id_usuariofk=payload.get('id_usuariofk'),
    )

    return {"message": resultado}




@router.get("/{id}/pagos", dependencies=[Depends(permiso_requerido('Pagos_venta', 'leer'))], summary="Obtener pagos", description="Obtiene todos los pagos de una venta.")
async def obtenerPagosPorVentaApi(id: int):
    """Obtiene los pagos de una venta."""
    pagos = await obtener_pagos_por_venta(id)
    return {"message": pagos if pagos else []}


@router.get("/{id}/total", dependencies=[Depends(permiso_requerido('Pagos_venta', 'leer'))], summary="Obtener total pagado", description="Obtiene el total pagado de una venta.")
async def obtenerTotalPagadoApi(id: int):
    """Obtiene el total pagado."""
    total = await obtener_total_pagado(id)
    return {"message": {"id_venta": id, "total_pagado": total}}


@router.patch("/{id}/anular", dependencies=[Depends(permiso_requerido('Pagos_venta', 'eliminar'))], summary="Anular pago", description="Anula un pago (cambia estado a inactivo).")
async def anularPagoApi(id: int, current_user: dict = Depends(permiso_requerido('pago', 'eliminar'))):
    """Anula un pago."""
    # Primero obtener la venta asociada para recalcular después
    from ..repositories.pago_venta_repository import obtenerPagoVenta
    pago = await obtenerPagoVenta({'id': id})
    
    actor_id = current_user.get("id")
    if actor_id is None:
        raise HTTPException(status_code=401, detail="No se pudo determinar el usuario autenticado.")
    
    resultado = await anular_pago(id)
    
    # Recalcular saldos si existe la venta
    if pago and pago[0].get('id_ventafk'):
        await recalcular_saldos(pago[0]['id_ventafk'])
    
    return {"message": resultado}


@router.post("/{id}/recalcular-saldos", dependencies=[Depends(permiso_requerido('Pagos_venta', 'leer'))], summary="Recalcular saldos", description="Recalcula los saldos de una venta usando lógica FIFO.")
async def recalcularSaldosApi(id: int):
    """Recalcula los saldos."""
    resultado = await recalcular_saldos(id)
    return {"message": resultado}
