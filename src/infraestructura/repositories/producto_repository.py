from typing import Optional, Union

from src.shell.flujo.producto.actualizar_producto import actualizarDetallesDesdeProducto
from src.infraestructura.models.producto import Producto
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

    # Extraer detalles_producto por separado (no se persisten en la tabla productos directamente)
    detalles = None
    if isinstance(datos, dict):
        detalles = datos.get('detalles_producto')
    else:
        detalles = getattr(datos, 'detalles_producto', None)

    if id is None:
        producto = await insert('productos', payload)

        # Si se enviaron detalles con precios, guardarlos y vincularlos
        if detalles:
            actualizarDetallesDesdeProducto(detalles)
        return producto
    producto_actualizado = await update('productos', id, payload)

    # Si se enviaron detalles con precios al actualizar, procesarlos:
    if detalles:
        actualizarDetallesDesdeProducto(detalles)
        
    return producto_actualizado