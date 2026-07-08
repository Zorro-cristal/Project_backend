from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.infraestructura.services.prediccion_ventas_service import (
    build_daily_prediction_payloads,
    train_and_save_sales_forecast_model,
)

router = APIRouter()


class TrainingRequest(BaseModel):
    limite: int | None = Field(None, description="Cantidad máxima de días de historial a usar")


@router.get(
    "/entrenar",
    summary="Entrenar modelo de predicción de ventas",
    description="Lee el historial de ventas desde Supabase, entrena un modelo local y lo guarda en disco.",
)
async def entrenar_modelo_ventas(request: TrainingRequest) -> dict[str, Any]:
    try:
        result = train_and_save_sales_forecast_model(limite=request.limite)
        return {"success": True, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al entrenar el modelo: {exc}") from exc


@router.get(
    "/predecir",
    summary="Predecir ventas proyectadas",
    description="Recibe un rango de fechas por query params, consulta clima real por día y devuelve la previsión diaria con ventas, recaudo y productos estimados.",
)
async def predecir_ventas(
    fecha_inicio: str = Query(..., description="Fecha inicial en formato YYYY-MM-DD"),
    fecha_fin: str = Query(..., description="Fecha final en formato YYYY-MM-DD"),
    dias_festivos: list[str] | None = Query(None, description="Fechas festivas opcionales en formato YYYY-MM-DD"),
) -> dict[str, Any]:
    try:
        return build_daily_prediction_payloads(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias_festivos=dias_festivos or [],
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise HTTPException(status_code=500, detail=f"Error inesperado al predecir: {exc}") from exc
