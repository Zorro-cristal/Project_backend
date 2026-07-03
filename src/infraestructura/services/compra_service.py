from datetime import datetime, timezone
from typing import Optional

from src.shell.flujo.detalle_compra.crearActualizarDetalleCompra import \
    crear_o_actualizar_detalle_compra
from src.shell.utils import validar_fk_existente

from ..models.compra import Compra
from ..models.cuota_compra import CuotaCompra
from ..repositories.compra_repository import actualizarCompra, obtenerCompra
from ..repositories.detalle_compra_repository import obtenerDetalleCompra
from .cuota_compra_service import calcular_saldo_fifo, crear_cuotas_para_compra
from .detalle_compra_service import crear_detalle_compra
from .local_service import obtener_locales
from .pago_compra_service import registrar_pago_contado
from .producto_service import obtener_productos
from .proveedor_service import obtener_proveedores


def _convert_fecha(value) -> Optional[datetime]:
    """Convierte string de fecha a datetime, manteniendo datetime sin cambios."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Soporta formatos: "2026-06-12", "2026-06-12T10:00:00", "2026-06-12 10:00:00"
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    raise ValueError(f"Formato de fecha inválido: {value}")


def build_compra_entity(payload: dict) -> Compra:
    # Convertir fecha si viene como string
    if 'fecha' in payload:
        payload = dict(payload)
        payload['fecha'] = _convert_fecha(payload.get('fecha'))
    
    valid_fields = {key: value for key, value in payload.items() if key in Compra.__annotations__}
    return Compra(**valid_fields)


async def obtener_compras(filtros: dict = None, columnas: str = '*', joins: list = None):
    """Retorna compras con filtros opcionales.
    
    Args:
        filtros: Diccionario de filtros para la consulta.
        columnas: Columnas a seleccionar.
        joins: Lista de configuraciones de JOIN para filtrar por campos relacionados.
               Ejemplo: [{'table': 'usuarios', 'foreign_key': 'id_usuariofk', 'primary_key': 'id', 'name_field': 'alias', 'nombre_usuario': 'juan'}]
    """
    return await obtenerCompra(filtros=filtros, columnas=columnas, joins=joins)


async def obtener_compra_solo(id: int, columnas: str = '*'):
    compras = await obtenerCompra(filtros={"id": id}, columnas=columnas)
    if not compras:
        return None
    if isinstance(compras, list):
        return compras[0] if compras else None
    return compras


async def obtener_compra_detalles(id: int):
    return await obtenerDetalleCompra(filtros={"id_comprafk": id})


async def crear_compra(payload: dict):
    # Extraer detalles antes de construir la entidad compra
    detalles = payload.pop('detalles', None)
    
    # Validar FKs si se proporcionan
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Crear la compra
    compra = build_compra_entity(payload)
    resultado = await actualizarCompra(compra)
    
    # Obtener el ID de la compra creada (repo devuelve 'id' o 'id_compra')
    id_compra = (resultado.get('id_compra') or resultado.get('id')) if resultado else None
    
# Si hay detalles y se creó la compra, guardar cada detalle
    if detalles and id_compra:
        for detalle in detalles:
            # Asignar el ID de la compra al detalle
            detalle['id_comprafk'] = id_compra
            
            # Usar crear_o_actualizar_detalle_compra que crea el stock automáticamente
            await crear_o_actualizar_detalle_compra(detalle)
    
    return resultado


async def actualizar_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    
    # Convertir fecha si viene como string
    if 'fecha' in payload:
        payload = dict(payload)
        payload['fecha'] = _convert_fecha(payload.get('fecha'))
    
    # Extraer detalles para procesarlos
    detalles = payload.pop('detalles', None)
    
    # Validar FKs si se proporcionan
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Actualizar la compra
    resultado = await actualizarCompra(payload, id)
    
# Si hay detalles, actualizar/crear cada detalle
    if detalles:
        for detalle in detalles:
            # Asignar el ID de la compra al detalle
            detalle['id_comprafk'] = id
            
            # Usar crear_o_actualizar_detalle_compra que crea el stock automáticamente
            await crear_o_actualizar_detalle_compra(detalle)
    
    return resultado


# =============================================================================
# NUEVAS FUNCIONES PARA PROCESAR COMPRAS CON PAGOS (LÓGICA DE NEGOCIO FIFO)
# =============================================================================

async def crear_compra_con_pago(payload: dict) -> dict:
    """Crea una compra al contado y automáticamente registra el pago total.
    
    Reglas de Negocio:
    - tipo_credito: False (0) = Compra al contado
    - Se inserta automáticamente el pago en pagos_compra (tipo = 1, que indica pago total)
    
    Args:
        payload: Diccionario con los datos de la compra más 'id_cajafk' y opcionalmente 'id_usuariofk'
    
    Returns:
        Dict con la compra creada y el pago registrado
    """
    # Extraer datos para el pago
    id_cajafk = payload.pop('id_cajafk', None)
    id_usuariofk = payload.pop('id_usuariofk', None)
    monto_total = payload.pop('monto_total', None)
    
    if not id_cajafk:
        raise ValueError('Para compra al contado se requiere id_cajafk')
    
    if not monto_total:
        raise ValueError('Para compra al contado se requiere monto_total')
    
    # Validar FKs
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Establecer tipo_credito como falso (contado)
    payload['tipo_credito'] = 0
    
    # Crear la compra
    compra = build_compra_entity(payload)
    resultado = await actualizarCompra(compra)
    
    # Obtener el ID de la compra creada
    id_compra = resultado.get('id_compra') if resultado else None

    # Si no hay id_compra, mejor lanzar el error real (para debug)
    if not id_compra:
        raise Exception(f"Error al crear la compra: respuesta inválida -> {resultado}")
    
    # Registrar automáticamente el pago total (tipo=1 = Contado)
    pago = await registrar_pago_contado(
        id_compra=id_compra,
        monto_total=monto_total,
        id_cajafk=id_cajafk,
        id_usuariofk=id_usuariofk,
    )
    
    return {
        'compra': resultado,
        'pago': pago,
        'tipo': 'contado',
    }


async def crear_compra_a_credito(payload: dict) -> dict:
    """Crea una compra a crédito y genera las cuotas.
    
    Reglas de Negocio:
    - tipo_credito: True (1) = Compra a crédito
    - Se generan las filas en cuotas_compra según total_cuotas
    - Los pagos posteriores se registrarn en pagos_compra (tipo = 2)
    
    Args:
        payload: Diccionario con los datos de la compra más:
            - id_cajafk: ID de la caja
            - monto_total: (opcional) Total de la compra. Si no se envía, se calcula desde `detalles`
            - total_cuotas: Número de cuotas (ej. 12)
            - fecha_inicio_cuota: Fecha de la primera cuota (opcional, por defecto hoy)
            - descuento_cuota: Descuento por cuota (opcional)
            - interes_cuota: Interés por cuota en porcentaje (opcional)
            - id_usuariofk: ID del usuario (opcional)
    
    Returns:
        Dict con la compra creada y las cuotas generadas
    """
    from calendar import monthrange

    # Extraer datos para las cuotas
    id_cajafk = payload.pop('id_cajafk', None)
    id_usuariofk = payload.pop('id_usuariofk', None)
    monto_total = payload.pop('monto_total', None)
    monto_entrega_raw = payload.pop('monto_entrega', 0) or 0
    monto_entrega = float(monto_entrega_raw)
    total_cuotas = payload.pop('total_cuotas', 1)
    fecha_inicio_str = payload.pop('fecha_inicio_cuota', None)
    descuento_cuota = payload.pop('descuento_cuota', 0)
    interes_cuota = payload.pop('interes_cuota', 0)

    if not id_cajafk:
        raise ValueError('Para compra a crédito se requiere id_cajafk')

    # Si no se envía monto_total, calcularlo desde detalles (precio, descuento, cantidad)
    if monto_total is None:
        detalles = payload.get('detalles') or []
        if not detalles:
            raise ValueError('Para compra a crédito se requiere monto_total o detalles para calcularlo')

        monto_total_calc = 0.0
        for d in detalles:
            precio = float(d.get('precio') or 0)
            descuento_detalle = float(d.get('descuento') or 0)
            cantidad = float(d.get('cantidad') or 0)
            monto_total_calc += (precio - descuento_detalle) * cantidad

        monto_total = monto_total_calc

    if total_cuotas < 1:
        raise ValueError('total_cuotas debe ser mayor a 0')
    
    # Validar FKs
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Establecer tipo_credito como verdadero (crédito)
    payload['tipo_credito'] = 1
    # Reinyectar id_cajafk al payload porque luego se usa build_compra_entity(payload)
    payload['id_cajafk'] = id_cajafk

    # Asegurar que monto_entrega viaje a Supabase con el valor correcto
    payload['monto_entrega'] = float(monto_entrega)
    
    # Crear la compra
    compra = build_compra_entity(payload)
    resultado = await actualizarCompra(compra)
    
    # Obtener el ID de la compra creada (repo devuelve 'id' o 'id_compra')
    id_compra = (resultado.get('id_compra') or resultado.get('id')) if resultado else None

    if not id_compra:
        raise Exception(f"Error al crear la compra: respuesta inválida -> {resultado}")
    

    # Calcular monto por cuota sobre la DEUDA (total - entrega)
    monto_deuda = max(0.0, float(monto_total) - float(monto_entrega))
    monto_cuota = monto_deuda / float(total_cuotas)
    
    # Determinar fecha de inicio de las cuotas
    if fecha_inicio_str:
        fecha_inicio = _convert_fecha(fecha_inicio_str)
    else:
        fecha_inicio = datetime.now(timezone.utc)
    
    # Generar las cuotas
    cuota_base = CuotaCompra(
        id_comprafk=id_compra,
        total_cuotas=int(total_cuotas),
        monto_cuota=monto_cuota,
        fecha_inicio=fecha_inicio,
        id_usuariofk=id_usuariofk,
        descuento=descuento_cuota,
        interes=interes_cuota,
    )
    cuotas = await crear_cuotas_para_compra(cuota_base)
    
    return {
        'compra': resultado,
        'cuotas': cuotas,
        'tipo': 'credito',
        'total_cuotas': total_cuotas,
        'monto_cuota': monto_cuota,
    }


async def calcular_saldo_compra(id_compra: int) -> dict:
    """Calcula el saldo de una compra a crédito usando lógica FIFO.
    
    Esta función es el método principal para obtener el estado de una compra:
    - Suma todos los pagos en pagos_compra asociados a la compra
    - Distribuye el total entre las cuotas (de la más antigua a la más nueva)
    - Actualiza el estado de las cuotas saldadas
    - Devuelve el saldo restante global y el estado de cada cuota
    
    Args:
        id_compra: ID de la compra a crédito
    
    Returns:
        Dict con:
        - id_compra: ID de la compra
        - total_pagado: Total de dinero pagado
        - total_deuda: Total de la deuda original
        - cuotas: Lista de cuotas con estado calculado
        - saldo_pendiente: Saldo pendiente global
        - cuotas_pagadas: Cantidad de cuotas cubiertas
    """
    return await calcular_saldo_fifo(id_compra)
