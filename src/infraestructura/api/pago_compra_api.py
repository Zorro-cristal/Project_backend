from fastapi import APIRouter, Depends, Query, HTTPException

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.pago_compra_request import (
    PagoCompraRequest,
)

from ..services.pago_compra_service import (
    anular_pago,
    obtener_pagos_por_compra,
    obtener_total_pagado,
    recalcular_saldos,
    registrar_pago,
)

router = APIRouter()


@router.post("/", dependencies=[Depends(permiso_requerido('pago', 'crear'))], summary="Registrar pago compra", description="Registra un pago para una compra.")
async def registrarPagoCompraApi(requestBody: PagoCompraRequest):
    payload = requestBody.model_dump(exclude_unset=True)

    try:
        resultado = await registrar_pago(
            id_compra=payload['id_comprafk'],
            monto=payload['monto'],
            tipo=payload['tipo'],
            id_cajafk=payload['id_cajafk'],
            fecha=payload.get('fecha'),
            id_usuariofk=payload.get('id_usuariofk'),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"message": resultado}


@router.get("/{id}/pagos", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Obtener pagos compra", description="Obtiene todos los pagos de una compra.")
async def obtenerPagosPorCompraApi(id: int):
    pagos = await obtener_pagos_por_compra(id)
    return {"message": pagos if pagos else []}


@router.get("/{id}/total", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Obtener total pagado compra", description="Obtiene el total pagado de una compra.")
async def obtenerTotalPagadoCompraApi(id: int):
    total = await obtener_total_pagado(id)
    return {"message": {"id_compra": id, "total_pagado": total}}


@router.patch("/{id}/anular", dependencies=[Depends(permiso_requerido('pago', 'eliminar'))], summary="Anular pago compra", description="Anula un pago de compra (cambia estado a inactivo).")
async def anularPagoCompraApi(id: int):
    # Recalcular saldos si existe la compra asociada
    from ..repositories.pago_compra_repository import obtenerPagoCompra

    pago = await obtenerPagoCompra({'id': id})
    resultado = await anular_pago(id)

    if pago and pago[0].get('id_comprafk'):
        await recalcular_saldos(pago[0]['id_comprafk'])

    return {"message": resultado}


@router.post("/{id}/recalcular-saldos", dependencies=[Depends(permiso_requerido('pago', 'leer'))], summary="Recalcular saldos compra", description="Recalcula los saldos de una compra usando lógica FIFO.")
async def recalcularSaldosCompraApi(id: int):
    resultado = await recalcular_saldos(id)
    return {"message": resultado}
