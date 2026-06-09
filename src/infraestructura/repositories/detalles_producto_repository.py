from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.detalles_producto import detalles_producto


async def obtenerDetalleProducto(filtros= None, limite= 100, offset= 0, columnas= "*", include_producto: bool = False):
    # Si se solicita incluir producto, usamos la columna específica con la relación
    # pero excluyendo detalles_producto del producto para evitar ciclos
    if include_producto:
        columnas = '*, id_productofk:productos(id,nombre,impuesto,pesable,costeo,unidad_medida,id_categoriafk,id_marcafk,descripcion,estado,perecedero,es_ingrediente,es_comida,categorias(id,nombre),marcas(id,nombre))'
    return await get('detalles_producto', filtros, limite, offset, columns=columnas)

async def actualizarDetalleProducto(datos: Union[detalles_producto, dict], cod_barra: Optional[int] = None):
    payload = prepararPayloadDb(datos)

    # Asegurar que id_productofk venga siempre (BD lo exige como NOT NULL)
    if payload.get('id_productofk') is None:
        raise ValueError('id_productofk es requerido para insertar/actualizar detalles_producto')

    if cod_barra is None:
        return await insert('detalles_producto', payload)
    return await update('detalles_producto', cod_barra, payload, key='cod_barra')
