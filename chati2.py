# ============================================================================
# 1. CORE/INTERFACES/REPOSITORIES/base_repository.py - Repositorio Genérico
# ============================================================================
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')

class BaseRepositoryInterface(Generic[T], ABC):
    """Interface genérica para cualquier repositorio"""
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        pass
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        pass
    
    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        pass


# ============================================================================
# 2. INFRASTRUCTURE/DATABASE/REPOSITORIES/supabase_generic_repository.py
# ============================================================================
from typing import Any, Dict, List, Optional

from supabase import Client

from src.core.interfaces.repositories.base_repository import \
    BaseRepositoryInterface


class SupabaseGenericRepository(BaseRepositoryInterface[Dict[str, Any]]):
    """Repositorio genérico para cualquier tabla de Supabase"""
    
    def __init__(self, supabase_client: Client, table_name: str):
        self.client = supabase_client
        self.table_name = table_name
    
    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = self.client.table(self.table_name).insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Obtener todos con paginación y filtros opcionales"""
        query = self.client.table(self.table_name).select("*")
        
        # Aplicar filtros si existen
        if filters:
            for key, value in filters.items():
                if isinstance(value, dict):
                    # Soportar operadores: {"$gt": 18}, {"$like": "%juan%"}
                    operator = list(value.keys())[0]
                    val = value[operator]
                    
                    if operator == "$gt":
                        query = query.gt(key, val)
                    elif operator == "$gte":
                        query = query.gte(key, val)
                    elif operator == "$lt":
                        query = query.lt(key, val)
                    elif operator == "$lte":
                        query = query.lte(key, val)
                    elif operator == "$like":
                        query = query.like(key, val)
                    elif operator == "$ilike":
                        query = query.ilike(key, val)
                else:
                    query = query.eq(key, value)
        
        # Paginación
        result = query.range(skip, skip + limit - 1).execute()
        return result.data
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualizar un registro"""
        result = self.client.table(self.table_name).update(data).eq("id", id).execute()
        return result.data[0] if result.data else None
    
    async def delete(self, id: str) -> bool:
        """Eliminar un registro"""
        result = self.client.table(self.table_name).delete().eq("id", id).execute()
        return len(result.data) > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros con filtros opcionales"""
        query = self.client.table(self.table_name).select("*", count="exact")
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.count if hasattr(result, 'count') else 0


# ============================================================================
# 3. APPLICATION/USE_CASES/generic_crud_use_case.py - Casos de Uso Genéricos
# ============================================================================
from typing import Any, Dict, List, Optional

from src.core.interfaces.repositories.base_repository import \
    BaseRepositoryInterface


class GenericCRUDUseCase:
    """Casos de uso genéricos para CRUD"""
    
    def __init__(self, repository: BaseRepositoryInterface):
        self.repository = repository
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear un nuevo registro"""
        return await self.repository.create(data)
    
    async def get_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Obtener por ID"""
        result = await self.repository.get_by_id(id)
        if not result:
            raise ValueError(f"Registro con ID {id} no encontrado")
        return result
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Listar todos con paginación"""
        return await self.repository.get_all(skip=skip, limit=limit, filters=filters)
    
    async def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar un registro"""
        # Verificar que existe
        existing = await self.repository.get_by_id(id)
        if not existing:
            raise ValueError(f"Registro con ID {id} no encontrado")
        
        result = await self.repository.update(id, data)
        return result
    
    async def delete(self, id: str) -> bool:
        """Eliminar un registro"""
        # Verificar que existe
        existing = await self.repository.get_by_id(id)
        if not existing:
            raise ValueError(f"Registro con ID {id} no encontrado")
        
        return await self.repository.delete(id)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar registros"""
        return await self.repository.count(filters=filters)


from typing import Any, Dict, List, Optional

# ============================================================================
# 4. INFRASTRUCTURE/API/ROUTES/generic_crud.py - Router Genérico
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.application.use_cases.generic_crud_use_case import GenericCRUDUseCase
from src.infrastructure.api.dependencies import get_generic_repository


class GenericCreateSchema(BaseModel):
    """Schema genérico para crear"""
    data: Dict[str, Any]

class GenericUpdateSchema(BaseModel):
    """Schema genérico para actualizar"""
    data: Dict[str, Any]

def create_generic_router(table_name: str, tag: str = None) -> APIRouter:
    """Factory para crear routers CRUD genéricos"""
    
    router = APIRouter(
        prefix=f"/{table_name}", 
        tags=[tag or table_name.capitalize()]
    )
    
    @router.post("/", status_code=201)
    async def create_record(
        schema: GenericCreateSchema,
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Crear un nuevo registro"""
        try:
            use_case = GenericCRUDUseCase(repository)
            return await use_case.create(schema.data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{record_id}")
    async def get_record(
        record_id: str,
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Obtener un registro por ID"""
        try:
            use_case = GenericCRUDUseCase(repository)
            return await use_case.get_by_id(record_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.get("/")
    async def list_records(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        filters: Optional[str] = Query(None, description="JSON string de filtros"),
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Listar registros con paginación y filtros"""
        import json
        filter_dict = json.loads(filters) if filters else None
        
        use_case = GenericCRUDUseCase(repository)
        return await use_case.get_all(skip=skip, limit=limit, filters=filter_dict)
    
    @router.put("/{record_id}")
    async def update_record(
        record_id: str,
        schema: GenericUpdateSchema,
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Actualizar un registro"""
        try:
            use_case = GenericCRUDUseCase(repository)
            return await use_case.update(record_id, schema.data)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.delete("/{record_id}", status_code=204)
    async def delete_record(
        record_id: str,
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Eliminar un registro"""
        try:
            use_case = GenericCRUDUseCase(repository)
            await use_case.delete(record_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.get("/count/total")
    async def count_records(
        filters: Optional[str] = Query(None, description="JSON string de filtros"),
        repository = Depends(lambda: get_generic_repository(table_name))
    ):
        """Contar registros"""
        import json
        filter_dict = json.loads(filters) if filters else None
        
        use_case = GenericCRUDUseCase(repository)
        count = await use_case.count(filters=filter_dict)
        return {"count": count}
    
    return router


# ============================================================================
# 5. INFRASTRUCTURE/API/dependencies.py - Inyección de Dependencias
# ============================================================================
from supabase import Client, create_client

from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.repositories.supabase_generic_repository import \
    SupabaseGenericRepository


def get_supabase_client() -> Client:
    """Obtener cliente de Supabase"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_generic_repository(table_name: str) -> SupabaseGenericRepository:
    """Obtener repositorio genérico para una tabla"""
    client = get_supabase_client()
    return SupabaseGenericRepository(client, table_name)


# ============================================================================
# 6. INFRASTRUCTURE/API/main.py - App FastAPI con routers genéricos
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.routes.generic_crud import create_generic_router
from src.infrastructure.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear routers genéricos para diferentes tablas
personas_router = create_generic_router("personas", "Personas")
productos_router = create_generic_router("productos", "Productos")
clientes_router = create_generic_router("clientes", "Clientes")

# Incluir routers
app.include_router(personas_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")
app.include_router(clientes_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================
"""
CREAR PERSONA:
POST /api/v1/personas
{
  "data": {
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "edad": 30,
    "telefono": "+595981234567"
  }
}

LISTAR CON FILTROS:
GET /api/v1/personas?skip=0&limit=10&filters={"edad": {"$gt": 25}}

OBTENER POR ID:
GET /api/v1/personas/{id}

ACTUALIZAR:
PUT /api/v1/personas/{id}
{
  "data": {
    "edad": 31,
    "telefono": "+595981234568"
  }
}

ELIMINAR:
DELETE /api/v1/personas/{id}

CONTAR:
GET /api/v1/personas/count/total?filters={"edad": {"$gt": 18}}
"""


# ============================================================================
# 7. ALTERNATIVA: Router único dinámico
# ============================================================================
from fastapi import Path

# Si prefieres un único endpoint que reciba la tabla como parámetro:
dynamic_router = APIRouter(prefix="/api/v1/crud", tags=["CRUD Dinámico"])

@dynamic_router.post("/{table_name}/")
async def dynamic_create(
    table_name: str = Path(..., description="Nombre de la tabla"),
    schema: GenericCreateSchema = None,
    repository = Depends(lambda table_name: get_generic_repository(table_name))
):
    """Crear registro en cualquier tabla"""
    use_case = GenericCRUDUseCase(repository)
    return await use_case.create(schema.data)

@dynamic_router.get("/{table_name}/{record_id}")
async def dynamic_get(
    table_name: str,
    record_id: str,
    repository = Depends(lambda table_name: get_generic_repository(table_name))
):
    """Obtener registro de cualquier tabla"""
    use_case = GenericCRUDUseCase(repository)
    return await use_case.get_by_id(record_id)

# app.include_router(dynamic_router)

"""
USO DEL ROUTER DINÁMICO:
POST /api/v1/crud/personas/
POST /api/v1/crud/productos/
GET /api/v1/crud/personas/{id}
GET /api/v1/crud/productos/{id}
"""