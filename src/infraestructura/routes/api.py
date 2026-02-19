from fastapi import APIRouter

from src.shell.flujo.prueba.conexion_supabase import conexion_supabase

router = APIRouter()

@router.get("/health")
async def root():
    result = await conexion_supabase(True)
    return {"message": result} 