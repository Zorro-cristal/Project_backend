from src.infraestructura.config.supabase import get_supabase_client
from typing import Any, Generic, Optional, TypeVar
from datetime import datetime, timezone # Importar timezone

T = TypeVar('T')

async def insert(table: str, data: dict) -> dict:
    client= get_supabase_client()
    print(datetime.now(timezone.utc).isoformat())
    if "fecha_creado" not in data:
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
            if ("inicio" in field):
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


async def update(table: str, id: str, updates: dict) -> dict:
    client = get_supabase_client()
    
    # Agregar timestamp de actualización
    updates["fecha_edit"] = datetime.now(timezone.utc).isoformat() # Usar datetime.now(timezone.utc)
    
    response = client.table(table).update(updates).eq("id", id).execute()
    
    if not response.data:
        raise Exception(f"No se encontró registro con id {id} en {table}")
    
    return response.data[0]

async def soft_delete(table: str, id: str) -> dict:
    return await update(table, id, {
        "fecha_edit": datetime.now(timezone.utc).isoformat(), # Usar datetime.now(timezone.utc)
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
