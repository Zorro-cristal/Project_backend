from typing import Optional

from fastapi import APIRouter, Depends, Query

from src.infraestructura.api.dependencies import permiso_requerido

from ..services.persona_service import obtener_personas

router = APIRouter()

@router.get("/{cedula}", dependencies=[Depends(permiso_requerido('persona', 'leer'))], summary="Obtener persona por cédula", description="Obtiene los datos de una persona por su cédula.")
async def obtenerPersonaPorCedulaApi(cedula: int):
    result = await obtener_personas({"cedula": cedula})
    return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('persona', 'leer'))], summary="Obtener personas", description="Obtiene una lista de personas con filtros opcionales.")
async def obtenerPersonasApi(
    nombre_completo: Optional[str] = Query(None, description="Buscar por nombre completo (nombre o apellido, contiene)"),
    cedula: Optional[int] = Query(None, description="Filtrar personas por cédula"),
    nombres: Optional[str] = Query(None, description="Filtrar personas por nombre parcial"),
    apellidos: Optional[str] = Query(None, description="Filtrar personas por apellido parcial"),
    telefono: Optional[int] = Query(None, description="Filtrar personas por teléfono"),
    direccion: Optional[str] = Query(None, description="Filtrar personas por dirección parcial"),
    nacionalidad: Optional[str] = Query(None, description="Filtrar personas por nacionalidad"),
):
    filtros = {}
    if nombre_completo is not None:
        filtros["nombre_completo"] = nombre_completo
    if cedula is not None:
        filtros["cedula"] = cedula
    if nombres is not None:
        filtros["nombres"] = nombres
    if apellidos is not None:
        filtros["apellidos"] = apellidos
    if telefono is not None:
        filtros["telefono"] = telefono
    if direccion is not None:
        filtros["direccion"] = direccion
    if nacionalidad is not None:
        filtros["nacionalidad"] = nacionalidad

    result = await obtener_personas(filtros)
    return {"message": result}
