from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from typing import Any


from src.infraestructura.api.dependencies import permiso_requerido
from src.shell.adapters.requests.mesa_request import (MesaRequest,
                                                      MesaUpdateRequest)

from ..services.mesa_service import actualizar_mesa, crear_mesa, obtener_mesas
from ..services.prediccion_mesas_service import (
    entrenar_modelo,
    predecir_tiempo_ocupacion,
)

router = APIRouter()


@router.put("/{id}", dependencies=[Depends(permiso_requerido('mesa', 'editar'))], summary="Actualizar mesa", description="Actualiza una mesa existente por su ID.")
async def actualizarMesaApi(id: int, requestBody: MesaUpdateRequest):
	payload = requestBody.model_dump(exclude_unset=True)
	try:
		result = await actualizar_mesa(id, payload)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
	return {"message": result}


@router.patch("/{id}", dependencies=[Depends(permiso_requerido('mesa', 'editar'))], summary="Actualizar mesa parcialmente", description="Actualiza parcialmente una mesa existente por su ID.")
async def patchMesaApi(id: int, requestBody: MesaUpdateRequest):
	return await actualizarMesaApi(id, requestBody)


@router.post("/", dependencies=[Depends(permiso_requerido('mesa', 'crear'))], summary="Crear mesa", description="Crea una nueva mesa.")
async def agregarMesaApi(requestBody: MesaRequest):
	payload = requestBody.model_dump()
	try:
		result = await crear_mesa(payload)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc))
	return {"message": result}


@router.get("/", dependencies=[Depends(permiso_requerido('mesa', 'leer'))], summary="Obtener mesas", description="Obtiene una lista de mesas con filtros opcionales.")
async def obtenerMesasApi(
	id: Optional[str] = Query(None, description="Filtrar mesas por ID"),
	nombre: Optional[str] = Query(None, description="Filtrar mesas por nombre parcial"),
	estado: Optional[int] = Query(None, description="Filtrar mesas por estado (1 activo, 0 inactivo)"),
	id_localfk: Optional[int] = Query(None, description="Filtrar mesas por ID de local asociada"),
	mostrar_inactivo: Optional[int] = Query(None, description="Si es 1, muestra registros inactivos (estado=0). Por defecto solo muestra activos"),
):
	filtros = {}
	if id is not None:
		filtros["id"] = id
	if nombre is not None:
		filtros["nombre"] = nombre
	if estado is not None:
		filtros["estado"] = estado
	if id_localfk is not None:
		filtros["id_localfk"] = id_localfk
	# Por defecto: traer todos los registros con estado != 0
	# Si mostrar_inactivo=1: mostrar todos incluyendo inactivos (estado=0)
	if mostrar_inactivo != 1 and "estado" not in filtros:
		filtros["mostrar_inactivo"] = 0  # estado != 0

	result = await obtener_mesas(filtros)
	return {"message": result}


@router.get("/{id}", dependencies=[Depends(permiso_requerido('mesa', 'leer'))], summary="Obtener mesa por ID", description="Obtiene una mesa específica por su ID.")
async def obtenerMesaPorIdApi(id: int):
	filtros = {"id": id}
	result = await obtener_mesas(filtros)
	if not result:
		return {"message": f"Mesa con ID {id} no encontrada"}
	return {"message": result[0] if isinstance(result, list) else result}


@router.get(
	"/modelo/entrenar",
	summary="Entrenar modelo de ocupación de mesas",
	description="Lee la tabla ventas y entrena un modelo de regresión lineal múltiple por local.",
)
async def entrenar_modelo_mesas(
	local: str | None = Query(None, description="Local para entrenar el modelo"),
) -> dict[str, Any]:
	try:
		return entrenar_modelo(local=local)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except RuntimeError as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc
	except Exception as exc:  # pragma: no cover
		raise HTTPException(status_code=500, detail=f"Error inesperado al entrenar el modelo: {exc}") from exc


@router.get(
	"/modelo/predecir",
	summary="Predecir tiempo de ocupación de mesas",
	description="Recibe la cantidad de personas y el local para estimar el tiempo de ocupación.",
)
async def predecir_mesas(
	cantidad_personas: int = Query(..., ge=0, description="Cantidad de personas en la mesa"),
	local: str | None = Query(None, description="Local para el que se estima el tiempo"),
	es_dia_festivo: bool = Query(False, description="Indica si el día es festivo"),
) -> dict[str, Any]:
	try:
		return predecir_tiempo_ocupacion(
			cantidad_personas,
			local=local,
			es_dia_festivo=es_dia_festivo,
		)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:  # pragma: no cover
		raise HTTPException(status_code=500, detail=f"Error inesperado al predecir: {exc}") from exc

