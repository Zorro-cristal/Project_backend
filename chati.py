# ============================================================================
# 1. CORE/ENTITIES/persona.py - Entidad de Dominio
# ============================================================================
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Persona:
    """Entidad de dominio Persona"""
    id: Optional[str]
    nombre: str
    apellido: str
    email: str
    edad: int
    telefono: Optional[str]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def nombre_completo(self) -> str:
        """Método de dominio"""
        return f"{self.nombre} {self.apellido}"
    
    def es_mayor_de_edad(self) -> bool:
        """Lógica de negocio"""
        return self.edad >= 18


# ============================================================================
# 2. CORE/INTERFACES/REPOSITORIES/persona_repository.py - Port (Interface)
# ============================================================================
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.entities.persona import Persona

class PersonaRepositoryInterface(ABC):
    """Port - Define el contrato para el repositorio"""
    
    @abstractmethod
    async def create(self, persona: Persona) -> Persona:
        pass
    
    @abstractmethod
    async def get_by_id(self, persona_id: str) -> Optional[Persona]:
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Persona]:
        pass
    
    @abstractmethod
    async def update(self, persona_id: str, persona: Persona) -> Optional[Persona]:
        pass
    
    @abstractmethod
    async def delete(self, persona_id: str) -> bool:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Persona]:
        pass


# ============================================================================
# 3. APPLICATION/DTOS/persona_dto.py - Data Transfer Objects
# ============================================================================
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class PersonaCreateDTO(BaseModel):
    """DTO para crear una persona"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    edad: int = Field(..., ge=0, le=150)
    telefono: Optional[str] = Field(None, max_length=20)

class PersonaUpdateDTO(BaseModel):
    """DTO para actualizar una persona"""
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    apellido: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    edad: Optional[int] = Field(None, ge=0, le=150)
    telefono: Optional[str] = Field(None, max_length=20)

class PersonaResponseDTO(BaseModel):
    """DTO de respuesta"""
    id: str
    nombre: str
    apellido: str
    email: str
    edad: int
    telefono: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============================================================================
# 4. APPLICATION/USE_CASES/persona/create_persona.py - Caso de Uso
# ============================================================================
from src.core.interfaces.repositories.persona_repository import PersonaRepositoryInterface
from src.core.entities.persona import Persona
from src.application.dtos.persona_dto import PersonaCreateDTO, PersonaResponseDTO

class CreatePersonaUseCase:
    """Caso de uso: Crear una persona"""
    
    def __init__(self, repository: PersonaRepositoryInterface):
        self.repository = repository
    
    async def execute(self, data: PersonaCreateDTO) -> PersonaResponseDTO:
        # Verificar que el email no exista
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ValueError(f"El email {data.email} ya está registrado")
        
        # Crear entidad de dominio
        persona = Persona(
            id=None,
            nombre=data.nombre,
            apellido=data.apellido,
            email=data.email,
            edad=data.edad,
            telefono=data.telefono
        )
        
        # Persistir
        created = await self.repository.create(persona)
        
        # Retornar DTO
        return PersonaResponseDTO.model_validate(created)


# ============================================================================
# 5. APPLICATION/USE_CASES/persona/get_persona.py
# ============================================================================
class GetPersonaUseCase:
    """Caso de uso: Obtener una persona por ID"""
    
    def __init__(self, repository: PersonaRepositoryInterface):
        self.repository = repository
    
    async def execute(self, persona_id: str) -> PersonaResponseDTO:
        persona = await self.repository.get_by_id(persona_id)
        if not persona:
            raise ValueError(f"Persona con ID {persona_id} no encontrada")
        
        return PersonaResponseDTO.model_validate(persona)


# ============================================================================
# 6. APPLICATION/USE_CASES/persona/list_personas.py
# ============================================================================
from typing import List

class ListPersonasUseCase:
    """Caso de uso: Listar personas con paginación"""
    
    def __init__(self, repository: PersonaRepositoryInterface):
        self.repository = repository
    
    async def execute(self, skip: int = 0, limit: int = 100) -> List[PersonaResponseDTO]:
        personas = await self.repository.get_all(skip=skip, limit=limit)
        return [PersonaResponseDTO.model_validate(p) for p in personas]


# ============================================================================
# 7. APPLICATION/USE_CASES/persona/update_persona.py
# ============================================================================
class UpdatePersonaUseCase:
    """Caso de uso: Actualizar una persona"""
    
    def __init__(self, repository: PersonaRepositoryInterface):
        self.repository = repository
    
    async def execute(self, persona_id: str, data: PersonaUpdateDTO) -> PersonaResponseDTO:
        # Verificar que existe
        existing = await self.repository.get_by_id(persona_id)
        if not existing:
            raise ValueError(f"Persona con ID {persona_id} no encontrada")
        
        # Actualizar solo los campos proporcionados
        updated_data = data.model_dump(exclude_unset=True)
        
        # Crear entidad actualizada
        persona = Persona(
            id=persona_id,
            nombre=updated_data.get('nombre', existing.nombre),
            apellido=updated_data.get('apellido', existing.apellido),
            email=updated_data.get('email', existing.email),
            edad=updated_data.get('edad', existing.edad),
            telefono=updated_data.get('telefono', existing.telefono)
        )
        
        updated = await self.repository.update(persona_id, persona)
        return PersonaResponseDTO.model_validate(updated)


# ============================================================================
# 8. APPLICATION/USE_CASES/persona/delete_persona.py
# ============================================================================
class DeletePersonaUseCase:
    """Caso de uso: Eliminar una persona"""
    
    def __init__(self, repository: PersonaRepositoryInterface):
        self.repository = repository
    
    async def execute(self, persona_id: str) -> bool:
        # Verificar que existe
        existing = await self.repository.get_by_id(persona_id)
        if not existing:
            raise ValueError(f"Persona con ID {persona_id} no encontrada")
        
        return await self.repository.delete(persona_id)


# ============================================================================
# 9. INFRASTRUCTURE/DATABASE/REPOSITORIES/supabase_persona_repository.py
# ============================================================================
from typing import List, Optional
from supabase import Client
from src.core.interfaces.repositories.persona_repository import PersonaRepositoryInterface
from src.core.entities.persona import Persona
from datetime import datetime

class SupabasePersonaRepository(PersonaRepositoryInterface):
    """Adaptador concreto para Supabase"""
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.table = "personas"
    
    async def create(self, persona: Persona) -> Persona:
        data = {
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "email": persona.email,
            "edad": persona.edad,
            "telefono": persona.telefono
        }
        
        result = self.client.table(self.table).insert(data).execute()
        return self._to_entity(result.data[0])
    
    async def get_by_id(self, persona_id: str) -> Optional[Persona]:
        result = self.client.table(self.table).select("*").eq("id", persona_id).execute()
        
        if not result.data:
            return None
        
        return self._to_entity(result.data[0])
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Persona]:
        result = self.client.table(self.table).select("*").range(skip, skip + limit - 1).execute()
        return [self._to_entity(row) for row in result.data]
    
    async def update(self, persona_id: str, persona: Persona) -> Optional[Persona]:
        data = {
            "nombre": persona.nombre,
            "apellido": persona.apellido,
            "email": persona.email,
            "edad": persona.edad,
            "telefono": persona.telefono
        }
        
        result = self.client.table(self.table).update(data).eq("id", persona_id).execute()
        
        if not result.data:
            return None
        
        return self._to_entity(result.data[0])
    
    async def delete(self, persona_id: str) -> bool:
        result = self.client.table(self.table).delete().eq("id", persona_id).execute()
        return len(result.data) > 0
    
    async def get_by_email(self, email: str) -> Optional[Persona]:
        result = self.client.table(self.table).select("*").eq("email", email).execute()
        
        if not result.data:
            return None
        
        return self._to_entity(result.data[0])
    
    def _to_entity(self, row: dict) -> Persona:
        """Convierte un registro de BD a entidad de dominio"""
        return Persona(
            id=str(row["id"]),
            nombre=row["nombre"],
            apellido=row["apellido"],
            email=row["email"],
            edad=row["edad"],
            telefono=row.get("telefono"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else None
        )


# ============================================================================
# 10. INFRASTRUCTURE/API/ROUTES/personas.py - Endpoints FastAPI
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from src.application.dtos.persona_dto import (
    PersonaCreateDTO, 
    PersonaUpdateDTO, 
    PersonaResponseDTO
)
from src.application.use_cases.persona.create_persona import CreatePersonaUseCase
from src.application.use_cases.persona.get_persona import GetPersonaUseCase
from src.application.use_cases.persona.list_personas import ListPersonasUseCase
from src.application.use_cases.persona.update_persona import UpdatePersonaUseCase
from src.application.use_cases.persona.delete_persona import DeletePersonaUseCase
from src.infrastructure.api.dependencies import get_persona_repository

router = APIRouter(prefix="/personas", tags=["Personas"])

@router.post("/", response_model=PersonaResponseDTO, status_code=201)
async def create_persona(
    data: PersonaCreateDTO,
    repository = Depends(get_persona_repository)
):
    """Crear una nueva persona"""
    try:
        use_case = CreatePersonaUseCase(repository)
        return await use_case.execute(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{persona_id}", response_model=PersonaResponseDTO)
async def get_persona(
    persona_id: str,
    repository = Depends(get_persona_repository)
):
    """Obtener una persona por ID"""
    try:
        use_case = GetPersonaUseCase(repository)
        return await use_case.execute(persona_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=List[PersonaResponseDTO])
async def list_personas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repository = Depends(get_persona_repository)
):
    """Listar todas las personas con paginación"""
    use_case = ListPersonasUseCase(repository)
    return await use_case.execute(skip=skip, limit=limit)

@router.put("/{persona_id}", response_model=PersonaResponseDTO)
async def update_persona(
    persona_id: str,
    data: PersonaUpdateDTO,
    repository = Depends(get_persona_repository)
):
    """Actualizar una persona"""
    try:
        use_case = UpdatePersonaUseCase(repository)
        return await use_case.execute(persona_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{persona_id}", status_code=204)
async def delete_persona(
    persona_id: str,
    repository = Depends(get_persona_repository)
):
    """Eliminar una persona"""
    try:
        use_case = DeletePersonaUseCase(repository)
        await use_case.execute(persona_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ============================================================================
# 11. INFRASTRUCTURE/API/dependencies.py - Inyección de Dependencias
# ============================================================================
from supabase import create_client, Client
from src.infrastructure.config.settings import get_settings
from src.infrastructure.database.repositories.supabase_persona_repository import SupabasePersonaRepository

def get_supabase_client() -> Client:
    """Obtener cliente de Supabase"""
    settings = get_settings()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_persona_repository() -> SupabasePersonaRepository:
    """Obtener repositorio de personas"""
    client = get_supabase_client()
    return SupabasePersonaRepository(client)


# ============================================================================
# 12. INFRASTRUCTURE/API/main.py - App FastAPI
# ============================================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.infrastructure.config.settings import get_settings
from src.infrastructure.api.routes import personas

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

# Rutas
app.include_router(personas.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
