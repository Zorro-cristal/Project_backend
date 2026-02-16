from src.infraestructura.config.supabase import get_supabase_client
from typing import TypeVar, Generic, Optional, Any
from datetime import datetime

T = TypeVar('T')

async def insert(table: str, data: dict) -> dict:
    client= get_supabase_client()
    if "fecha_creado" not in data:
        data["fecha_creado"] = datetime.utcnow().isoformat()
    
    response = client.table(table).insert(data).execute()
    
    if not response.data:
        raise Exception(f"Error al insertar en {table}")
    
    return response.data[0]


async def get(
    table: str,
    filters: Optional[dict] = None,
    limit: int = 100,
    offset: int = 0,
    order_by: str = "id",
    order_desc: bool = True
) -> list[dict]:
    client = get_supabase_client()
    
    query = client.table(table).select("*")
    
    # Aplicar filtros
    if filters:
        for field, value in filters.items():
            query = query.eq(field, value)
    
    # Ordenamiento
    query = query.order(order_by, desc=order_desc)
    
    # Paginación
    response = query.range(offset, offset + limit - 1).execute()
    
    return response.data


async def update(table: str, id: str, updates: dict) -> dict:
    client = get_supabase_client()
    
    # Agregar timestamp de actualización
    updates["fecha_edit"] = datetime.utcnow().isoformat()
    
    response = client.table(table).update(updates).eq("id", id).execute()
    
    if not response.data:
        raise Exception(f"No se encontró registro con id {id} en {table}")
    
    return response.data[0]

async def soft_delete(table: str, id: str) -> dict:
    return await update(table, id, {
        "fecha_edit": datetime.utcnow().isoformat(),
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
