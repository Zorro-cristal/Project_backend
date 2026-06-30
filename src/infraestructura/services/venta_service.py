from typing import Optional

from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.venta import Venta
from ..repositories.detalle_venta_repository import obtenerDetalleVenta
from ..repositories.venta_repository import actualizarVenta, obtenerVenta
from .caja_service import obtener_cajas
from .cliente_service import obtener_clientes
from .detalle_venta_service import (actualizar_detalle_venta,
                                    crear_detalle_venta)
from .local_service import obtener_locales


def build_venta_entity(payload: dict) -> Venta:
    valid_fields = {key: value for key, value in payload.items() if key in Venta.__annotations__}
    return Venta(**valid_fields)


async def attach_related_data(ventas: list[dict]) -> list[dict]:
    # One-to-one
    ventas = await attach_related(ventas, 'id_clientefk', obtener_clientes, 'id', 'id', 'cliente')
    ventas = await attach_related(ventas, 'id_localfk', obtener_locales, 'id', 'id', 'local')
    ventas = await attach_related(ventas, 'id_cajafk', obtener_cajas, 'id', 'id', 'caja')
# One-to-many detalles
    ventas = await attach_grouped(ventas, 'id', obtenerDetalleVenta, 'id_ventafk', 'id_ventafk', 'detalles_venta')
    
    # Calcular subtotal para cada detalle y para cada venta
    for venta in ventas:
        detalles = venta.get('detalles_venta', [])
        subtotal = 0.0
        for detalle in detalles:
            # Calcular subtotal individual del detalle: (precio - descuento) * cantidad
            precio = detalle.get('precio', 0)
            descuento = detalle.get('descuento') or 0
            cantidad = detalle.get('cantidad', 0)
            detalle_subtotal = (precio - descuento) * cantidad
            detalle['subtotal'] = detalle_subtotal
            subtotal += detalle_subtotal
        venta['subtotal'] = subtotal
    
    return ventas


async def obtener_ventas(filtros: dict = None, columnas: str = '*', joins: list = None):
    """Retorna ventas con relaciones adjuntas (cliente/local/caja/detalles).
    
    Args:
        filtros: Diccionario de filtros para la consulta.
        columnas: columnas a seleccionar.
        joins: Lista de configuraciones de JOIN para filtrar por campos relacionados.
               Ejemplo: [{'table': 'usuarios', 'foreign_key': 'id_usuariofk', 'primary_key': 'id', 'name_field': 'alias', 'nombre_usuario': 'juan'}]
    """
    ventas = await obtenerVenta(filtros=filtros, columnas=columnas, joins=joins)
    if not ventas:
        return ventas
    return await attach_related_data(ventas)


async def obtener_venta_por_id_sin_detalles(filtros: dict = None, columnas: str = '*'):
    """Retorna la venta por id sin adjuntar detalle_venta."""
    venta = await obtenerVenta(filtros=filtros, columnas=columnas)
    if not venta:
        return None
    # repository suele retornar lista
    if isinstance(venta, list):
        return venta[0] if venta else None
    return venta


async def obtener_venta_por_id_con_detalles(filtros: dict = None, columnas: str = '*'):
    """Retorna la venta por id con relaciones adjuntas, incluyendo detalles."""
    venta_con_detalles = await obtener_ventas(filtros=filtros, columnas=columnas)
    if not venta_con_detalles:
        return None
    if isinstance(venta_con_detalles, list):
        return venta_con_detalles[0] if venta_con_detalles else None
    return venta_con_detalles


async def obtener_detalle_venta_por_venta_id(filtros: dict = None):
    """Conveniencia: wrapper para obtenerDetalleVenta filtrando por id_ventafk."""
    return await obtenerDetalleVenta(filtros=filtros)


async def crear_venta(payload: dict):
    await validar_fk_existente(
        payload.get('id_clientefk'),
        obtener_clientes,
        'id',
        f"Cliente con ID {payload.get('id_clientefk')} no existe",
    )
    await validar_fk_existente(
        payload.get('id_localfk'),
        obtener_locales,
        'id',
        f"Local con ID {payload.get('id_localfk')} no existe",
    )
    await validar_fk_existente(
        payload.get('id_cajafk'),
        obtener_cajas,
        'id',
        f"Caja con ID {payload.get('id_cajafk')} no existe",
    )
    
# Extraer detalles_venta antes de construir la entidad venta
    detalles_venta = payload.pop('detalles_venta', None)
    
# Crear la venta
    venta = build_venta_entity(payload)
    resultado = await actualizarVenta(venta)
    
    # Obtener el ID de la venta creada
    # El resultado puede tener 'id_venta' o 'id' dependiendo de la tabla
    id_venta = None
    if resultado:
        id_venta = resultado.get('id_venta') or resultado.get('id')
    
    # Depuración: mostrar el resultado y el ID obtenido
    print(f"[crear_venta] resultado: {resultado}")
    print(f"[crear_venta] id_venta extraído: {id_venta}")
    print(f"[crear_venta] detalles_venta: {detalles_venta}")
    
    # Si hay detalles_venta y se creó la venta, guardar cada detalle
    if detalles_venta and id_venta:
        print(f"[crear_venta] Guardando {len(detalles_venta)} detalles para venta {id_venta}")
        for detalle in detalles_venta:
            # Asignar el ID de la venta al detalle
            detalle['id_ventafk'] = id_venta
            # Si el id es 0 o no existe, crear nuevo; si tiene id, actualizar
            detalle_id = detalle.get('id')
            if detalle_id and detalle_id != 0:
                await actualizar_detalle_venta(detalle_id, detalle)
            else:
                await crear_detalle_venta(detalle)
    
    return resultado


async def actualizar_venta(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')

    await validar_fk_existente(
        payload.get('id_clientefk'),
        obtener_clientes,
        'id',
        f"Cliente con ID {payload.get('id_clientefk')} no existe",
    )
    await validar_fk_existente(
        payload.get('id_localfk'),
        obtener_locales,
        'id',
        f"Local con ID {payload.get('id_localfk')} no existe",
    )
    await validar_fk_existente(
        payload.get('id_cajafk'),
        obtener_cajas,
        'id',
        f"Caja con ID {payload.get('id_cajafk')} no existe",
    )
    
# Extraer detalles_venta para procesarlos
    detalles_venta = payload.pop('detalles_venta', None)
    
    # Extraer cuotas y pagos si existen
    cuotas = payload.pop('cuotas', None)
    pagos = payload.pop('pagos', None)
    
    # Actualizar la venta
    resultado = await actualizarVenta(payload, id)
    
    # Si hay detalles_venta, procesar cada detalle con el ID de la venta
    if detalles_venta:
        for detalle in detalles_venta:
            detalle['id_ventafk'] = id
            # Si el id es 0 o no existe, crear nuevo; si tiene id, actualizar
            detalle_id = detalle.get('id')
            if detalle_id and detalle_id != 0:
                await actualizar_detalle_venta(detalle_id, detalle)
            else:
                await crear_detalle_venta(detalle)
    
    return resultado


# Funciones para ventas con pagos y cuotas (FIFO)

async def crear_venta_contado(payload: dict) -> dict:
    """Crea una venta al contado y registra el pago automáticamente.
    
    Proceso:
    1. Crear la venta
    2. Registrar el pago en pagos_venta con tipo=1 (Entrega) por el valor total
    """
    from .pago_venta_service import registrar_pago_contado

    # Extraer información de la venta
    detalles_venta = payload.pop('detalles_venta', None)
    monto_total = payload.pop('monto_total', None)
    id_cajafk = payload.get('id_cajafk')
    
    # Validar monto_total
    if monto_total is None:
        raise ValueError('Para ventas al contado se requiere monto_total')
    
    # Validar caja
    await validar_fk_existente(
        id_cajafk,
        obtener_cajas,
        'id',
        f"Caja con ID {id_cajafk} no existe",
    )
    
    # Establecer tipo_credito = 0 (contado)
    payload['tipo_credito'] = 0
    
    # Crear la venta
    resultado = await crear_venta(payload)
    
    # Obtener ID de la venta creada
    id_venta = resultado.get('id_venta') or resultado.get('id')
    
    # Registrar el pago (tipo=1 Entrega)
    await registrar_pago_contado(
        id_venta=id_venta,
        monto_total=monto_total,
        id_cajafk=id_cajafk,
    )
    
    # Si hay detalles_venta, guardarlos
    if detalles_venta:
        for detalle in detalles_venta:
            detalle['id_ventafk'] = id_venta
            await crear_detalle_venta(detalle)
    
    return {
        'venta': resultado,
        'pago_registrado': True,
        'tipo': 'contado',
    }


async def crear_venta_credito(payload: dict) -> dict:
    """Crea una venta a crédito y genera las cuotas automáticamente.
    
    Proceso:
    1. Crear la venta con tipo_credito=1
    2. Generar las cuotas en cuotas_venta
    """
    from .cuota_venta_service import crear_cuotas_para_venta

    # Extraer información de cuotas
    detalles_venta = payload.pop('detalles_venta', None)
    total_cuotas = payload.pop('total_cuotas', None)
    monto_cuota = payload.pop('monto_cuota', None)
    fecha_inicio = payload.pop('fecha_inicio', None)
    descuento = payload.pop('descuento', 0)
    interes = payload.pop('interes', 0)
    
    # Validar datos necesarios para crédito
    if total_cuotas is None:
        raise ValueError('Para ventas a crédito se requiere total_cuotas')
    if monto_cuota is None:
        raise ValueError('Para ventas a crédito se requiere monto_cuota')
    if fecha_inicio is None:
        raise ValueError('Para ventas a crédito se requiere fecha_inicio')
    
    # Establecer tipo_credito = 1 (crédito)
    payload['tipo_credito'] = 1
    
    # Crear la venta
    resultado = await crear_venta(payload)
    
    # Obtener ID de la venta creada
    id_venta = resultado.get('id_venta') or resultado.get('id')
    
    # Generar las cuotas
    cuotas = await crear_cuotas_para_venta(
        id_venta=id_venta,
        total_cuotas=total_cuotas,
        monto_cuota=monto_cuota,
        fecha_inicio=fecha_inicio,
        descuento=descuento,
        interes=interes,
    )
    
    # Si hay detalles_venta, guardarlos
    if detalles_venta:
        for detalle in detalles_venta:
            detalle['id_ventafk'] = id_venta
            await crear_detalle_venta(detalle)
    
    return {
        'venta': resultado,
        'cuotas_generadas': len(cuotas),
        'tipo': 'credito',
    }

