from typing import Any

from src.infraestructura.repositories.detalle_precio_repository import \
    obtenerDetallePrecio
from src.infraestructura.services.ingrediente_service import \
    obtener_ingredientes
from src.infraestructura.services.precio_service import obtener_precios
from src.infraestructura.services.producto_service import (
    obtener_detallesProducto, obtener_producto, obtener_productos)
from src.infraestructura.services.stock_service import obtener_stocks


def _extraer_producto_unico(producto: Any) -> Any:
    if isinstance(producto, list):
        return producto[0] if producto else None
    return producto


async def attach_precios_a_detalles(detalles: list[dict]) -> list[dict]:
    if not detalles:
        return detalles

    codigos = [detalle.get('cod_barra') for detalle in detalles if detalle.get('cod_barra') is not None]
    if not codigos:
        for detalle in detalles:
            detalle['precios'] = []
        return detalles

    detalle_precios = await obtenerDetallePrecio(filtros={'id_detalleproductofk': codigos})
    if not detalle_precios:
        for detalle in detalles:
            detalle['precios'] = []
        return detalles

    precio_ids = [rel.get('id_preciofk') for rel in detalle_precios if rel.get('id_preciofk') is not None]
    precios = await obtener_precios({'id': precio_ids}) if precio_ids else []
    precio_map = {precio['id']: precio for precio in (precios or [])}

    precios_por_codigo: dict[Any, list[dict]] = {}
    for relacion in detalle_precios:
        codigo = relacion.get('id_detalleproductofk')
        precio_id = relacion.get('id_preciofk')
        precio_obj = precio_map.get(precio_id)
        if codigo is None or precio_obj is None:
            continue
        precios_por_codigo.setdefault(codigo, []).append(precio_obj)

    for detalle in detalles:
        detalle['precios'] = precios_por_codigo.get(detalle.get('cod_barra'), [])

    return detalles


def _renombrar_marca_en_producto(producto: dict) -> dict:
    if 'marcas' in producto:
        marca_supabase = producto.pop('marcas') if 'marca' not in producto else None

        if marca_supabase is not None:
            producto['marca'] = {
                'id': marca_supabase.get('id_marcafk'),
                'nombre': marca_supabase.get('marca_nombre'),
                'estado': marca_supabase.get('marca_estado'),
            }

    return producto


async def _attach_stock_a_detalles(detalles: list[dict]) -> list[dict]:
    """
    Adjunta a cada detalle_producto:
      - cant_disponible = cant_mostrador + cant_deposito
      - cant_reservada = cant_reservado
    """
    if not detalles:
        return detalles

    # `detalles_producto` trae `cod_barra`.
    # En Supabase, `stocks` no tiene `cod_barra`, por eso filtramos por `stocks.id_detalleproductofk`.
    # Además, en el código existente se usa `cod_barra` como `id_detalleproductofk` en precios, así que aquí asumimos el mismo mapeo.
    detalle_codigos = [d.get('cod_barra') for d in detalles if d.get('cod_barra') is not None]

    stocks: list[dict] = []
    if detalle_codigos:
        stocks = await obtener_stocks(
            filtros={'id_detalleproductofk': detalle_codigos},
            columnas='cant_mostrador,cant_deposito,cant_reservado,id_detalleproductofk'
        )

    # Construir mapa por id_detalleproductofk
    stock_map_by_detalle_id = {}
    for s in stocks or []:
        _detalle_id = s.get('id_detalleproductofk')
        if _detalle_id is not None:
            stock_map_by_detalle_id[_detalle_id] = s

    for detalle in detalles:
        detalle_id = detalle.get('cod_barra')  # mapeo descrito arriba
        s = stock_map_by_detalle_id.get(detalle_id) if detalle_id is not None else None

        cant_mostrador = (s or {}).get('cant_mostrador') or 0
        cant_deposito = (s or {}).get('cant_deposito') or 0
        cant_reservado = (s or {}).get('cant_reservado') or 0

        detalle['cant_disponible'] = int(cant_mostrador) + int(cant_deposito)
        detalle['cant_reservada'] = int(cant_reservado)

    return detalles


async def _attach_produccion_posible_a_detalles(productos: list[dict]) -> None:
    """
    Para productos con es_comida=true:
      - calcula cant_deposito posible según ingredientes y stock disponible
      - lo asigna a detalle_producto.cant_deposito
    """
    comida_productos = [p for p in productos if p.get('es_comida') is True]
    if not comida_productos:
        return

    producto_ids_finales = [p.get('id') for p in comida_productos if p.get('id') is not None]
    if not producto_ids_finales:
        return

    ingredientes = await obtener_ingredientes({'id_producto_finalfk': producto_ids_finales})
    ingredientes = ingredientes or []

    # Agrupar ingredientes por producto final
    ingredientes_por_final: dict[int, list[dict]] = {}
    for ing in ingredientes:
        final_id = ing.get('id_producto_finalfk')
        if final_id is None:
            continue
        ingredientes_por_final.setdefault(final_id, []).append(ing)

    # Cache: detalles + stock de cada producto ingrediente
    detalles_stock_cache: dict[int, list[dict]] = {}

    for producto in comida_productos:
        final_id = producto.get('id')
        if final_id is None:
            continue

        ingredientes_del_final = ingredientes_por_final.get(final_id) or []
        if not ingredientes_del_final:
            # Sin receta -> producción posible 0
            for d in (producto.get('detalles_producto') or []):
                d['cant_deposito'] = 0
            continue

        producciones_posibles = []
        for ing in ingredientes_del_final:
            id_ing_prod = ing.get('id_producto_ingredientefk')
            cantidad_req = ing.get('cantidad') or 0
            if id_ing_prod is None or cantidad_req in (0, None):
                continue

            # Obtener detalles del producto ingrediente y adjuntar stock
            if id_ing_prod not in detalles_stock_cache:
                detalles_ing = await obtener_detallesProducto(id_ing_prod)
                detalles_ing = detalles_ing or []
                await _attach_stock_a_detalles(detalles_ing)
                detalles_stock_cache[id_ing_prod] = detalles_ing

            detalles_ing = detalles_stock_cache[id_ing_prod]
            total_stock_disponible_ing = sum(int(d.get('cant_disponible') or 0) for d in (detalles_ing or []))

            produccion_ing = total_stock_disponible_ing // int(cantidad_req)
            producciones_posibles.append(produccion_ing)

        produccion_posible = min(producciones_posibles) if producciones_posibles else 0

        for d in (producto.get('detalles_producto') or []):
            # cantidad posible de producción se refleja como cant_deposito
            d['cant_deposito'] = int(produccion_posible)

async def obtener_productos_con_detalles(filtros: dict = None, incluir_precios: bool = True):
    columnas = '*, marcas(id_marcafk:id, marca_nombre:nombre, marca_estado:estado), detalles_producto(*)'
    productos = await obtener_productos(filtros, columnas)
    if not productos:
        return productos

    for producto in productos:
        _renombrar_marca_en_producto(producto)
        detalles = producto.get('detalles_producto') or []
        if incluir_precios:
            await attach_precios_a_detalles(detalles)
        await _attach_stock_a_detalles(detalles)

    await _attach_produccion_posible_a_detalles(productos)
    return productos


async def obtener_producto_con_detalles(id: int):
    producto = await obtener_producto(id, include_detallesProducto=True)
    producto = _extraer_producto_unico(producto)
    if not producto:
        return producto

    _renombrar_marca_en_producto(producto)

    detalles = producto.get('detalles_producto') or []
    await attach_precios_a_detalles(detalles)
    await _attach_stock_a_detalles(detalles)

    # Adjuntar ingredientes (siempre), con la info del producto referenciado
    ingredientes_raw = await obtener_ingredientes({'id_producto_finalfk': id})
    ingredientes_con_producto = []
    for ing in (ingredientes_raw or []):
        id_prod_ing = ing.get('id_producto_ingredientefk')
        if id_prod_ing is not None:
            producto_ingrediente = await obtener_producto(id_prod_ing)
            ing['producto_ingrediente'] = _extraer_producto_unico(producto_ingrediente)
        ingredientes_con_producto.append(ing)
    producto['ingredientes'] = ingredientes_con_producto

    await _attach_produccion_posible_a_detalles([producto])
    return producto
