from datetime import datetime, timezone
from typing import Optional

from ..repositories.cuota_venta_repository import (actualizarCuotaVenta,
                                                   obtenerCuotasPorVentaId)

ESTADO_INACTIVO = 0
ESTADO_ACTIVO = 1

async def crear_cuotas_para_venta(
    id_venta: int,
    total_cuotas: int,
    monto_cuota: float,
    fecha_inicio: datetime,
    id_usuariofk: Optional[int] = None,
    descuento: float = 0,
    interes: int = 0,
) -> list[dict]:
    """Genera las cuotas para una venta a crédito.
    
Args:
        id_venta: ID de la venta
        total_cuotas: Número total de cuotas (ej. 12 para un año)
        monto_cuota: Monto de cada cuota
        fecha_inicio: Fecha de la primera cuota
        id_usuariofk: ID del usuario que crea las cuotas
        descuento: Descuento aplicado por cuota
        interes: Porcentaje de interés

    Returns:
        Lista de cuotas criadas
    """
    cuotas_creadas = []
    
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
            'id_ventafk': id_venta,
            'id_usuariofk': id_usuariofk,
        }
        
        cuota = await actualizarCuotaVenta(cuota_data)
        cuotas_creadas.append(cuota)
    
    return cuotas_creadas


async def obtener_cuotas_por_venta(id_venta: int) -> list[dict]:
    """Obtiene las cuotas de una venta ordenadas por fecha."""
    return await obtenerCuotasPorVentaId(id_venta)


async def actualizar_estado_cuota(id_cuota: int, nuevo_estado: int) -> dict:
    """Actualiza el estado activo/inactivo de una cuota.
    
    Nota: Esto solo cambia si la cuota está activa o inactiva,
    no indica si está pagada.
    """
    return await actualizarCuotaVenta({'estado': nuevo_estado}, id_cuota)


async def recalcular_estado_cuotas(id_venta: int, total_pagado: float) -> dict:
    """Calcula el estado de las cuotas según la lógica FIFO.
    
    El estado "pagada" se calcula DINÁMICAMENTE según la cantidad de
    registros en pagos_venta, NO se almacena en la base de datos.
    
    Lógica FIFO:
    - Se ordenan las cuotas por fecha (más antigua primero)
    - Cada pago registrada cubre la siguiente cuota pendiente
    - Si hay 3 pagos, las primeras 3 cuotas estão pagadas
    
    Args:
        id_venta: ID de la venta
        total_pagado: Total de dinero pagado (solo para referencia)
    
    Returns:
        Dict con:
        - cuotas: Lista de cuotas con estado calculado
        - saldo_pendiente: Saldo pendiente global
        - total_pagado: Total pagado
        - total_deuda: Total de la deuda
    """
    from ..repositories.pago_venta_repository import obtenerPagosPorVentaId

    # Obtener cuotas activas ordenadas por fecha
    cuotas = await obtenerCuotasPorVentaId(id_venta)
    
    # Filtrar solo cuotas activas
    cuotas = [c for c in cuotas if c.get('estado', 1) == 1]
    
    if not cuotas:
        return {
            'cuotas': [],
            'saldo_pendiente': 0,
            'total_pagado': total_pagado,
            'total_deuda': 0,
            'cuotas_pagadas': 0,
        }
    
    # Contar pagos activos (cada pago = 1 cuota pagada)
    pagos = await obtenerPagosPorVentaId(id_venta)
    cantidad_pagos = sum(1 for p in (pagos or []) if p.get('estado', 1) == 1)
    
    # Calcular total de las cuotas activas
    total_deuda = sum(float(c.get('monto', 0) or 0) for c in cuotas)
    
    # Procesar cada cuota con lógica FIFO
    cuotas_procesadas = []
    for idx, cuota in enumerate(cuotas):
        id_cuota = cuota.get('id')
        monto_cuota = float(cuota.get('monto', 0) or 0)
        
        # FIFO: si el índice es menor que la cantidad de pagos, está pagada
        if idx < cantidad_pagos:
            pagada = True
            monto_cubierto = monto_cuota
        else:
            pagada = False
            monto_cubierto = 0
        
        # NO actualizamos el campo estado en la BD
        # El estado activo/inactivo se mantiene igual
        
        cuotas_procesadas.append({
            'id': id_cuota,
            'monto_original': monto_cuota,
            'monto_cubierto': monto_cubierto,
            'saldo_restante': max(0, monto_cuota - monto_cubierto),
            'pagada': pagada,  # Calculado dinámicamente, NO de la BD
            'fecha': cuota.get('fecha'),
            'estado': cuota.get('estado'),  # Esto es activo/inactivo
        })
    
    # Calcular saldo pendiente global
    cantidad_pagadas = min(cantidad_pagos, len(cuotas))
    saldo_pendiente_global = total_deuda - sum(
        float(c.get('monto', 0) or 0) 
        for c in cuotas[:cantidad_pagadas]
    )
    
    return {
        'cuotas': cuotas_procesadas,
        'saldo_pendiente': saldo_pendiente_global,
        'total_pagado': total_pagado,
        'total_deuda': total_deuda,
        'cuotas_pagadas': cantidad_pagadas,
    }


async def calcular_saldo_fifo(id_venta: int) -> dict:
    """Calcula el saldo de una venta a crédito usando lógica FIFO.
    
    Esta función es el método principal que debe llamarse desde la API.
    
    Returns:
        - id_venta: ID de la venta
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
    from ..repositories.pago_venta_repository import \
        obtenerTotalPagadoPorVentaId

    # Obtener total pagado (suma de montos de pagos activos)
    total_pagado = await obtenerTotalPagadoPorVentaId(id_venta) or 0
    
    # Procesar cuotas con FIFO
    resultado = await recalcular_estado_cuotas(id_venta, float(total_pagado))
    
    return {
        'id_venta': id_venta,
        'total_pagado': resultado['total_pagado'],
        'total_deuda': resultado.get('total_deuda', 0),
        'cuotas': resultado['cuotas'],
        'saldo_pendiente': resultado['saldo_pendiente'],
        'cuotas_pagadas': resultado.get('cuotas_pagadas', 0),
    }


async def obtener_info_cuota_venta(id_ventafk: int) -> dict:
    """Obtiene información completa de cuotas de una venta.
    
    Incluye:
    - Información de cuotas (total, pendientes, monto por cuota, pagos realizados, monto pendiente)
    - Datos de la venta con cliente incluido
    
    Args:
        id_ventafk: ID de la venta
        
    Returns:
        Dict con toda la información de cuotas y venta
    """
    from .venta_service import obtener_venta_por_id_con_detalles

    # Obtener la venta con cliente relacionado
    venta = await obtener_venta_por_id_con_detalles(
        filtros={'id': id_ventafk}
    )
    
    if not venta:
        return {
            'error': f'Veenta con ID {id_ventafk} no encontrada',
            'cuota_info': None,
            'venta': None
        }
    
    # Obtener info de cuotas con lógica FIFO
    cuota_info = await calcular_saldo_fifo(id_ventafk)
    
    # Extraer datos de cuotas
    cuotas = cuota_info.get('cuotas', [])
    
    # Calcular totales
    total_cuotas = len(cuotas)
    cuotas_pendientes = total_cuotas - cuota_info.get('cuotas_pagadas', 0)
    monto_pendiente = cuota_info.get('saldo_pendiente', 0)
    pagos_totales = cuota_info.get('total_pagado', 0)
    
    # Calcular monto de cada cuota (promedio o el valor de la primera)
    monto_cuota = 0
    if cuotas:
        monto_cuota = float(cuotas[0].get('monto_original', 0) or 0) if cuotas else 0
    
    # Construir respuesta estructurada
    result = {
        'cuota_info': {
            'total_cuotas': total_cuotas,
            'cuotas_pendientes': cuotas_pendientes,
            'monto_cuota': monto_cuota,
            'pagos_totales': pagos_totales,
            'monto_pendiente': monto_pendiente,
            'cuotas': cuotas
        },
        'venta': venta[0] if isinstance(venta, list) else venta
    }
    
    return result
