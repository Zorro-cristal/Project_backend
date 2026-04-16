from fastapi import APIRouter
from src.infraestructura.logica.precio import actualizar_precio, crear_precio, obtener_precios
from src.shell.adaptadores.requests.PrecioRequest import PrecioRequest, PrecioUpdateRequest

router = APIRouter()

@router.put("/{id}")
async def actualizarPrecioApi(id: int, requestBody: PrecioUpdateRequest):
    payload = requestBody.model_dump(exclude_unset=True)
    result = await actualizar_precio(id, payload)
    return {"message": result}

@router.patch("/{id}")
async def patchPrecioApi(id: int, requestBody: PrecioUpdateRequest):
    return await actualizarPrecioApi(id, requestBody)

@router.post("/")
async def agregarPrecioApi(requestBody: PrecioRequest):
    payload = requestBody.model_dump()
    result = await crear_precio(payload)
    return {"message": result}

@router.get("/")
async def obtenerPreciosApi():
    result = await obtener_precios()
    return {"message": result}
