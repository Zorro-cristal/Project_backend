from fastapi import APIRouter

from src.infraestructura.logica.categoria import actualizar_categoria, crear_categoria, obtener_categorias
from src.shell.adaptadores.requests.CategoriaRequest import CategoriaRequest, CategoriaUpdateRequest

router = APIRouter()

@router.put("/{id}")
async def actualizarCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_categoria(id, payload)
    return {"message": result}

@router.patch("/{id}")
async def patchCategoriaApi(id: int, requestBody: CategoriaUpdateRequest):
    return actualizarCategoriaApi(id, requestBody)

@router.post("/")
async def agregarCategoriaApi(requestBody: CategoriaRequest):
    payload = requestBody.model_dump()
    result = await crear_categoria(payload)
    return {"message": result}

@router.get("/")
async def obtenerCategoriasApi():
    result = await obtener_categorias()
    return {"message": result}
