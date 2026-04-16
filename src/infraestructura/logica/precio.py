from src.infraestructura.database.precios import actualizarPrecio, obtenerPrecio
from src.infraestructura.entidad.precio import Precio

def build_precio_entity(payload: dict) -> Precio:
    valid_fields = {key: value for key, value in payload.items() if key in Precio.__annotations__}
    return Precio(**valid_fields)

async def obtener_precios(columns: str = '*'):
    return await obtenerPrecio(columnas=columns)

async def crear_precio(payload: dict):
    precio = build_precio_entity(payload)
    return await actualizarPrecio(precio)

async def actualizar_precio(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarPrecio(payload, id)
