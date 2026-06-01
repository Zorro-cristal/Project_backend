from src.infraestructura.models.precio import Precio
from src.infraestructura.repositories.precio_repository import (
    actualizarPrecio, crearDetallePrecio, crearPrecio, obtenerPrecio)


def build_precio_entity(payload: dict) -> Precio:
    valid_fields = {key: value for key, value in payload.items() if key in Precio.__annotations__}
    return Precio(**valid_fields)

async def obtener_precios(filtros: dict= None, columnas: str = '*'):
    return await obtenerPrecio(columnas=columnas, filtros=filtros)

async def crear_precio(payload: dict):
    precio = build_precio_entity(payload)
    nuevo_precio = await crearPrecio(precio)
    await crearDetallePrecio({
        'id_detalleProductofk': payload['id_detalleProductofk'],
        'id_preciofk': nuevo_precio['id']
    })
    return nuevo_precio

async def actualizar_precio(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPrecio(payload, id)
