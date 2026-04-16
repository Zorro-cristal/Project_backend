from fastapi import APIRouter

from src.infraestructura.logica.marca import ( actualizar_marca, crear_marca, obtener_marcas)
from src.shell.adaptadores.requests.MarcaRequest import MarcaRequest, MarcaUpdateRequest

router = APIRouter()

@router.put("/{id}")
async def actualizarMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_marca(id, payload)
    return {"message": result}

@router.patch("/{id}")
async def patchMarcaApi(id: int, requestBody: MarcaUpdateRequest):
    return await actualizarMarcaApi(id, requestBody)

@router.post("/")
async def agregarMarcaApi(requestBody: MarcaRequest):
    payload = requestBody.model_dump()
    result = await crear_marca(payload)
    return {"message": result}

@router.get("/")
async def obtenerMarcasApi():
    result = await obtener_marcas()
    return {"message": result}
