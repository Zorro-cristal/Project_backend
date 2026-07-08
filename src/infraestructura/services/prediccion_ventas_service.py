from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import requests

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from src.infraestructura.config.supabase import get_supabase_client
from src.shell.adapters.externals.openmeteo import obtenerInformacionClimatica

MODEL_DIR = Path(__file__).resolve().parents[3] / "src" / "ml" / "ventas_prediccion"
MODEL_PATH = MODEL_DIR / "ventas_model.joblib"
WEATHER_API_KEY = "4b2f4f5d78c0d6e5d2b9f41fed90393f"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"
LATITUD_EMPRESA = -25.801843
LONGITUD_EMPRESA = -56.437743


def _normalize_clima_value(value: Any) -> str:
    """Normaliza el nombre de la condición climática para usarlo como feature."""
    if value is None or pd.isna(value):
        return "desconocido"

    normalized = str(value).strip().lower()
    normalized = "_".join(normalized.split())
    return normalized or "desconocido"


def _is_cercania_pago(fecha: pd.Timestamp) -> bool:
    """Marca fechas cercanas al pago, entre el 25 del mes y el 5 del siguiente."""
    day = fecha.day
    return day >= 25 or day <= 5


def _is_fin_de_mes(fecha: pd.Timestamp) -> bool:
    """Indica si la fecha es el último día del mes o el día anterior."""
    next_day = fecha + timedelta(days=1)
    return next_day.month != fecha.month


def build_feature_frame(
    historial: pd.DataFrame,
    target_column: str | None = "ventas_totales",
) -> pd.DataFrame:
    """Construye el conjunto de features con ingeniería de características."""
    if historial.empty:
        raise ValueError("No hay datos de historial para construir features.")

    data = historial.copy()
    if "fecha" not in data.columns:
        raise ValueError("El DataFrame debe incluir la columna 'fecha'.")

    data["fecha"] = pd.to_datetime(data["fecha"], utc=True)
    data["fecha"] = data["fecha"].dt.tz_convert(None)
    data = data.sort_values("fecha").reset_index(drop=True)

    if "evento_festivo" not in data.columns:
        if "evento_festivo" in data.columns:
            data["evento_festivo"] = data["evento_festivo"].fillna(False).astype(bool)
        elif "eventofestivo" in data.columns:
            data["evento_festivo"] = data["eventofestivo"].fillna(False).astype(bool)
        else:
            data["evento_festivo"] = False

    if "condicion_clima" not in data.columns:
        if "clima" in data.columns:
            data["condicion_clima"] = data["clima"]
        else:
            data["condicion_clima"] = "desconocido"

    data["evento_festivo"] = data["evento_festivo"].fillna(False).astype(bool)
    data["condicion_clima"] = data["condicion_clima"].fillna("desconocido")
    data["condicion_clima"] = data["condicion_clima"].apply(_normalize_clima_value)

    features = pd.DataFrame({
        "dia_semana": data["fecha"].dt.dayofweek,
        "mes": data["fecha"].dt.month,
        "fin_de_semana": data["fecha"].dt.dayofweek.isin([5, 6]).astype(bool),
        "fin_de_mes": data["fecha"].apply(_is_fin_de_mes).astype(bool),
        "evento_festivo": data["evento_festivo"].astype(bool),
        "cercania_pago": data["fecha"].apply(_is_cercania_pago).astype(bool),
    })

    clima_dummies = pd.get_dummies(
        data["condicion_clima"],
        prefix="clima",
        dtype=int,
    )
    features = pd.concat([features, clima_dummies], axis=1)

    for column in ["temperatura", "humedad", "velocidad_viento", "lluvia", "precipitaciones", "probabilidad_precipitaciones"]:
        if column in data.columns:
            features[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    if target_column and target_column in data.columns:
        features[target_column] = data[target_column].astype(float)

    return features


def train_sales_forecast_model(historial: pd.DataFrame) -> RandomForestRegressor:
    """Entrena un modelo de regresión con las features ingenierizadas."""
    feature_frame = build_feature_frame(historial, target_column="ventas_totales")

    X = feature_frame.drop(columns=["ventas_totales"])
    y = feature_frame["ventas_totales"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model


def save_sales_forecast_model(
    model: RandomForestRegressor,
    feature_columns: Iterable[str],
    path: Path | str | None = None,
) -> Path:
    """Guarda el modelo y las columnas esperadas por el endpoint de predicción."""
    model_path = Path(path or MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "model": model,
        "feature_columns": list(feature_columns),
        "created_at": datetime.utcnow().isoformat(),
    }
    joblib.dump(payload, model_path)
    return model_path


def load_sales_forecast_model(path: Path | str | None = None) -> dict[str, Any]:
    """Carga el modelo entrenado desde el archivo local."""
    model_path = Path(path or MODEL_PATH)
    if not model_path.exists():
        raise FileNotFoundError(
            f"No existe un modelo entrenado en {model_path}. Primero ejecuta el entrenamiento."
        )

    payload = joblib.load(model_path)
    if not isinstance(payload, dict) or "model" not in payload:
        raise ValueError("El archivo del modelo no tiene el formato esperado.")

    return payload


def _fetch_sales_history(limite: int | None = None) -> pd.DataFrame:
    """Obtiene el historial de ventas desde Supabase usando ventas y detalle_venta."""
    supabase = get_supabase_client()

    ventas_response = supabase.table("ventas").select("id,fecha,evento_festivo,clima,temperatura,humedad").execute()
    ventas_data = ventas_response.data or []

    detalles_response = supabase.table("detalle_venta").select("id_ventafk,cantidad,precio,descuento").execute()
    detalles_data = detalles_response.data or []

    if not ventas_data:
        return pd.DataFrame(columns=["fecha", "evento_festivo", "condicion_clima", "ventas_totales"])

    ventas_df = pd.DataFrame(ventas_data)
    detalles_df = pd.DataFrame(detalles_data)

    if detalles_df.empty:
        detalles_df = pd.DataFrame(columns=["id_ventafk", "cantidad", "precio", "descuento"])

    if not detalles_df.empty and "id_ventafk" in detalles_df.columns:
        detalles_df["id_ventafk"] = pd.to_numeric(detalles_df["id_ventafk"], errors="coerce")
        detalles_df["cantidad"] = pd.to_numeric(detalles_df["cantidad"], errors="coerce").fillna(0)
        detalles_df["precio"] = pd.to_numeric(detalles_df["precio"], errors="coerce").fillna(0)
        detalles_df["descuento"] = pd.to_numeric(detalles_df["descuento"], errors="coerce").fillna(0)

        detalles_agrupados = (
            detalles_df.assign(importe=(detalles_df["cantidad"] * detalles_df["precio"] - detalles_df["descuento"]))
            .groupby("id_ventafk", as_index=False)["importe"].sum()
        )
        ventas_df = ventas_df.merge(detalles_agrupados, left_on="id", right_on="id_ventafk", how="left")
        ventas_df["importe"] = ventas_df["importe"].fillna(0)
    else:
        ventas_df["importe"] = 0

    ventas_df["fecha"] = pd.to_datetime(ventas_df["fecha"], utc=True)
    ventas_df["fecha"] = ventas_df["fecha"].dt.tz_convert(None)

    historial = (
        ventas_df.groupby(ventas_df["fecha"].dt.normalize(), as_index=False)["importe"].sum()
        .rename(columns={"fecha": "fecha", "importe": "ventas_totales"})
    )

    historial["fecha"] = pd.to_datetime(historial["fecha"])

    if "evento_festivo" not in ventas_df.columns:
        if "evento_festivo" in ventas_df.columns:
            ventas_df["evento_festivo"] = ventas_df["evento_festivo"].fillna(False).astype(bool)
        else:
            ventas_df["evento_festivo"] = False
    if "condicion_clima" not in ventas_df.columns:
        ventas_df["condicion_clima"] = ventas_df.get("clima", "desconocido")

    ventas_df["evento_festivo"] = ventas_df["evento_festivo"].fillna(False).astype(bool)
    ventas_df["condicion_clima"] = ventas_df["condicion_clima"].fillna("desconocido")

    ventas_con_feature = ventas_df[["id", "fecha", "evento_festivo", "condicion_clima"]].copy()
    ventas_con_feature["fecha"] = pd.to_datetime(ventas_con_feature["fecha"], utc=True)
    ventas_con_feature["fecha"] = ventas_con_feature["fecha"].dt.tz_convert(None)
    ventas_con_feature["fecha"] = ventas_con_feature["fecha"].dt.normalize()

    historial = historial.merge(
        ventas_con_feature.groupby("fecha", as_index=False).first(),
        on="fecha",
        how="left",
    )

    historial["evento_festivo"] = historial["evento_festivo"].fillna(False).astype(bool)
    historial["condicion_clima"] = historial["condicion_clima"].fillna("desconocido")

    if limite is not None and limite > 0:
        historial = historial.tail(limite)

    return historial


def train_and_save_sales_forecast_model(limite: int | None = None, path: Path | str | None = None) -> dict[str, Any]:
    """Obtiene datos, entrena y guarda el modelo localmente."""
    historial = _fetch_sales_history(limite=limite)
    if historial.empty or len(historial) < 2:
        raise ValueError("Se necesitan al menos 2 días de historial para entrenar el modelo.")

    model = train_sales_forecast_model(historial)
    feature_frame = build_feature_frame(historial, target_column="ventas_totales")
    model_path = save_sales_forecast_model(model, feature_frame.drop(columns=["ventas_totales"]).columns, path=path)

    predictions = model.predict(feature_frame.drop(columns=["ventas_totales"]))
    mae = mean_absolute_error(feature_frame["ventas_totales"], predictions)

    return {
        "message": "Modelo entrenado correctamente",
        "model_path": str(model_path),
        "rows_used": int(len(historial)),
        "mae": round(float(mae), 4),
    }


def _normalize_weather_condition(description: str | None) -> str:
    """Normaliza la condición meteorológica a un valor legible y estable."""
    if not description:
        return "variable"

    lowered = str(description).strip().lower()
    if any(token in lowered for token in ["rain", "drizzle", "shower"]):
        return "lluvioso"
    if any(token in lowered for token in ["cloud", "overcast"]):
        return "nublado"
    if any(token in lowered for token in ["clear", "sunny", "few clouds"]):
        return "soleado"
    if any(token in lowered for token in ["snow", "ice"]):
        return "nevado"
    if any(token in lowered for token in ["thunderstorm", "storm"]):
        return "tormentoso"
    return lowered


def _get_weather_forecast_for_range(
    fecha_inicio: str | datetime,
    fecha_fin: str | datetime,
) -> dict[str, dict[str, Any]]:
    """Consulta la API de OpenWeatherMap para obtener pronóstico real por día."""
    try:
        response = requests.get(
            WEATHER_API_URL,
            params={
                "lat": LATITUD_EMPRESA,
                "lon": LONGITUD_EMPRESA,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "cnt": 40,
            },
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        payload = {}

    forecast_by_date: dict[str, dict[str, Any]] = {}
    for item in payload.get("list", []):
        try:
            date_text = item["dt_txt"].split(" ")[0]
            main = item.get("main", {})
            weather = item.get("weather", [{}])[0]
            rain_3h = float(item.get("rain", {}).get("3h", item.get("rain", 0) or 0))
            snow_3h = float(item.get("snow", {}).get("3h", item.get("snow", 0) or 0))
            forecast_by_date[date_text] = {
                "temperatura_max": round(float(main.get("temp_max", main.get("temp", 0))), 1),
                "humedad": int(main.get("humidity", 0)),
                "condicion_clima": _normalize_weather_condition(weather.get("description")),
                "velocidad_viento": round(float(item.get("wind", {}).get("speed", 0)), 2),
                "lluvia": round(rain_3h, 2),
                "precipitaciones": round(rain_3h + snow_3h, 2),
                "probabilidad_precipitaciones": int(round(float(item.get("pop", 0)) * 100)),
            }
        except Exception:
            continue

    if forecast_by_date:
        return forecast_by_date

    fallback = obtenerInformacionClimatica(LATITUD_EMPRESA, LONGITUD_EMPRESA, ["weather_code", "temperature_2m", "relative_humidity_2m"])
    if not fallback:
        return {}

    return {
        pd.Timestamp.utcnow().strftime("%Y-%m-%d"): {
            "temperatura_max": float(fallback.get("temperatura", 0)),
            "humedad": int(fallback.get("humedad", 0)),
            "condicion_clima": _normalize_weather_condition(str(fallback.get("clima", "variable"))),
            "velocidad_viento": float(fallback.get("velocidad_viento", 0)),
            "lluvia": float(fallback.get("lluvia", 0)),
            "precipitaciones": float(fallback.get("precipitaciones", 0)),
            "probabilidad_precipitaciones": int(fallback.get("probabilidad_precipitaciones", 0)),
        }
    }


def _build_forecast_rows(
    fecha_inicio: str | datetime,
    fecha_fin: str | datetime,
    dias_festivos: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Genera una lista de días de predicción entre dos fechas y copia el clima real del rango."""
    inicio = pd.to_datetime(fecha_inicio).normalize()
    fin = pd.to_datetime(fecha_fin).normalize()

    if inicio > fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

    festivos = {pd.to_datetime(item).normalize().date().isoformat() for item in (dias_festivos or [])}
    weather_forecast = _get_weather_forecast_for_range(fecha_inicio, fecha_fin)
    rows: list[dict[str, Any]] = []
    current = inicio

    while current <= fin:
        fecha_str = current.strftime("%Y-%m-%d")
        meteorologia = weather_forecast.get(fecha_str, {
            "temperatura_max": 0.0,
            "humedad": 0,
            "condicion_clima": "desconocido",
            "velocidad_viento": 0.0,
            "lluvia": 0.0,
            "precipitaciones": 0.0,
            "probabilidad_precipitaciones": 0,
        })
        rows.append({
            "fecha": fecha_str,
            "evento_festivo": fecha_str in festivos,
            "datos_meteorologicos": {
                "temperatura_max": meteorologia["temperatura_max"],
                "humedad": meteorologia["humedad"],
                "condicion_clima": meteorologia["condicion_clima"],
                "velocidad_viento": meteorologia.get("velocidad_viento", 0.0),
                "lluvia": meteorologia.get("lluvia", 0.0),
                "precipitaciones": meteorologia.get("precipitaciones", 0.0),
                "probabilidad_precipitaciones": meteorologia.get("probabilidad_precipitaciones", 0),
            },
        })
        current = current + timedelta(days=1)

    return rows


def _estimate_product_breakdown(ventas_previstas: float) -> list[dict[str, Any]]:
    """Desglosa la previsión de productos con una regla simple basada en porcentajes."""
    if ventas_previstas <= 0:
        return [
            {"categoria": "Platos Principales", "cantidad_estimada": 0},
            {"categoria": "Bebidas", "cantidad_estimada": 0},
            {"categoria": "Postres", "cantidad_estimada": 0},
        ]

    return [
        {"categoria": "Platos Principales", "cantidad_estimada": int(round(ventas_previstas / 6000))},
        {"categoria": "Bebidas", "cantidad_estimada": int(round(ventas_previstas / 3500))},
        {"categoria": "Postres", "cantidad_estimada": int(round(ventas_previstas / 12000))},
    ]


def build_daily_prediction_payloads(
    fecha_inicio: str | datetime,
    fecha_fin: str | datetime,
    dias_festivos: Iterable[str] | None = None,
    weather_forecast_by_date: dict[str, dict[str, Any]] | None = None,
    ventas_previstas_por_fecha: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Construye la estructura final con una entrada por día del rango."""
    forecast_rows = []
    inicio = pd.to_datetime(fecha_inicio).normalize()
    fin = pd.to_datetime(fecha_fin).normalize()

    if inicio > fin:
        raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")

    festivos = {pd.to_datetime(item).normalize().date().isoformat() for item in (dias_festivos or [])}
    weather_forecast = weather_forecast_by_date or _get_weather_forecast_for_range(fecha_inicio, fecha_fin)
    prediction_rows: list[dict[str, Any]] = []
    current = inicio

    while current <= fin:
        fecha_str = current.strftime("%Y-%m-%d")
        weather_payload = weather_forecast.get(fecha_str, {
            "temperatura_max": 0.0,
            "humedad": 0,
            "condicion_clima": "variable",
        })
        prediction_rows.append({
            "fecha": fecha_str,
            "evento_festivo": fecha_str in festivos,
            "condicion_clima": weather_payload.get("condicion_clima", "variable"),
            "temperatura": weather_payload.get("temperatura_max", 0.0),
            "humedad": weather_payload.get("humedad", 0),
            "velocidad_viento": weather_payload.get("velocidad_viento", 0.0),
            "lluvia": weather_payload.get("lluvia", 0.0),
            "precipitaciones": weather_payload.get("precipitaciones", 0.0),
            "probabilidad_precipitaciones": weather_payload.get("probabilidad_precipitaciones", 0),
        })
        current = current + timedelta(days=1)

    if ventas_previstas_por_fecha is None:
        ventas_predichas = predict_sales_forecast(prediction_rows)
        ventas_previstas_por_fecha = {
            item["fecha"]: float(item.get("ventas_proyectadas", 0.0)) for item in ventas_predichas
        }

    current = inicio
    while current <= fin:
        fecha_str = current.strftime("%Y-%m-%d")
        weather_payload = weather_forecast.get(fecha_str, {
            "temperatura_max": 0.0,
            "humedad": 0,
            "condicion_clima": "variable",
        })
        ventas_previstas = float(ventas_previstas_por_fecha.get(fecha_str, 0.0))

        forecast_rows.append({
            "fecha": fecha_str,
            "evento_festivo": fecha_str in festivos,
            "datos_meteorologicos": {
                "temperatura_max": weather_payload.get("temperatura_max", 0.0),
                "humedad": weather_payload.get("humedad", 0),
                "condicion_clima": weather_payload.get("condicion_clima", "variable"),
                "velocidad_viento": weather_payload.get("velocidad_viento", 0.0),
                "lluvia": weather_payload.get("lluvia", 0.0),
                "precipitaciones": weather_payload.get("precipitaciones", 0.0),
                "probabilidad_precipitaciones": weather_payload.get("probabilidad_precipitaciones", 0),
            },
            "ventas_previstas": round(ventas_previstas, 2),
            "monto_a_recaudar_estimado": round(ventas_previstas, 2),
            "prevision_productos": _estimate_product_breakdown(ventas_previstas),
        })
        current = current + timedelta(days=1)

    return {
        "success": True,
        "message": forecast_rows,
        "meta": {
            "modelo": "RandomForestRegressor",
            "rango": {
                "fecha_inicio": inicio.strftime("%Y-%m-%d"),
                "fecha_fin": fin.strftime("%Y-%m-%d"),
            },
        },
    }


def predict_sales_forecast(
    forecast_rows: Iterable[dict[str, Any]],
    path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Predice ventas para una lista de fechas futuras a partir del modelo guardado."""
    model_payload = load_sales_forecast_model(path=path)
    model = model_payload["model"]
    expected_columns = model_payload.get("feature_columns", [])

    forecast_frame = pd.DataFrame(list(forecast_rows))
    if forecast_frame.empty:
        raise ValueError("Debe proporcionar al menos un día de pronóstico.")

    forecast_frame["fecha"] = pd.to_datetime(forecast_frame["fecha"], utc=True)
    forecast_frame["fecha"] = forecast_frame["fecha"].dt.tz_convert(None)
    forecast_frame["fecha"] = forecast_frame["fecha"].dt.normalize()

    forecast_frame["evento_festivo"] = forecast_frame["evento_festivo"].fillna(False).astype(bool)
    if "condicion_clima" not in forecast_frame.columns:
        forecast_frame["condicion_clima"] = forecast_frame.get("clima", "desconocido")
    forecast_frame["condicion_clima"] = forecast_frame["condicion_clima"].fillna("desconocido")

    features = build_feature_frame(
        forecast_frame.rename(columns={"fecha": "fecha", "evento_festivo": "evento_festivo", "condicion_clima": "condicion_clima"}),
        target_column=None,
    )
    features = features.reindex(columns=expected_columns, fill_value=0)

    predictions = model.predict(features)

    results: list[dict[str, Any]] = []
    for index, value in enumerate(predictions):
        entry = forecast_frame.iloc[index].to_dict()
        entry["fecha"] = entry["fecha"].strftime("%Y-%m-%d")
        entry["ventas_proyectadas"] = round(float(value), 2)
        results.append(entry)

    return results
