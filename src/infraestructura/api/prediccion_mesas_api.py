from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from src.infraestructura.services.prediccion_mesas_service import (
    entrenar_modelo,
    predecir_tiempo_ocupacion,
)

router = APIRouter()


@router.get(
    "/entrenar",
    summary="Entrenar modelo de ocupación de mesas",
    description="Lee la tabla ventas y entrena un modelo de regresión lineal múltiple por local.",
)
async def entrenar_modelo_mesas(local: str | None = Query(None, description="Local para entrenar el modelo")) -> dict[str, Any]:
    try:
        return entrenar_modelo(local=local)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al entrenar el modelo: {exc}") from exc


@router.get(
    "/predecir",
    summary="Predecir tiempo de ocupación de mesas",
    description="Recibe la cantidad de personas y el local para estimar el tiempo de ocupación.",
)
async def predecir_mesas(
    cantidad_personas: int = Query(..., ge=0, description="Cantidad de personas en la mesa"),
    local: str | None = Query(None, description="Local para el que se estima el tiempo"),
    es_dia_festivo: bool = Query(False, description="Indica si el día es festivo"),
) -> dict[str, Any]:
    try:
        return predecir_tiempo_ocupacion(cantidad_personas, local=local, es_dia_festivo=es_dia_festivo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al predecir: {exc}") from exc
