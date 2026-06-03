from typing import Any

from src.infraestructura.repositories.detalle_precio_repository import \
    obtenerDetallePrecio
from src.infraestructura.services.precio_service import obtener_precios
from src.infraestructura.services.producto_service import (obtener_producto,
                                                           obtener_productos)


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

    detalle_precios = await obtenerDetallePrecio(filtros={'detalles_producto_cod': codigos})
    if not detalle_precios:
        for detalle in detalles:
            detalle['precios'] = []
        return detalles

    precio_ids = [rel.get('precio_id') for rel in detalle_precios if rel.get('precio_id') is not None]
    precios = await obtener_precios({'id': precio_ids}) if precio_ids else []
    precio_map = {precio['id']: precio for precio in (precios or [])}

    precios_por_codigo: dict[Any, list[dict]] = {}
    for relacion in detalle_precios:
        codigo = relacion.get('detalles_producto_cod')
        precio_id = relacion.get('precio_id')
        precio_obj = precio_map.get(precio_id)
        if codigo is None or precio_obj is None:
            continue
        precios_por_codigo.setdefault(codigo, []).append(precio_obj)

    for detalle in detalles:
        detalle['precios'] = precios_por_codigo.get(detalle.get('cod_barra'), [])

    return detalles


async def obtener_productos_con_detalles(filtros: dict = None):
    columnas = '*, marcas(id_marcafk:id, marca_nombre:nombre, marca_estado:estado), detalles_producto(*)'
    productos = await obtener_productos(filtros, columnas)
    if not productos:
        return productos

    for producto in productos:
        detalles = producto.get('detalles_producto') or []
        await attach_precios_a_detalles(detalles)

    return productos


async def obtener_producto_con_detalles(id: int):
    producto = await obtener_producto(id, include_detallesProducto=True)
    producto = _extraer_producto_unico(producto)
    if not producto:
        return producto

    detalles = producto.get('detalles_producto') or []
    await attach_precios_a_detalles(detalles)
    return producto
