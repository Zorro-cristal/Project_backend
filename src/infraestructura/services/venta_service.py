from typing import Optional

from src.configs.settings import get_settings
from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica
from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.venta import Venta
from ..repositories.detalle_venta_repository import obtenerDetalleVenta
from ..repositories.local_repository import obtenerLocal
from ..repositories.vendedor_repository import obtenerVendedor
from ..repositories.venta_repository import actualizarVenta, obtenerVenta
from .caja_service import obtener_cajas
from .cliente_service import obtener_clientes
from .detalle_venta_service import (actualizar_detalle_venta,
                                    crear_detalle_venta)
from .local_service import obtener_locales


async def generar_cod_num_venta(id_localfk: int, id_vendedorfk: int) -> str:
    """Genera automáticamente el número de factura con el patrón:
    {locales.cod_num}-{vendedores.cod_num}-{venta.cod_num}
    
    Donde venta.cod_num es el max + 1 para esa combinación de local+vendedor.
    
    Args:
        id_localfk: ID del local donde se realiza la venta
        id_vendedorfk: ID del vendedor que realiza la venta
        
    Returns:
        String con el código generado, ej: "001-002-000001"
    """
    # Obtener datos del local
    locales = await obtenerLocal(filtros={'id': id_localfk})
    if not locales:
        raise ValueError(f"Local con ID {id_localfk} no encontrado")
    local = locales[0] if isinstance(locales, list) else locales
    local_cod = local.get('cod_num') or '000'
    
    # Obtener datos del vendedor
    vendedores = await obtenerVendedor(filtros={'id': id_vendedorfk})
    if not vendedores:
        raise ValueError(f"Vendedor con ID {id_vendedorfk} no encontrado")
    vendedor = vendedores[0] if isinstance(vendedores, list) else vendedores
    vendedor_cod = vendedor.get('cod_num') or '000'
    
    # Buscar el máximo código de factura para esta combinación local+vendedor
    # Filtrar ventas por id_localfk E id_vendedorfk
    ventas_existentes = await obtenerVenta(
        filtros={
            'id_localfk': id_localfk,
            'id_vendedorfk': id_vendedorfk
        },
        columnas='cod_num'
    )
    
    max_secuencia = 0
    if ventas_existentes:
        for v in ventas_existentes:
            cod_num = v.get('cod_num')
            if cod_num:
                # El código tiene formato: {local_cod}-{vendedor_cod}-{secuencia}
                # Extraer la parte de la secuencia (últimos 6 dígitos)
                partes = cod_num.split('-')
                if len(partes) == 3:
                    try:
                        secuencia = int(partes[2])
                        if secuencia > max_secuencia:
                            max_secuencia = secuencia
                    except (ValueError, IndexError):
                        pass
    
    # Generar nuevo número de secuencia (6 dígitos con ceros a la izquierda)
    nueva_secuencia = max_secuencia + 1
    secuencia_formateada = f"{nueva_secuencia:06d}"
    
    # Construir el código completo
    codigo_completo = f"{local_cod}-{vendedor_cod}-{secuencia_formateada}"
    
    print(f"[generar_cod_num_venta] Generado: {codigo_completo} (secuencia: {nueva_secuencia})")
    
    return codigo_completo


async def obtener_clima_para_venta():
    """Obtiene información climática actual para registrar en la venta.
    
    Utiliza las coordenadas de la empresa definidas en settings.
    """
    settings = get_settings()
    latitud = settings.EMPRESA_LATITUD
    longitud = settings.EMPRESA_LONGITUD
    
    clima_info = obtenerInformacionClimatica(latitud, longitud)
    if clima_info:
        print(f"[obtener_clima_para_venta] Clima obtenido: {clima_info}")
    return clima_info


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


async def crear_venta(payload: dict, _ya_procesado: bool = False, _detalles_venta_extraidos: list = None):
    # Auto-generar cod_num de venta si no está proporcionado y se tienen los datos necesarios
    if payload.get('cod_num') is None:
        id_localfk = payload.get('id_localfk')
        id_vendedorfk = payload.get('id_vendedorfk')
        if id_localfk and id_vendedorfk:
            try:
                cod_num_generado = await generar_cod_num_venta(id_localfk, id_vendedorfk)
                payload['cod_num'] = cod_num_generado
                print(f"[crear_venta] cod_num generado automáticamente: {cod_num_generado}")
            except Exception as e:
                print(f"[crear_venta] Error al generar cod_num: {e}")
                # Continuar sin cod_num si hay error
    
    # Obtener información climática automáticamente si no está proporcionada
    print(f"procesado? [_ya_procesado]")
    if not _ya_procesado:
        clima_info = await obtener_clima_para_venta()
        if clima_info:
            # Agregar datos del clima a la venta si no están presentes en el payload
            if payload.get('clima') is None:
                payload['clima'] = clima_info.get('clima')
            if payload.get('temperatura') is None:
                payload['temperatura'] = clima_info.get('temperatura')
            if payload.get('humedad') is None:
                payload['humedad'] = clima_info.get('humedad')
            print(f"[crear_venta] Clima agregado automáticamente: {clima_info}")
    
    # Verificar si tipo_credito está presente en el payload para rutear automáticamente
    # Solo rutear si no ha sido procesado previamente (para evitar recursión infinita)
    tipo_credito = payload.get('tipo_credito')
    
    if not _ya_procesado and tipo_credito is not None:
        # Convertir boolean a entero si es necesario
        if isinstance(tipo_credito, bool):
            tipo_credito = 1 if tipo_credito else 0
        
        if tipo_credito == 0:
            # Venta al contado - usar crear_venta_contado
            return await crear_venta_contado(payload)
        elif tipo_credito == 1:
            # Venta a crédito - usar crear_venta_credito
            return await crear_venta_credito(payload)
    
    # Si tipo_credito no está definido, continuar con el comportamiento original (backward compatibility)
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
# Si ya fueron extraídos por crear_venta_contado/crear_venta_credito, usarlos; si no, extraer del payload
    if _detalles_venta_extraidos is not None:
        detalles_venta = _detalles_venta_extraidos
    else:
        detalles_venta = payload.pop('detalles_venta', None)
    
# Crear la venta
    venta = build_venta_entity(payload)
    resultado = await actualizarVenta(venta)
    
    # Obtener el ID de la venta creado
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
    
    # Calcular monto_total automáticamente desde detalles_venta si no se proporciona
    if monto_total is None and detalles_venta:
        monto_total = 0
        for detalle in detalles_venta:
            precio = float(detalle.get('precio') or 0)
            descuento = float(detalle.get('descuento') or 0)
            cantidad = float(detalle.get('cantidad') or 0)
            monto_total += (precio - descuento) * cantidad
    
    # Validar monto_total
    if monto_total is None or monto_total <= 0:
        raise ValueError('Para ventas al contado se requiere monto_total o detalles_venta con cantidad y precio')
    
    # Validar caja
    await validar_fk_existente(
        id_cajafk,
        obtener_cajas,
        'id',
        f"Caja con ID {id_cajafk} no existe",
    )
    
    # Establecer tipo_credito = 0 (contado)
    payload['tipo_credito'] = 0
    
    # Crear la venta con _ya_procesado=True y pasar detalles_venta extraídos
    resultado = await crear_venta(payload, _ya_procesado=True, _detalles_venta_extraidos=detalles_venta)
    
    # Obtener ID de la venta creada
    id_venta = resultado.get('id_venta') or resultado.get('id')
    
    # Registrar el pago (tipo=1 Entrega)
    await registrar_pago_contado(
        id_venta=id_venta,
        monto_total=monto_total,
        id_cajafk=id_cajafk,
    )
    
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
    
    Cálculo del monto de cuotas:
    - Si se proporciona monto_entrega: monto_restante = total - monto_entrega
    - monto_cuota = monto_restante / total_cuotas
    """
    from .cuota_venta_service import crear_cuotas_para_venta

    # Extraer información de cuotas
    detalles_venta = payload.pop('detalles_venta', None)
    total_cuotas = payload.pop('total_cuotas', None)
    monto_cuota = payload.pop('monto_cuota', None)  # Opcional - se calcula si no se proporciona
    monto_entrega = payload.pop('monto_entrega', 0) or 0
    fecha_inicio = payload.pop('fecha_inicio', None)
    descuento = payload.pop('descuento', 0)
    interes = payload.pop('interes', 0)
    
    # Validar datos necesarios para crédito
    if total_cuotas is None:
        raise ValueError('Para ventas a crédito se requiere total_cuotas')
    if fecha_inicio is None:
        raise ValueError('Para ventas a crédito se requiere fecha_inicio')
    
    # Calcular monto_total automáticamente desde detalles_venta si no se proporciona
    monto_total = payload.pop('monto_total', None)
    if monto_total is None and detalles_venta:
        monto_total = 0
        for detalle in detalles_venta:
            precio = float(detalle.get('precio') or 0)
            descuento_detalle = float(detalle.get('descuento') or 0)
            cantidad = float(detalle.get('cantidad') or 0)
            monto_total += (precio - descuento_detalle) * cantidad
    
    if monto_total is None:
        raise ValueError('Para ventas a crédito se requiere monto_total o detalles_venta con cantidad y precio')
    
    # Calcular monto_restante y monto_cuota automáticamente
    monto_restante = monto_total - monto_entrega
    if monto_restante < 0:
        raise ValueError('monto_entrega no puede ser mayor que el monto_total')
    
    # Si no se proporciona monto_cuota, calcular automáticamente
    if monto_cuota is None:
        if total_cuotas <= 0:
            raise ValueError('total_cuotas debe ser mayor a 0')
        monto_cuota = monto_restante / total_cuotas
    
    # Establecer tipo_credito = 1 (crédito)
    payload['tipo_credito'] = 1
    
    # Establecer monto_entrega en payload (se guardará en la venta)
    payload['monto_entrega'] = monto_entrega
    
    # Crear la venta con _ya_procesado=True y pasar detalles_venta extraídos
    resultado = await crear_venta(payload, _ya_procesado=True, _detalles_venta_extraidos=detalles_venta)
    
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
    
    return {
        'venta': resultado,
        'cuotas_generadas': len(cuotas),
        'monto_entrega': monto_entrega,
        'monto_restante': monto_restante,
        'monto_cuota': monto_cuota,
        'tipo': 'credito',
    }

