from typing import Optional, Union

from src.infraestructura.entidad.producto import Producto
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import prepare_payload_for_db, filter_none_values


async def obtenerProducto(filtros: Optional[dict] = None, limite: Optional[int]= 100, offset: Optional[int]= 0, columnas: str= "*"):
    return await get('productos', filtros, limite, offset, columns=columnas)

async def actualizarProducto(datos: Union[Producto, dict], id: Optional[int] = None):
    # Campos de Producto que son objetos o listas de objetos y no deben ser enviados directamente
    # a la tabla 'productos' (ya que tenemos sus FKs o se manejan por separado).
    fields_to_exclude_from_product_payload = ['categoria', 'marca', 'detalles_producto']

    # Prepara el payload, excluyendo el 'id' y los campos de relación complejos
    payload = prepare_payload_for_db(datos, exclude_fields=fields_to_exclude_from_product_payload)

    # Si es una actualización (id no es None), filtra los valores None para no sobrescribir datos existentes.
    if id is not None:
        payload = filter_none_values(payload)

    for field in ['pesable', 'perecedero', 'es_ingrediente']:
        if field in payload and isinstance(payload[field], bool):
            payload[field] = 1 if payload[field] else 0

    if id is None:
        return await insert('productos', payload)
    return await update('productos', id, payload)