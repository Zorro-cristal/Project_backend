from datetime import datetime, timezone
from typing import Optional

from src.shell.utils import prepararPayloadDb

from ..repositories.cuota_compra_repository import (actualizarCuotaCompra,
                                                    obtenerCuotasPorCompraId)

ESTADO_INACTIVO = 0
ESTADO_ACTIVO = 1

from ..models.cuota_compra import CuotaCompra


async def crear_cuotas_para_compra(cuota_base: CuotaCompra) -> list[dict]:
    if not cuota_base.id_comprafk:
        raise ValueError("crear_cuotas_para_compra: cuota_base.id_comprafk es requerido")

    if not cuota_base.total_cuotas or cuota_base.total_cuotas < 1:
        raise ValueError("crear_cuotas_para_compra: total_cuotas debe ser mayor a 0")

    if cuota_base.monto_cuota is None:
        raise ValueError("crear_cuotas_para_compra: monto_cuota es requerido")

    if cuota_base.fecha_inicio is None:
        raise ValueError("crear_cuotas_para_compra: fecha_inicio es requerido")

    cuotas_creadas = []
    total_cuotas = int(cuota_base.total_cuotas)
    monto_cuota = float(cuota_base.monto_cuota)
    fecha_inicio = cuota_base.fecha_inicio
    id_usuariofk = cuota_base.id_usuariofk
    descuento = float(cuota_base.descuento or 0)
    interes = int(cuota_base.interes or 0)

    for i in range(total_cuotas):
        # Calcular fecha de cada cuota (añadir meses)
        from calendar import monthrange

        año = fecha_inicio.year
        mes = fecha_inicio.month + i
        año += (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        dia = min(fecha_inicio.day, monthrange(año, mes)[1])

        fecha_cuota = datetime(año, mes, dia, tzinfo=timezone.utc)

        # Calcular monto con interés si aplica
        monto_final = monto_cuota
        if interes > 0:
            monto_final = monto_cuota * (1 + interes / 100)

        # Aplicar descuento si existe
        if descuento > 0:
            monto_final = monto_final - descuento

        # Crear cuota con estado=1 (activo)
        cuota_data = {
            'estado': ESTADO_ACTIVO,
            'monto': monto_final,
            'fecha': fecha_cuota.isoformat(),
            'descuento': descuento,
            'interes': interes,
            'id_comprafk': cuota_base.id_comprafk,
            'id_usuariofk': id_usuariofk,
        }

        cuota = await actualizarCuotaCompra(cuota_data)
        cuotas_creadas.append(cuota)

    return cuotas_creadas


async def obtener_cuotas_por_compra(id_compra: int) -> list[dict]:
    """Obtiene las cuotas de una compra ordenadas por fecha."""
    return await obtenerCuotasPorCompraId(id_compra)


async def actualizar_estado_cuota(id_cuota: int, nuevo_estado: int) -> dict:
    """Actualiza el estado activo/inactivo de una cuota.
    
    Nota: Esto solo cambia si la cuota está activa o inactiva,
    no indica si está pagada.
    """
    return await actualizarCuotaCompra({'estado': nuevo_estado}, id_cuota)


async def recalcular_estado_cuotas(id_compra: int, total_pagado: float) -> dict:
    """Calcula el estado de las cuotas según la lógica FIFO (dinámica).

    Nota de implementación:
    - En ventas, "pagada" se calcula por COBERTURA acumulada basada en montos:
        monto_cubierto = min(monto_cuota, saldo_pagado_acumulado)
    - En compras, se implementa la misma lógica para que pagos parciales cubran
      parcialmente cuotas y el saldo pendiente sea correcto.

    Filtrado:
    - cuotas consideradas: estado==1 (activa)
    - pagos considerados: estado==1 (activos). Los pagos con estado==0 se excluyen.

    Returns:
        Dict con:
        - cuotas: Lista de cuotas con estado calculado (pagada dinámicamente)
        - saldo_pendiente: Saldo pendiente global
        - total_pagado: Total pagado (suma entregada desde repository)
        - total_deuda: Total de la deuda (suma montos de cuotas activas)
        - cuotas_pagadas: Cantidad de cuotas totalmente cubiertas
    """
    from ..repositories.pago_compra_repository import obtenerPagosPorCompraId

    cuotas = await obtenerCuotasPorCompraId(id_compra)
    cuotas = [c for c in (cuotas or []) if c.get('estado', 1) == 1]

    if not cuotas:
        return {
            'cuotas': [],
            'saldo_pendiente': 0,
            'total_pagado': total_pagado,
            'total_deuda': 0,
            'cuotas_pagadas': 0,
        }

    pagos = await obtenerPagosPorCompraId(id_compra)
    pagos_activos = [p for p in (pagos or []) if p.get('estado', 1) == 1]

    total_deuda = sum(float(c.get('monto', 0) or 0) for c in cuotas)
    saldo_pagado_acumulado = float(total_pagado or 0)

    cuotas_procesadas = []
    cuotas_pagadas = 0

    # FIFO por orden en la lista (repository describe orden por fecha)
    for cuota in cuotas:
        id_cuota = cuota.get('id')
        monto_cuota = float(cuota.get('monto', 0) or 0)

        monto_cubierto = min(monto_cuota, saldo_pagado_acumulado)
        saldo_pagado_acumulado = max(0, saldo_pagado_acumulado - monto_cuota)

        pagada = monto_cubierto >= monto_cuota and monto_cuota > 0
        if pagada:
            cuotas_pagadas += 1

        monto_pendiente_cuota = max(0, monto_cuota - monto_cubierto)

        cuotas_procesadas.append({
            'id': id_cuota,
            'monto_original': monto_cuota,
            'monto_cubierto': monto_cubierto,
            'saldo_restante': monto_pendiente_cuota,
            'monto_pendiente': monto_pendiente_cuota,
            'pagada': pagada,
            'fecha': cuota.get('fecha'),
            'estado': cuota.get('estado'),
        })

    saldo_pendiente_global = max(
        0,
        total_deuda - sum(float(c.get('monto_cubierto', 0) or 0) for c in cuotas_procesadas)
    )

    return {
        'cuotas': cuotas_procesadas,
        'saldo_pendiente': saldo_pendiente_global,
        'total_pagado': total_pagado,
        'total_deuda': total_deuda,
        'cuotas_pagadas': cuotas_pagadas,
    }


async def actualizar_cuota_compra(id_cuota: int, payload: dict) -> dict:
    """Actualiza atributos de una cuota de compra por ID.

    Nota:
    - Se delega a `actualizarCuotaCompra`, que actualiza campos del payload en DB.
    - No recalcula FIFO automáticamente; si se requiere, llamar desde la API
      `POST /{id}/recalcular` (igual que en ventas).
    """
    # El repository espera (datos, id)
    from ..repositories.cuota_compra_repository import actualizarCuotaCompra
    return await actualizarCuotaCompra(payload, id=id_cuota)


async def calcular_saldo_fifo(id_compra: int) -> dict:
    """Calcula el saldo de una compra a crédito usando lógica FIFO.
    
    Esta función es el método principal que debe llamarse desde la API.
    
    Returns:
        - id_compra: ID de la compra
        - total_pagado: Total de dinero pagado
        - total_deuda: Total de la deuda original
        - cuotas: Lista de cuotas con:
            - monto_original
            - monto_cubierto
            - saldo_restante
            - pagada (calculada dinámicamente por FIFO)
        - saldo_pendiente: Saldo pendiente global
        - cuotas_pagadas: Cantidad de cuotas cubiertas
    """
    from ..repositories.pago_compra_repository import \
        obtenerTotalPagadoPorCompraId

    # Obtener total pagado (suma de montos de pagos activos)
    total_pagado = await obtenerTotalPagadoPorCompraId(id_compra) or 0
    
    # Procesar cuotas con FIFO
    resultado = await recalcular_estado_cuotas(id_compra, float(total_pagado))
    
    return {
        'id_compra': id_compra,
        'total_pagado': resultado['total_pagado'],
        'total_deuda': resultado.get('total_deuda', 0),
        'cuotas': resultado['cuotas'],
        'saldo_pendiente': resultado['saldo_pendiente'],
        'cuotas_pagadas': resultado.get('cuotas_pagadas', 0),
    }
