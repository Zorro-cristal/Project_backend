from __future__ import annotations

import calendar
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.configs.settings import get_settings

try:
    from src.infraestructura.config.supabase import get_supabase_client
except Exception:  # pragma: no cover - fallback para entornos sin cliente inicializado
    get_supabase_client = None

MODEL_PATH = (
    Path(__file__).resolve().parents[2]
    / "ml"
    / "mesas_prediccion"
    / "mesas_model.joblib"
)
MODEL_CACHE: dict[str, Any] | None = None


def _normalizar_local(local: str | int | None) -> str:
    """Normaliza el identificador del local para usarlo como clave."""
    if local is None:
        return "general"
    local_texto = str(local).strip().lower()
    return local_texto or "general"


def _coincide_local(registro: dict[str, Any], local_key: str) -> bool:
    """Comprueba si un registro corresponde al local solicitado."""
    for campo in ("local", "nombre_local", "nombre", "id_localfk", "local_id"):
        valor = registro.get(campo)
        if valor is None:
            continue
        if str(valor).strip().lower() == local_key:
            return True
    return False


def _parsear_ocupacion_a_minutos(valor: Any) -> int:
    """Convierte un valor de ocupacion tipo hh:mm:ss a minutos."""
    if valor is None or pd.isna(valor):
        return 0

    if isinstance(valor, (int, float)):
        return int(valor)

    if hasattr(valor, "hour") and hasattr(valor, "minute") and hasattr(valor, "second"):
        return int(valor.hour * 60 + valor.minute + valor.second / 60)

    texto = str(valor).strip()
    if not texto:
        return 0

    partes = texto.split(":")
    if len(partes) < 2:
        return 0

    horas = int(partes[0])
    minutos = int(partes[1])
    segundos = int(partes[2]) if len(partes) > 2 else 0
    return horas * 60 + minutos + int(segundos / 60)


def _extraer_fecha(valor: Any) -> date | None:
    """Convierte fechas de Supabase a objetos date."""
    if valor is None or pd.isna(valor):
        return None

    if isinstance(valor, date) and not isinstance(valor, datetime):
        return valor

    if isinstance(valor, datetime):
        return valor.date()

    try:
        return pd.to_datetime(valor).date()
    except Exception:
        return None


def _es_fin_de_semana(fecha: date | None = None) -> bool:
    """Indica si la fecha actual corresponde a fin de semana."""
    fecha_actual = fecha or date.today()
    return fecha_actual.weekday() >= 5


def _es_fin_de_mes(fecha: date | None = None) -> bool:
    """Indica si la fecha actual corresponde al fin de mes."""
    fecha_actual = fecha or date.today()
    ultimo_dia = calendar.monthrange(fecha_actual.year, fecha_actual.month)[1]
    return fecha_actual.day >= ultimo_dia - 1


def _normalizar_payload_modelo(payload: Any) -> dict[str, Any]:
    """Adapta modelos viejos o nuevos al formato esperado en disco."""
    if isinstance(payload, dict) and "model_by_local" in payload:
        return payload

    if isinstance(payload, LinearRegression):
        return {
            "model_by_local": {"general": payload},
            "feature_columns": ["cantidad_personas", "es_fin_de_semana"],
            "created_at": datetime.utcnow().isoformat(),
        }

    raise ValueError("El archivo del modelo no tiene el formato esperado.")


def _serialize_payload_to_bytes(payload: dict[str, Any]) -> bytes:
    buf = BytesIO()
    joblib.dump(payload, buf)
    return buf.getvalue()


def _deserialize_payload_from_bytes(data: bytes) -> dict[str, Any]:
    payload = joblib.load(BytesIO(data))
    if not isinstance(payload, dict):
        raise ValueError("Payload de modelo inválido.")
    return _normalizar_payload_modelo(payload)


def _download_payload_from_supabase_storage() -> dict[str, Any] | None:
    settings = get_settings()
    if get_supabase_client is None:
        return None

    supabase = get_supabase_client()
    storage = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_MESAS_MODELS)
    obj = storage.download(settings.SUPABASE_STORAGE_OBJECT_MESAS_MODEL)

    data: bytes | None = None
    if isinstance(obj, (bytes, bytearray)):
        data = bytes(obj)
    elif hasattr(obj, "read"):
        data = obj.read()
    elif hasattr(obj, "content") and isinstance(getattr(obj, "content"), (bytes, bytearray)):
        data = bytes(getattr(obj, "content"))
    elif hasattr(obj, "data") and isinstance(getattr(obj, "data"), (bytes, bytearray)):
        data = bytes(getattr(obj, "data"))

    if data is None:
        # último recurso: convertir a bytes (si el SDK lo devuelve como stream/response)
        try:
            data = bytes(obj)  # type: ignore[arg-type]
        except Exception:
            return None

    return _deserialize_payload_from_bytes(data)


def _upload_payload_to_supabase_storage(payload: dict[str, Any]) -> None:
    settings = get_settings()
    if get_supabase_client is None:
        raise RuntimeError("No hay un cliente de Supabase disponible para subir el modelo.")

    supabase = get_supabase_client()
    storage = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET_MESAS_MODELS)

    data = _serialize_payload_to_bytes(payload)
    object_path = settings.SUPABASE_STORAGE_OBJECT_MESAS_MODEL

    try:
        storage.upload(
            path=object_path,
            file=data,
            file_options={"content-type": "application/octet-stream"},
        )
    except Exception as exc:
        # Idempotencia para re-entrenar: si el objeto ya existe, eliminar y re-subir.
        # El error puede venir con estructura dict/str dependiendo del SDK.
        msg = str(exc)
        is_duplicate = "409" in msg or "Duplicate" in msg or "already exists" in msg

        if not is_duplicate:
            raise

        try:
            # Intentar eliminar el objeto existente
            storage.remove(object_path)
        except Exception:
            # Si falla el remove igual intentamos subir (por algunas implementaciones el estado puede cambiar)
            pass

        storage.upload(
            path=object_path,
            file=data,
            file_options={"content-type": "application/octet-stream"},
        )


def cargar_modelo_en_memoria() -> dict[str, Any] | None:
    """Carga el modelo (preferente Supabase Storage) una sola vez y lo mantiene en memoria."""
    global MODEL_CACHE

    if MODEL_CACHE is not None:
        return MODEL_CACHE

    # Preferir Supabase (read-only server)
    try:
        payload = _download_payload_from_supabase_storage()
        MODEL_CACHE = payload
        return MODEL_CACHE
    except Exception:
        # fallback a disco (solo desarrollo; no es requerido para producción read-only)
        MODEL_CACHE = None

    try:
        if not MODEL_PATH.exists():
            return None
        payload = joblib.load(MODEL_PATH)
        MODEL_CACHE = _normalizar_payload_modelo(payload)
    except Exception:
        MODEL_CACHE = None

    return MODEL_CACHE


# Carga inicial del modelo al importar el módulo.
MODEL_CACHE = cargar_modelo_en_memoria()


def entrenar_modelo(local: str | int | None = None) -> dict[str, Any]:
    """Entrena un modelo de regresión lineal múltiple para un local concreto."""
    cliente_supabase = get_supabase_client() if get_supabase_client is not None else None
    if cliente_supabase is None:
        raise RuntimeError("No hay un cliente de Supabase disponible para entrenar el modelo.")

    try:
        response = (
            cliente_supabase.table("ventas")
            .select("fecha, ocupacion, cantidad_personas, id_localfk")
            .execute()
        )
        registros = response.data or []
    except Exception as exc:  # pragma: no cover - guard against unexpected failures
        raise RuntimeError(f"No se pudieron leer los registros de ventas: {exc}") from exc

    local_key = _normalizar_local(local)
    if local is not None:
        registros = [registro for registro in registros if _coincide_local(registro, local_key)]

    if len(registros) < 10:
        raise ValueError("Se necesitan al menos 10 registros para entrenar el modelo.")

    datos = pd.DataFrame(registros)
    datos = datos[["fecha", "ocupacion", "cantidad_personas"]].copy()
    datos = datos.dropna(subset=["fecha", "ocupacion", "cantidad_personas"])

    if len(datos) < 10:
        raise ValueError("Se necesitan al menos 10 registros válidos para entrenar el modelo.")

    datos["cantidad_personas"] = pd.to_numeric(datos["cantidad_personas"], errors="coerce").fillna(0).astype(int)
    datos["tiempo_ocupacion_minutos"] = datos["ocupacion"].apply(_parsear_ocupacion_a_minutos)
    datos["es_fin_de_semana"] = datos["fecha"].apply(_extraer_fecha).apply(_es_fin_de_semana).astype(int)

    X = datos[["cantidad_personas", "es_fin_de_semana"]]
    y = datos["tiempo_ocupacion_minutos"]

    modelo = LinearRegression()
    modelo.fit(X, y)

    payload = {
        "model_by_local": {local_key: modelo},
        "feature_columns": ["cantidad_personas", "es_fin_de_semana"],
        "created_at": datetime.utcnow().isoformat(),
    }

    # Subir a Supabase Storage (read-only server)
    _upload_payload_to_supabase_storage(payload)

    # Mantener cache en memoria para la instancia actual
    global MODEL_CACHE
    MODEL_CACHE = payload

    info = get_settings()
    return {
        "mensaje": "Modelo entrenado correctamente",
        "registros_usados": int(len(datos)),
        "storage_bucket": info.SUPABASE_STORAGE_BUCKET_MESAS_MODELS,
        "storage_object": info.SUPABASE_STORAGE_OBJECT_MESAS_MODEL,
        "local": local_key,
    }


def predecir_tiempo_ocupacion(
    cantidad_personas: int,
    local: str | int | None = None,
    es_dia_festivo: bool = False,
) -> dict[str, Any]:
    """Predice el tiempo de ocupación usando el modelo de Supabase (si existe) o fórmula de respaldo."""
    if cantidad_personas < 0:
        raise ValueError("cantidad_personas debe ser mayor o igual a 0.")

    local_key = _normalizar_local(local)
    fecha_hoy = date.today()
    es_fin_de_semana = _es_fin_de_semana(fecha_hoy)
    es_fin_de_mes = _es_fin_de_mes(fecha_hoy)

    # Forzamos consistencia con el modelo entrenado en Supabase.
    # cargar_modelo_en_memoria prioriza Supabase, y mantiene cache para esta instancia.
    modelo_payload = cargar_modelo_en_memoria()
    if modelo_payload is not None:
        modelo_por_local = modelo_payload.get("model_by_local", {})
        modelo = modelo_por_local.get(local_key) or modelo_por_local.get("general")
        if modelo is not None:
            # el modelo fue entrenado con features:
            #   X = [["cantidad_personas", "es_fin_de_semana"]]
            features = [[float(cantidad_personas), 1.0 if es_fin_de_semana else 0.0]]
            tiempo_estimado = int(round(float(modelo.predict(features)[0])))
            return {
                "tiempo_estimado_minutos": tiempo_estimado,
                "metodo": "modelo_regresion",
                "local": local_key,
            }

    # fallback teórico si el modelo no existe o no tiene modelo para el local solicitado
    tiempo_estimado = 30 + (15 * cantidad_personas)
    if es_fin_de_semana:
        tiempo_estimado += 15
    if es_fin_de_mes:
        tiempo_estimado += 10
    if es_dia_festivo:
        tiempo_estimado += 10

    return {
        "tiempo_estimado_minutos": tiempo_estimado,
        "metodo": "formula_teorica",
        "local": local_key,
    }
