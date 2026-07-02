from datetime import datetime, timezone
from typing import Optional

from ..repositories.pago_venta_repository import (actualizarPagoVenta,
                                                  obtenerPagosPorVentaId,
                                                  obtenerTotalPagadoPorVentaId)

# Tipos de pago
# NULL para ventas al contado (pago único)
# 1 para cuotas (crédito)
# 2 para entregas
TIPO_CUOTA = 1   # Pago de cuota (crédito)
# NOTA: Para ventas al contado, el tipo es NULL

# Estados
ESTADO_ACTIVO = 1
ESTADO_INACTIVO = 0


async def registrar_pago(
    id_venta: int,
    monto: float,
    tipo: int,
    id_cajafk: int,
    fecha: Optional[datetime] = None,
    id_usuariofk: Optional[int] = None,
) -> dict:
    """Registra un pago para una venta.
    
    Args:
        id_venta: ID de la venta
        monto: Monto del pago
        tipo: Tipo de pago (1=Cuota, 2=Entrega)
        id_cajafk: ID de la caja
        fecha: Fecha del pago (por defecto ahora)
        id_usuariofk: ID del usuario que registra el pago
    
    Returns:
        Dict con el pago creado
    """
    if fecha is None:
        fecha = datetime.now(timezone.utc)
    
    pago_data = {
        'estado': ESTADO_ACTIVO,
        'tipo': tipo,
        'monto': monto,
        'fecha': fecha.isoformat(),
        'id_ventafk': id_venta,
        'id_cajafk': id_cajafk,
    }
    
    if id_usuariofk:
        pago_data['id_usuariofk'] = id_usuariofk
    
    return await actualizarPagoVenta(pago_data)


async def registrar_pago_contado(
    id_venta: int,
    monto_total: float,
    id_cajafk: int,
    id_usuariofk: Optional[int] = None,
    fecha: Optional[datetime] = None,
) -> dict:
    """Registra un pago de contado (tipo=NULL).
    
    Para ventas al contado (tipo_credito=0), el tipo es NULL.
    """
    if fecha is None:
        fecha = datetime.now(timezone.utc)
    
    pago_data = {
        'estado': ESTADO_ACTIVO,
        'tipo': None,  # NULL para ventas al contado
        'monto': monto_total,
        'fecha': fecha.isoformat(),
        'id_ventafk': id_venta,
        'id_cajafk': id_cajafk,
    }
    
    if id_usuariofk:
        pago_data['id_usuariofk'] = id_usuariofk
    
    return await actualizarPagoVenta(pago_data)


async def registrar_pago_cuota(
    id_venta: int,
    monto: float,
    id_cajafk: int,
    id_usuariofk: Optional[int] = None,
) -> dict:
    """Registra un pago de cuota (tipo=1).
    
    Para ventas a crédito, los pagos posteriores son de tipo cuota.
    """
    return await registrar_pago(
        id_venta=id_venta,
        monto=monto,
        tipo=TIPO_CUOTA,
        id_cajafk=id_cajafk,
        id_usuariofk=id_usuariofk,
    )


async def obtener_pagos_por_venta(id_venta: int) -> list[dict]:
    """Obtiene todos los pagos de una venta."""
    return await obtenerPagosPorVentaId(id_venta)


async def obtener_total_pagado(id_venta: int) -> float:
    """Obtiene el total pagado de una venta."""
    return await obtenerTotalPagadoPorVentaId(id_venta)


async def anular_pago(id_pago: int) -> dict:
    """Anula un pago (cambia estado a inactivo)."""
    return await actualizarPagoVenta({'estado': ESTADO_INACTIVO}, id_pago)


async def recalcular_saldos(id_venta: int) -> dict:
    """Recalcula los saldos de una venta usando lógica FIFO.
    
    Esta función es llamada después de cada pago para actualizar
    el estado de las cuotas automáticamente.
    
    Returns:
        Dict con:
        - total_pagado: Total pagado
        - cuotas: Lista de cuotas con estados actualizados
        - saldo_pendiente: Saldo pendiente global
    """
    from .cuota_venta_service import recalcular_estado_cuotas

    # Obtener total pagado
    total_pagado = await obtenerTotalPagadoPorVentaId(id_venta)
    
    # Recalcular estados de cuotas con FIFO
    resultado = await recalcular_estado_cuotas(id_venta, total_pagado)
    
    return {
        'id_venta': id_venta,
        'total_pagado': resultado['total_pagado'],
        'cuotas': resultado['cuotas'],
        'saldo_pendiente': resultado['saldo_pendiente'],
        'total_deuda': resultado.get('total_deuda', 0),
    }
