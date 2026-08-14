from typing import Optional

from src.configs.settings import get_settings
from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica
from src.shell.utils import (attach_grouped, attach_related,
                             validar_fk_existente)

from ..models.venta import Venta
from ..repositories.detalle_venta_repository import obtenerDetalleVenta
from ..repositories.local_repository import obtenerLocal
from ..repositories.orden_repository import \
    actualizarOrden as actualizarOrdenRepo
from ..repositories.vendedor_repository import obtenerVendedor
from ..repositories.venta_repository import actualizarVenta, obtenerVenta
from .caja_service import obtener_cajas
from .cliente_service import obtener_clientes
from .detalle_venta_service import (actualizar_detalle_venta,
                                    crear_detalle_venta)
from .local_service import obtener_locales
from .orden_stock import desreservar_stock_para_venta
from .vendedor_service import obtener_vendedores

# (Deprecated) Antes se calculaba cod_num por "max" en ventas (NO es seguro ante concurrencia).
# Ahora se obtiene desde lógica de servidor (`timbrado_service`) en vez de RPC.


async def obtener_clima_para_venta_por_local(id_localfk: int):
    """Obtiene información climática actual para registrar en la venta usando coordenadas del local.

    La coordenadas provienen de la tabla `locales` (campos: latitud, longitud).
    """
    locales = await obtenerLocal(filtros={'id': id_localfk})
    if not locales:
        return None

    local = locales[0] if isinstance(locales, list) else locales
    latitud = local.get('latitud')
    longitud = local.get('longitud')

    # Si el local no tiene coordenadas, no romper el flujo: no se agrega clima.
    if latitud is None or longitud is None:
        return None

    clima_info = obtenerInformacionClimatica(latitud, longitud)
    if clima_info:
        print(f"[obtener_clima_para_venta_por_local] Clima obtenido: {clima_info}")
    return clima_info



def build_venta_entity(payload: dict) -> Venta:
    valid_fields = {key: value for key, value in payload.items() if key in Venta.__annotations__}
    return Venta(**valid_fields)


async def attach_related_data(ventas: list[dict]) -> list[dict]:
    # One-to-one
    ventas = await attach_related(
        ventas, "id_clientefk", obtener_clientes, "id", "id", "cliente"
    )
    ventas = await attach_related(
        ventas, "id_cajafk", obtener_cajas, "id", "id", "caja"
    )
    ventas = await attach_related(
        ventas, "id_vendedorfk", obtener_vendedores, "id", "id", "vendedor"
    )

    # One-to-many detalles
    ventas = await attach_grouped(
        ventas,
        "id",
        obtenerDetalleVenta,
        "id_ventafk",
        "id_ventafk",
        "detalles_venta",
    )

    # Calcular subtotal para cada detalle y para cada venta
    for venta in ventas:
        detalles = venta.get("detalles_venta", [])
        subtotal = 0.0
        for detalle in detalles:
            # Calcular subtotal individual del detalle: (precio - descuento) * cantidad
            precio = detalle.get("precio", 0)
            descuento = detalle.get("descuento") or 0
            cantidad = detalle.get("cantidad", 0)
            detalle_subtotal = (precio - descuento) * cantidad
            detalle["subtotal"] = detalle_subtotal
            subtotal += detalle_subtotal
        venta["subtotal"] = subtotal

    return ventas


async def obtener_ventas(filtros: dict = None, columnas: str = '*', joins: list = None, limite: int = 100, offset: int = 0):
    """Retorna ventas con relaciones adjuntas (cliente/local/caja/detalles).
    
    Args:
        filtros: Diccionario de filtros para la consulta.
        columnas: columnas a seleccionar.
        joins: Lista de configuraciones de JOIN para filtrar por campos relacionados.
               Ejemplo: [{'table': 'usuarios', 'foreign_key': 'id_usuariofk', 'primary_key': 'id', 'name_field': 'alias', 'nombre_usuario': 'juan'}]
    """
    ventas = await obtenerVenta(filtros=filtros, columnas=columnas, joins=joins, limit=limite, offset=offset)
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
    # Al crear una venta, la PK `ventas.id` es identity/auto-increment.
    # Si el cliente envía `id` (aunque sea 0/1), el INSERT fallará con PK duplicada.
    payload.pop('id', None)

    # Debug para verificar que nunca persiste un id desde el request

    # print(f"[crear_venta] payload.id={payload.get('id')} payload keys={list(payload.keys())}")

    # Auto-generar cod_num e id_secuencias_ventafk
    # utilizando lógica de servidor (timbrado_service) en vez de RPC.
    if payload.get('cod_num') is None:
        id_localfk = payload.get('id_localfk')
        id_vendedorfk = payload.get('id_vendedorfk')
        if id_localfk and id_vendedorfk:
            from .timbrado_service import \
                emitir_cod_num_venta as emitir_cod_num_venta_srv
            try:
                row = await emitir_cod_num_venta_srv(id_local=id_localfk, id_vendedor=id_vendedorfk)

                payload['cod_num'] = row.get('cod_num_completo')

                # Asegurar que el FK obligatorio NO quede en NULL
                id_sec = (
                    row.get('id_secuencia')
                    or row.get('id')
                    or row.get('id_secuencias_ventafk')
                )

                # Fallback definitivo: si el row no trae id de secuencia,
                # lo consultamos por la PK compuesta de secuencias_venta.
                if id_sec is None:
                    from src.shell.adapters.database.generic_crud import \
                        get as get_crud
                    id_timbrado = row.get('id_timbrado')
                    if id_timbrado is None:
                        raise ValueError(f'emitir_cod_num_venta inválida (sin id_timbrado): {row}')

                    filas = await get_crud(
                        "secuencias_venta",
                        {
                            "id_localfk": id_localfk,
                            "id_vendedorfk": id_vendedorfk,
                            "id_timbradofk": id_timbrado,
                        },
                        limit=1,
                        offset=0,
                        columns="id",
                    )
                    id_sec = filas[0].get("id") if filas else None

                payload['id_secuencias_ventafk'] = id_sec

                print(
                    f"[crear_venta] cod_num row={row} "
                    f"id_secuencias_ventafk={payload.get('id_secuencias_ventafk')} "
                    f"(local={id_localfk}, vendedor={id_vendedorfk})"
                )

                if payload.get('cod_num') is None or payload.get('id_secuencias_ventafk') is None:
                    raise ValueError(f'emitir_cod_num_venta inválida (sin id_secuencias_ventafk): {row}')

                print(f"[crear_venta] cod_num generado automáticamente: {payload['cod_num']}")
            except Exception as e:
                raise ValueError(f'Error al generar cod_num: {e}')
    
    # Obtener información climática automáticamente si no está proporcionada
    print(f"procesado? [_ya_procesado]")
    if not _ya_procesado:
        id_localfk = payload.get('id_localfk')
        clima_info = None
        if id_localfk is not None:
            clima_info = await obtener_clima_para_venta_por_local(id_localfk)

        if clima_info:
            # Agregar datos del clima a la venta si no están presentes en el payload
            if payload.get('clima') is None:
                payload['clima'] = clima_info.get('clima')
            if payload.get('temperatura') is None:
                payload['temperatura'] = clima_info.get('temperatura')
            if payload.get('humedad') is None:
                payload['humedad'] = clima_info.get('humedad')
            if payload.get('velocidad_viento') is None:
                payload['velocidad_viento'] = clima_info.get('velocidad_viento')
            if payload.get('lluvia') is None:
                payload['lluvia'] = clima_info.get('lluvia')
            if payload.get('precipitaciones') is None:
                payload['precipitaciones'] = clima_info.get('precipitaciones')
            # Nota: se elimina el campo venta.probabilidad_precipitaciones
            # para que no se persista en BD.
            print(f"[crear_venta] Clima agregado automáticamente: {clima_info}")

    
    # Compatibilidad de autoría:
    # - La API/negocio quiere guardar en ventas: id_vendedorfk (vendedor que crea).
    # - Pero si la tabla/BD exige id_usuariofk (NOT NULL) y no viene en payload,
    #   lo derivamos desde vendedores.id_usuariofk.
    if payload.get("id_usuariofk") is None and payload.get("id_vendedorfk") is not None:
        id_vendedorfk = payload.get("id_vendedorfk")
        try:
            vendedores = await obtenerVendedor(filtros={"id": id_vendedorfk})
            if vendedores:
                vendedor = vendedores[0] if isinstance(vendedores, list) else vendedores
                if vendedor.get("id_usuariofk") is not None:
                    payload["id_usuariofk"] = vendedor.get("id_usuariofk")
        except Exception:
            # Si no se puede resolver, se deja que la BD arroje error (evita ocultar fallos).
            pass

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
    # Nota: ventas NO tiene id_cajafk en el esquema (ver bdd.sql).
    # id_cajafk se usa para registrar pagos en pagos_venta (no para insertar en ventas).
    payload.pop('id_cajafk', None)

# Evitar persistir ids que ya no existen en la tabla `ventas`
    payload.pop('id_localfk', None)
    payload.pop('id_vendedorfk', None)

# Extraer detalles_venta antes de construir la entidad venta
# Si ya fueron extraídos por crear_venta_contado/crear_venta_credito, usarlos; si no, extraer del payload
    if _detalles_venta_extraidos is not None:
        detalles_venta = _detalles_venta_extraidos
    else:
        detalles_venta = payload.pop('detalles_venta', None)
    
    # Crear la venta
    print(
        f"[crear_venta] payload final para ventas: "
        f"id_secuencias_ventafk in payload={'id_secuencias_ventafk' in payload} "
        f"valor={payload.get('id_secuencias_ventafk')}"
    )
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

        # Calcular y persistir ocupación de mesa (ventas.ocupacion) una sola vez por venta
        ocupacion_persistida = False
        id_orden_para_ocupacion = None
        for detalle in detalles_venta:
            if not ocupacion_persistida:
                id_orden_para_ocupacion = detalle.get('id_ordenfk')
                if id_orden_para_ocupacion is not None:
                    break

        # Prioridad: usar id_mesafk enviado en el POST (payload) si existe.
        # Si no viene, caemos al comportamiento anterior derivándolo desde ordenes.id_mesafk.
        id_mesafk_from_payload = payload.get('id_mesafk')
        # Evitar que se intente persistir este campo no existente en la tabla `ventas`.
        payload.pop('id_mesafk', None)

        if (id_mesafk_from_payload is not None) or (id_orden_para_ocupacion is not None):
            try:
                id_mesafk = id_mesafk_from_payload

                import logging
                logging.getLogger(__name__).info(
                    f"[crear_venta] id_mesafk_from_payload={id_mesafk_from_payload} id_orden_para_ocupacion={id_orden_para_ocupacion}"
                )

                # Backward compatibility: si no viene por payload, obtener desde la orden
                if id_mesafk is None and id_orden_para_ocupacion is not None:
                    ordenes = await obtenerOrdenes(
                        filtros={'id': id_orden_para_ocupacion},
                        columnas='id_mesafk',
                    )
                    orden = ordenes[0] if isinstance(ordenes, list) else ordenes
                    id_mesafk = None if not orden else orden.get('id_mesafk')

                # Obtener ocupado_desde desde la mesa y calcular ocupación
                if id_mesafk is not None:
                    from ..repositories.mesa_repository import \
                        obtenerMesa as obtener_mesa_repo

                    mesas = await obtener_mesa_repo(
                        filtros={'id': id_mesafk},
                        columnas='ocupado_desde',
                        limite=1,
                        offset=0,
                    )
                    mesa = mesas[0] if isinstance(mesas, list) else mesas
                    ocupado_desde = None if not mesa else mesa.get('ocupado_desde')

                    if ocupado_desde:
                        from datetime import datetime as _dt
                        from datetime import time as _time
                        from datetime import timedelta as _td

                        if isinstance(ocupado_desde, _time):
                            start_time = ocupado_desde
                        else:
                            parts = str(ocupado_desde).split(':')
                            hh = int(parts[0]) if len(parts) > 0 else 0
                            mm = int(parts[1]) if len(parts) > 1 else 0
                            ss = int(parts[2]) if len(parts) > 2 else 0
                            start_time = _time(hour=hh, minute=mm, second=ss)

                        now = _dt.now()
                        start_dt = _dt.combine(now.date(), start_time)
                        dur = now - start_dt
                        if dur.total_seconds() < 0:
                            dur = dur + _td(days=1)

                        total_seconds = int(dur.total_seconds())
                        horas = total_seconds // 3600
                        minutos = (total_seconds % 3600) // 60
                        segundos = total_seconds % 60
                        horas = horas % 24
                        ocupacion_time_str = f"{horas:02d}:{minutos:02d}:{segundos:02d}"

                        await actualizarVenta({'ocupacion': ocupacion_time_str}, id_venta)
                        ocupacion_persistida = True
            except Exception as exc:
                import logging
                logging.getLogger(__name__).exception(f"[crear_venta] No se pudo calcular ocupacion: {exc}")


        for detalle in detalles_venta:
            # Asignar el ID de la venta al detalle
            detalle['id_ventafk'] = id_venta
            # Si el id es 0 o no existe, crear nuevo; si tiene id, actualizar
            detalle_id = detalle.get('id')
            if detalle_id and detalle_id != 0:
                await actualizar_detalle_venta(detalle_id, detalle)
            else:
                await crear_detalle_venta(detalle)

            # 1) Cambiar ordenes.estado a 5 (a cobrado)
            id_ordenfk = detalle.get('id_ordenfk')
            if id_ordenfk is not None:
                await actualizarOrdenRepo({'estado': 5}, id_ordenfk)

            # 2) Desreservar stock: restar cantidad desde stocks.cant_reservado
            id_detalleproductofk = detalle.get('id_detalleproductofk')
            cantidad_detalle = detalle.get('cantidad')
            if id_detalleproductofk is not None and cantidad_detalle is not None:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(
                    f"[crear_venta] Desreservar -> id_ordenfk={id_ordenfk}, "
                    f"id_detalleproductofk={id_detalleproductofk}, cantidad={cantidad_detalle}"
                )
                await desreservar_stock_para_venta(
                    id_detalleproductofk=str(id_detalleproductofk),
                    cantidad_a_liberar=int(cantidad_detalle),
                )

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
    # Nota: ventas NO tiene id_cajafk en el esquema.
    payload.pop('id_cajafk', None)

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

