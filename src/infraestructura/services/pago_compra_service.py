from datetime import datetime, timezone
from typing import Optional

from ..repositories.pago_compra_repository import (
    actualizarPagoCompra, obtenerPagosPorCompraId,
    obtenerTotalPagadoPorCompraId)

# Tipos de pago (PagoCompra.tipo)
# 1: Cuota
# 2: Entrega
TIPO_CUOTA = 1
TIPO_ENTREGA = 2

# Estados
ESTADO_ACTIVO = 1
ESTADO_INACTIVO = 0


async def registrar_pago(
    id_compra: int,
    monto: float,
    tipo: int,
    id_cajafk: int,
    fecha: Optional[datetime] = None,
    id_usuariofk: Optional[int] = None,
) -> dict:
    """Registra un pago para una compra.
    
    Args:
        id_compra: ID de la compra
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
        'id_comprafk': id_compra,
        'id_cajafk': id_cajafk,
    }
    
    # Nota: pagos_compra en el schema no contiene id_usuariofk.
    # El usuario se obtiene por lógica desde cajas/id_cajafk, pero no se persiste aquí.
    return await actualizarPagoCompra(pago_data)


async def registrar_pago_contado(
    id_compra: int,
    monto_total: float,
    id_cajafk: int,
    id_usuariofk: Optional[int] = None,
    fecha: Optional[datetime] = None,
) -> dict:
    """Registra el pago de entrega inicial (tipo=2).
    
    Para compras al contado, se registra el pago total como entrega inicial
    con tipo=2.
    """
    if fecha is None:
        fecha = datetime.now(timezone.utc)
    
    pago_data = {
        'estado': ESTADO_ACTIVO,
        'tipo': TIPO_ENTREGA,
        'monto': monto_total,
        'fecha': fecha.isoformat(),
        'id_comprafk': id_compra,
        'id_cajafk': id_cajafk,
    }
    
    # Nota: pagos_compra en el schema no contiene id_usuariofk.
    # El usuario se obtiene por lógica desde cajas/id_cajafk, pero no se persiste aquí.
    return await actualizarPagoCompra(pago_data)


async def registrar_pago_cuota(
    id_compra: int,
    monto: float,
    id_cajafk: int,
    id_usuariofk: Optional[int] = None,
) -> dict:
    """Registra un pago de cuota (tipo=1).
    
    Para compras a crédito, los pagos posteriores son de tipo cuota.
    """
    return await registrar_pago(
        id_compra=id_compra,
        monto=monto,
        tipo=TIPO_CUOTA,
        id_cajafk=id_cajafk,
        id_usuariofk=id_usuariofk,
    )


async def obtener_pagos_por_compra(id_compra: int) -> list[dict]:
    """Obtiene todos los pagos de una compra."""
    return await obtenerPagosPorCompraId(id_compra)


async def obtener_total_pagado(id_compra: int) -> float:
    """Obtiene el total pagado de una compra."""
    return await obtenerTotalPagadoPorCompraId(id_compra)


async def anular_pago(id_pago: int) -> dict:
    """Anula un pago (cambia estado a inactivo)."""
    return await actualizarPagoCompra({'estado': ESTADO_INACTIVO}, id_pago)


async def recalcular_saldos(id_compra: int) -> dict:
    """Recalcula los saldos de una compra usando lógica FIFO.
    
    Esta función es llamada después de cada pago para actualizar
    el estado de las cuotas automáticamente.
    
    Returns:
        Dict con:
        - total_pagado: Total pagado
        - cuotas: Lista de cuotas con estados actualizados
        - saldo_pendiente: Saldo pendiente global
    """
    from .cuota_compra_service import recalcular_estado_cuotas

    # Obtener total pagado
    total_pagado = await obtenerTotalPagadoPorCompraId(id_compra)
    
    # Recalcular estados de cuotas con FIFO
    resultado = await recalcular_estado_cuotas(id_compra, total_pagado)
    
    return {
        'id_compra': id_compra,
        'total_pagado': resultado['total_pagado'],
        'cuotas': resultado['cuotas'],
        'saldo_pendiente': resultado['saldo_pendiente'],
        'total_deuda': resultado.get('total_deuda', 0),
    }
