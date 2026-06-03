from src.infraestructura.repositories.precio_repository import crearDetallePrecio
from src.infraestructura.services.precio_service import (
    actualizar_precio,
    crear_precio,
)


async def crear_o_actualizar_precio(payload: dict):
    payload_copy = dict(payload)
    nuevo_precio = await crear_precio(payload_copy)
    detalle_payload = {
        'id_detalleproductofk': payload_copy['id_detalleproductofk'],
        'id_preciofk': nuevo_precio.get('id'),
    }
    await crearDetallePrecio(detalle_payload)
    return nuevo_precio


async def actualizar_precio_por_id(id_precio: int, payload: dict):
    return await actualizar_precio(id_precio, payload)
