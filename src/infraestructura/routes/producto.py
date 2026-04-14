from fastapi import APIRouter

from src.infraestructura.database.producto import obtenerProducto

router = APIRouter()

@router.get("/")
async def obtenerProductos():
    result = await obtenerProducto(
        columnas='*, marcas(marca_id:id, marca_nombre:nombre, marca_estado:estado)'
    )
    return {"message": result}