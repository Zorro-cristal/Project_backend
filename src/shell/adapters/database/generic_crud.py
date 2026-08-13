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
    'cuotas_venta': 'id',
    'pagos_venta': 'id',
    'cuotas_compra': 'id',
    'pagos_compra': 'id',
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
    columns: str = "*",  # Nuevo parámetro para especificar los campos a seleccionar, incluyendo relaciones
    joins: Optional[list[dict]] = None  # Parámetro para especificar JOINs
) -> list[dict]:
    """Obtiene registros de una tabla con soporte para filtros y JOINs.
    
    El parámetro `joins` permite filtrar por campos de tablas relacionadas.
    Ejemplo de uso:
        joins=[{
            'table': 'usuarios',
            'foreign_key': 'id_usuariofk',  # FK en la tabla principal (cajas)
            'primary_key': 'id',
            'name_field': 'alias',  # Campo por el cual filtrar en la tabla relacionada
            'nombre_usuario': 'juan'  # Valor a buscar
        }]
    """
    client = get_supabase_client()
    
    # Construir la consulta con columnas
    query = client.table(table).select(columns)
    
    # Aplicar filtros básicos (mismo comportamiento que antes)
    if filters:
        for field, value in filters.items():
            if isinstance(value, (list, tuple)):
                query = query.in_(field, list(value))
            elif ("inicio" in field):
                # Convención: "<col>_inicio" aplica gte contra la columna real "<col>"
                base_field = field.removesuffix("_inicio")
                query = query.gte(base_field, value)
            elif ("fin" in field):
                # Convención: "<col>_fin" aplica lte contra la columna real "<col>"
                base_field = field.removesuffix("_fin")
                query = query.lte(base_field, value)

            elif ("mostrar_inactivo" in field):
                if value == 0:
                    query = query.neq("estado", 0)  # estado != 0 (show all active records)
                # If mostrar_inactivo = 1, don't filter by estado (show all including inactive)
            else:
                query = query.eq(field, value)
    
    # Aplicar filtros de tablas relacionadas (JOINs)
    if joins:
        for join_config in joins:
            join_table = join_config.get('table')
            foreign_key = join_config.get('foreign_key')
            primary_key = join_config.get('primary_key', 'id')
            name_field = join_config.get('name_field')
            name_filter = join_config.get('nombre_usuario')
            
            if join_table and foreign_key and name_field and name_filter:
                # Primero, buscar en la tabla relacionada los IDs que coinciden con el filtro
                related_query = client.table(join_table).select(primary_key)
                
                # Aplicar filtro según el tipo de campo
                if name_field in ('alias', 'nombre', 'nombres', 'ruc', 'razon_social'):
                    # Búsqueda exacta (sensible a mayúsculas)
                    related_query = related_query.eq(name_field, name_filter)
                else:
                    # Búsqueda parcial (case-insensitive) para otros campos
                    related_query = related_query.ilike(name_field, f"%{name_filter}%")
                
                related_response = related_query.execute()
                
                if related_response.data:
                    # Obtener los IDs de la tabla relacionada
                    related_ids = [row[primary_key] for row in related_response.data]
                    
                    # Filtrar la tabla principal por esos IDs
                    query = query.in_(foreign_key, related_ids)
    
    # Ordenamiento
    if (order_by):
        query = query.order(order_by, desc=order_desc)
    if 'id' not in order_by and (table != 'detalles_producto' and table != 'personas'):
        query = query.order('id', desc=order_desc)
    
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
