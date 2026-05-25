from typing import Optional

from fastapi import APIRouter, Query

from src.infraestructura.logica.persona import obtener_personas

router = APIRouter()

@router.get("/{cedula}", summary="Obtener persona por cédula", description="Obtiene los datos de una persona por su cédula.")
async def obtenerPersonaPorCedulaApi(cedula: int):
    result = await obtener_personas({"cedula": cedula})
    return {"message": result}


@router.get("/", summary="Obtener personas", description="Obtiene una lista de personas con filtros opcionales.")
async def obtenerPersonasApi(
    cedula: Optional[int] = Query(None, description="Filtrar personas por cédula"),
    nombres: Optional[str] = Query(None, description="Filtrar personas por nombre parcial"),
    apellidos: Optional[str] = Query(None, description="Filtrar personas por apellido parcial"),
    estado: Optional[int] = Query(None, description="Filtrar personas por estado"),
    telefono: Optional[int] = Query(None, description="Filtrar personas por teléfono"),
    direccion: Optional[str] = Query(None, description="Filtrar personas por dirección parcial"),
    nacionalidad: Optional[str] = Query(None, description="Filtrar personas por nacionalidad"),
):
    filtros = {}
    if cedula is not None:
        filtros["cedula"] = cedula
    if nombres is not None:
        filtros["nombres"] = nombres
    if apellidos is not None:
        filtros["apellidos"] = apellidos
    if estado is not None:
        filtros["estado"] = estado
    if telefono is not None:
        filtros["telefono"] = telefono
    if direccion is not None:
        filtros["direccion"] = direccion
    if nacionalidad is not None:
        filtros["nacionalidad"] = nacionalidad

    result = await obtener_personas(filtros)
    return {"message": result}
