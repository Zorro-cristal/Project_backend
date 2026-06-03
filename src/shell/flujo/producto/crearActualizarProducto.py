from typing import Any

from src.infraestructura.repositories.producto_repository import \
    actualizarProducto
from src.shell.flujo.producto.actualizar_producto import \
    actualizarDetallesDesdeProducto


async def crear_o_actualizar_producto(datos: Any):
    detalles = datos.get('detalles_producto') if isinstance(datos, dict) else getattr(datos, 'detalles_producto', None)
    producto = await actualizarProducto(datos)
    if detalles:
        await actualizarDetallesDesdeProducto(detalles)
    return producto


async def actualizar_producto_por_id(id_producto: int, datos: Any):
    detalles = datos.get('detalles_producto') if isinstance(datos, dict) else getattr(datos, 'detalles_producto', None)
    producto_actualizado = await actualizarProducto(datos, id_producto)
    if detalles:
        await actualizarDetallesDesdeProducto(detalles)
    return producto_actualizado
