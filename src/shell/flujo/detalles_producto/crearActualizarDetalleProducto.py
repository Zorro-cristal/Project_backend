from src.infraestructura.services.detalles_producto_service import (
    actualizar_detalles_producto, crear_detalles_producto,
    obtener_detalles_productos)


async def crear_o_actualizar_detalle_producto(payload: dict):
    cod_barra = payload.get('cod_barra')
    if cod_barra is not None:
        existentes = await obtener_detalles_productos({'cod_barra': cod_barra})
        if existentes and len(existentes) > 0:
            return await actualizar_detalles_producto(cod_barra, payload)

    return await crear_detalles_producto(payload)


async def actualizar_detalle_producto_por_cod_barra(cod_barra: int, payload: dict):
    return await actualizar_detalles_producto(cod_barra, payload)
