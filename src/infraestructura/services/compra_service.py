from datetime import datetime
from typing import Optional

from src.shell.utils import validar_fk_existente

from ..models.compra import Compra
from ..repositories.compra_repository import actualizarCompra, obtenerCompra
from ..repositories.detalle_compra_repository import obtenerDetalleCompra
from .detalle_compra_service import crear_detalle_compra
from .local_service import obtener_locales
from .producto_service import obtener_productos
from .proveedor_service import obtener_proveedores


def _convert_fecha(value) -> Optional[datetime]:
    """Convierte string de fecha a datetime, manteniendo datetime sin cambios."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # Soporta formatos: "2026-06-12", "2026-06-12T10:00:00", "2026-06-12 10:00:00"
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    raise ValueError(f"Formato de fecha inválido: {value}")


def build_compra_entity(payload: dict) -> Compra:
    # Convertir fecha si viene como string
    if 'fecha' in payload:
        payload = dict(payload)
        payload['fecha'] = _convert_fecha(payload.get('fecha'))
    
    valid_fields = {key: value for key, value in payload.items() if key in Compra.__annotations__}
    return Compra(**valid_fields)


async def obtener_compras(filtros: dict = None, columnas: str = '*'):
    return await obtenerCompra(filtros=filtros, columnas=columnas)


async def obtener_compra_solo(id: int, columnas: str = '*'):
    compras = await obtenerCompra(filtros={"id": id}, columnas=columnas)
    if not compras:
        return None
    if isinstance(compras, list):
        return compras[0] if compras else None
    return compras


async def obtener_compra_detalles(id: int):
    return await obtenerDetalleCompra(filtros={"id_comprafk": id})


async def crear_compra(payload: dict):
    # Extraer detalles antes de construir la entidad compra
    detalles = payload.pop('detalles', None)
    
    # Validar FKs si se proporcionan
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Crear la compra
    compra = build_compra_entity(payload)
    resultado = await actualizarCompra(compra)
    
    # Obtener el ID de la compra creada
    id_compra = resultado.get('id_compra') if resultado else None
    
    # Si hay detalles y se creó la compra, guardar cada detalle
    if detalles and id_compra:
        for detalle in detalles:
            # Validar que el producto exista
            if detalle.get('id_productofk'):
                await validar_fk_existente(
                    detalle.get('id_productofk'),
                    obtener_productos,
                    'id',
                    f"Producto con ID {detalle.get('id_productofk')} no existe",
                )
            # Asignar el ID de la compra al detalle
            detalle['id_comprafk'] = id_compra
            # Remover campos que no son parte del modelo Detalle_compra
            detalle_limpio = {k: v for k, v in detalle.items() 
                            if k in ('cantidad', 'precio', 'id_comprafk', 'id_productofk')}
            await crear_detalle_compra(detalle_limpio)
    
    return resultado


async def actualizar_compra(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    
    # Convertir fecha si viene como string
    if 'fecha' in payload:
        payload = dict(payload)
        payload['fecha'] = _convert_fecha(payload.get('fecha'))
    
    # Extraer detalles para procesarlos
    detalles = payload.pop('detalles', None)
    
    # Validar FKs si se proporcionan
    if payload.get('id_localfk'):
        await validar_fk_existente(
            payload.get('id_localfk'),
            obtener_locales,
            'id',
            f"Local con ID {payload.get('id_localfk')} no existe",
        )
    
    if payload.get('id_proveedorfk'):
        await validar_fk_existente(
            payload.get('id_proveedorfk'),
            obtener_proveedores,
            'id',
            f"Proveedor con ID {payload.get('id_proveedorfk')} no existe",
        )
    
    # Actualizar la compra
    resultado = await actualizarCompra(payload, id)
    
    # Si hay detalles, actualizar/crear cada detalle
    if detalles:
        for detalle in detalles:
            # Validar que el producto exista
            if detalle.get('id_productofk'):
                await validar_fk_existente(
                    detalle.get('id_productofk'),
                    obtener_productos,
                    'id',
                    f"Producto con ID {detalle.get('id_productofk')} no existe",
                )
            # Asignar el ID de la compra al detalle
            detalle['id_comprafk'] = id
            # Remover campos que no son parte del modelo Detalle_compra
            detalle_limpio = {k: v for k, v in detalle.items() 
                            if k in ('cantidad', 'precio', 'id_comprafk', 'id_productofk')}
            
            # Si el detalle tiene ID, actualizarlo; si no, crearlo
            if detalle.get('id'):
                from .detalle_compra_service import actualizar_detalle_compra
                await actualizar_detalle_compra(detalle['id'], detalle_limpio)
            else:
                await crear_detalle_compra(detalle_limpio)
    
    return resultado
