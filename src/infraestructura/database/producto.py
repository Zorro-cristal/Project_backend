from typing import Optional, Union

from src.infraestructura.entidad.producto import Producto
from src.shell.adaptadores.database.generic_crud import get, insert, update
from src.shell.utils import normalizar_booleanos, prepararPayloadDb


async def obtenerProducto(filtros: Optional[dict] = None, limite: Optional[int]= 100, offset: Optional[int]= 0, columnas: str= "*"):
    return await get('productos', filtros, limite, offset, columns=columnas)

async def actualizarProducto(datos: Union[Producto, dict], id: Optional[int] = None):
    campos_excluir = ['categoria', 'marca', 'detalles_producto', 'ingredientes']

    # Prepara el payload
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
        return await insert('productos', payload)
    return await update('productos', id, payload)