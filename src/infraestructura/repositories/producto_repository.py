from typing import Optional, Union

from src.infraestructura.models.producto import Producto
from src.infraestructura.repositories.precio_repository import (
    actualizarPrecio, crear_precio, vincular_precio_detalle)
from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import normalizar_booleanos, prepararPayloadDb


async def obtenerProducto(filtros: Optional[dict] = None, limite: Optional[int]= 100, offset: Optional[int]= 0, columnas: str= "*"):
    return await get('productos', filtros, limite, offset, columns=columnas)


async def obtenerProductoConDetallesProducto(id: int):
    # DetallesProducto = detalles_producto asociados al producto
    return await obtenerProducto(
        filtros={"id": id},
        columnas='*, marcas(id_marcafk:id, marca_nombre:nombre, marca_estado:estado), detalles_producto(*)'
    )


async def obtenerDetallesProducto(id: int):
    # Lista de detalles_producto asociados a un producto
    return await get('detalles_producto', filters={"id_productofk": id}, limit=100, offset=0, columns='*')


async def actualizarProducto(datos: Union[Producto, dict], id: Optional[int] = None):
    campos_excluir = ['categoria', 'marca', 'detalles_producto', 'ingredientes']

    # Extraer detalles_producto por separado (no se persisten en la tabla productos directamente)
    detalles = None
    if isinstance(datos, dict):
        detalles = datos.get('detalles_producto')
    else:
        detalles = getattr(datos, 'detalles_producto', None)

    # Prepara el payload (excluye campos compuestos)
    payload = prepararPayloadDb(datos, exclude_fields=campos_excluir)

    # Si es una actualización (id no es None), filtra los valores None para no sobrescribir datos existentes.
    if id is not None:
        payload = {k: v for k, v in payload.items() if v is not None}

    payload = normalizar_booleanos(
        payload,
        ['pesable', 'perecedero', 'es_ingrediente', 'es_comida'],
        on_insert=id is None,
    )

    if id is None:
        producto = await insert('productos', payload)

        # Si se enviaron detalles con precios, guardarlos y vincularlos
        if detalles:
            for detalle in detalles:
                # obtener código de barra del detalle
                cod_barra = detalle.get('cod_barra') if isinstance(detalle, dict) else getattr(detalle, 'cod_barra', None)
                precios = detalle.get('precios') if isinstance(detalle, dict) else getattr(detalle, 'precios', None)
                if not precios:
                    continue
                for precio in precios:
                    # Crear precio y vincular al detalle
                    creado = await crear_precio(precio)
                    precio_id = creado.get('id')
                    if precio_id:
                        await vincular_precio_detalle(precio_id, cod_barra)

        return producto
    producto_actualizado = await update('productos', id, payload)

    # Si se enviaron detalles con precios al actualizar, procesarlos:
    if detalles:
        for detalle in detalles:
            cod_barra = detalle.get('cod_barra') if isinstance(detalle, dict) else getattr(detalle, 'cod_barra', None)
            precios = detalle.get('precios') if isinstance(detalle, dict) else getattr(detalle, 'precios', None)
            if not precios:
                continue
            for precio in precios:
                # Si el precio tiene id => actualizar, sino crear y vincular
                precio_id = precio.get('id') if isinstance(precio, dict) else getattr(precio, 'id', None)
                if precio_id:
                    await actualizarPrecio(precio, precio_id)
                else:
                    creado = await crear_precio(precio)
                    nuevo_id = creado.get('id')
                    if nuevo_id:
                        await vincular_precio_detalle(nuevo_id, cod_barra)

    return producto_actualizado