from datetime import datetime, timezone  # Importar timezone
from typing import Any, Generic, Optional, TypeVar

from src.infraestructura.config.supabase import get_supabase_client

T = TypeVar('T')

TABLE_PRIMARY_KEYS = {
    'personas': 'cedula',
    'roles': 'id',
    'permisos': 'id',
    'permisos_roles': 'id',
    'marcas': 'id',
    'categorias': 'id',
    'precios': 'id',
    'productos': 'id',
    'detalles_producto': 'cod_barra',
    'detalles_precio': 'id',
    'ingredientes': 'id',
    'usuarios': 'id',
    'proveedores': 'id',
    'clientes': 'id',
    'vendedores': 'id',
    'locales': 'id',
    'mesas': 'id',
    'stocks': 'id',
    'cajas': 'id',
    'ventas': 'id_venta',
    'detalle_venta': 'id_detalle_venta',
    'compras': 'id_compra',
    'detalle_compra': 'id_detalle_compra',
    'ordenes': 'id',
}


def _detect_primary_key(table: str, data: dict) -> Optional[str]:
    key = TABLE_PRIMARY_KEYS.get(table)
    if key and key in data:
        return key
    return None


async def insert(table: str, data: dict) -> dict:
    client = get_supabase_client()
    primary_key = _detect_primary_key(table, data)

    if primary_key is not None:
        key_value = data.get(primary_key)
        if key_value is not None:
            existing = client.table(table).select(primary_key).eq(primary_key, key_value).limit(1).execute()
            if existing.data:
                return await update(table, key_value, data, key=primary_key)

    if "fecha_creado" not in data or data.get("fecha_creado") is None:
        data["fecha_creado"] = datetime.now(timezone.utc).isoformat()

    response = client.table(table).insert(data).execute()

    if not response.data:
        raise Exception(f"Error al insertar en {table}")

    return response.data[0]


async def get(
    table: str,
    filters: Optional[dict] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = None,
    order_desc: bool = True,
    columns: str = "*" # Nuevo parámetro para especificar los campos a seleccionar, incluyendo relaciones
) -> list[dict]:
    client = get_supabase_client()
    
    query = client.table(table).select(columns)
    
    # Aplicar filtros
    if filters:
        for field, value in filters.items():
            if isinstance(value, (list, tuple)):
                query = query.in_(field, list(value))
            elif ("inicio" in field):
                query = query.gte(field, value)
            elif ("fin" in field):
                query = query.lte(field, value)
            else:
                query = query.eq(field, value)
    
    # Ordenamiento
    if (order_by):     
        query = query.order(order_by, desc=order_desc)
    
    # Paginación
    response = query.range(offset, offset + limit - 1).execute()
    
    return response.data


async def update(table: str, id: str, updates: dict, key: str = 'id') -> dict:
    client = get_supabase_client()
    

    
    response = client.table(table).update(updates).eq(key, id).execute()
    
    if not response.data:
        raise Exception(f"No se encontró registro con {key} {id} en {table}")
    
    return response.data[0]

async def soft_delete(table: str, id: str) -> dict:
    return await update(table, id, {
        "estado": 'inactivo'
    })



async def count(table: str, filters: Optional[dict] = None) -> int:
    client = get_supabase_client()
    
    query = client.table(table).select("*", count="exact")
    
    if filters:
        for field, value in filters.items():
            query = query.eq(field, value)
    
    response = query.execute()
    return response.count
