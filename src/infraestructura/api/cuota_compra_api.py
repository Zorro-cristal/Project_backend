from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.cuota_compra_request import CuotaCompraUpdateRequest
from src.shell.adapters.requests.cuota_venta_request import GenerarCuotasRequest

from ..services.cuota_compra_service import (
    calcular_saldo_fifo,
    crear_cuotas_para_compra,
    recalcular_estado_cuotas,
    actualizar_cuota_compra,
)

router = APIRouter()


@router.post("/{id}/generar-cuotas", dependencies=[Depends(permiso_requerido('compra', 'crear'))], summary="Generar cuotas compra", description="Genera cuotas automáticamente para una compra a crédito.")
async def generarCuotasCompraApi(id: int, requestBody: GenerarCuotasRequest):
    payload = requestBody.model_dump()

    cuotas = await crear_cuotas_para_compra(
        id_compra=id,
        total_cuotas=payload['total_cuotas'],
        monto_cuota=payload['monto_cuota'],
        fecha_inicio=payload['fecha_inicio'],
        id_usuariofk=payload.get('id_usuariofk'),
        descuento=payload.get('descuento', 0),
        interes=payload.get('interes', 0),
    )

    return {"message": cuotas}


@router.put("/{id}", dependencies=[Depends(permiso_requerido('compra', 'editar'))], summary="Actualizar cuota compra", description="Actualiza una cuota de compra existente por su ID.")
async def actualizarCuotaCompraApi(id: int, requestBody: CuotaCompraUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    if not payload:
        raise ValueError("No hay campos para actualizar")

    resultado = await actualizar_cuota_compra(id_cuota=id, payload=payload)
    return {"message": resultado}


@router.post("/{id}/recalcular", dependencies=[Depends(permiso_requerido('compra', 'leer'))], summary="Recalcular estado cuotas compra", description="Recalcula el estado de las cuotas de la compra usando lógica FIFO (cobertura acumulada).")
async def recalcularCuotasCompraApi(id: int, total_pagado: float = Query(..., description="Total de dinero pagado")):
    resultado = await recalcular_estado_cuotas(id, total_pagado)
    return {"message": resultado}


@router.get(
    "/{id_compra}/informacion",
    dependencies=[Depends(permiso_requerido('compra', 'leer'))],
    summary="Información cuotas compra",
    description="Retorna información consolidada de cuotas/pagos/compra con el mismo shape que cuota_venta.",
)
async def obtenerInformacionCuotaCompraApi(id_compra: int):
    """
    Shape equivalente al endpoint de ventas (cuota_venta_api):
    {
      "message": {
        "cuota_venta": [...],
        "pago_venta": [{ "pagos_totales": ... }],
        "venta": {...},
        "monto_pendiente": ...,
        "cuotas_pendientes": ...
      }
    }
    """
    resultado = await calcular_saldo_fifo(id_compra)

    # calcular_saldo_fifo devuelve:
    # - total_pagado, total_deuda, cuotas (con pagada, saldo_restante, etc.), saldo_pendiente, cuotas_pagadas
    cuotas_registros = resultado.get("cuotas", []) or []
    monto_pendiente = resultado.get("saldo_pendiente", 0) or 0
    cuotas_pendientes = resultado.get("cuotas_pagadas", 0)  # Nota: "cuotas_pendientes" en ventas se calcula como (total - cuotas_pagadas)
    # Intentamos mantener mismo criterio que ventas:
    # cuota_venta_api: cuotas_pendientes = total_cuotas - cuotas_pagadas
    # En calcular_saldo_fifo no viene total_cuotas; lo inferimos como len(cuotas)
    total_cuotas = len(cuotas_registros)
    cuotas_pendientes = max(0, total_cuotas - int(cuotas_pendientes or 0))

    pagos_totales = resultado.get("total_pagado", 0) or 0

    # No tenemos "compra" aquí porque calcular_saldo_fifo no trae el objeto compra.
    # Mantener compatibilidad devolviendo None si no está.
    compra = resultado.get("compra")

    return {
        "message": {
            "cuota_venta": cuotas_registros,
            "pago_venta": [
                {
                    "pagos_totales": pagos_totales,
                }
            ],
            "venta": compra,
            "monto_pendiente": monto_pendiente,
            "cuotas_pendientes": cuotas_pendientes,
        }
    }
