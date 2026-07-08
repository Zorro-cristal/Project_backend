import pandas as pd

from src.infraestructura.services.prediccion_ventas_service import (
    build_daily_prediction_payloads,
    build_feature_frame,
    train_sales_forecast_model,
)


def test_build_feature_frame_creates_engineered_features() -> None:
    data = pd.DataFrame(
        [
            {
                "fecha": "2024-01-06",
                "evento_festivo": True,
                "condicion_clima": "soleado",
                "ventas_totales": 120.5,
            }
        ]
    )
    data["fecha"] = pd.to_datetime(data["fecha"])

    features = build_feature_frame(data)

    assert "dia_semana" in features.columns
    assert "mes" in features.columns
    assert "fin_de_semana" in features.columns
    assert "cercania_pago" in features.columns
    assert "clima_soleado" in features.columns
    assert bool(features.iloc[0]["fin_de_semana"]) is True


def test_build_feature_frame_includes_fin_de_mes() -> None:
    data = pd.DataFrame(
        [{"fecha": "2024-01-31", "evento_festivo": False, "condicion_clima": "soleado", "ventas_totales": 130.0}]
    )
    data["fecha"] = pd.to_datetime(data["fecha"])

    features = build_feature_frame(data)

    assert "fin_de_mes" in features.columns


def test_build_daily_prediction_payloads_returns_message_shape() -> None:
    payloads = build_daily_prediction_payloads(
        fecha_inicio="2026-07-05",
        fecha_fin="2026-07-06",
        dias_festivos=[],
        weather_forecast_by_date={
            "2026-07-05": {
                "temperatura_max": 28.5,
                "humedad": 65,
                "condicion_clima": "lluvioso",
                "velocidad_viento": 3.2,
                "lluvia": 1.5,
                "precipitaciones": 2.2,
                "probabilidad_precipitaciones": 70,
            },
            "2026-07-06": {
                "temperatura_max": 30.0,
                "humedad": 58,
                "condicion_clima": "soleado",
                "velocidad_viento": 2.1,
                "lluvia": 0.0,
                "precipitaciones": 0.0,
                "probabilidad_precipitaciones": 10,
            },
        },
        ventas_previstas_por_fecha={"2026-07-05": 150000.0, "2026-07-06": 170000.0},
    )

    assert len(payloads["message"]) == 2
    assert payloads["message"][0]["datos_meteorologicos"]["condicion_clima"] == "lluvioso"
    assert payloads["message"][0]["datos_meteorologicos"]["velocidad_viento"] == 3.2
    assert payloads["message"][0]["datos_meteorologicos"]["lluvia"] == 1.5
    assert payloads["message"][0]["datos_meteorologicos"]["precipitaciones"] == 2.2
    assert payloads["message"][0]["datos_meteorologicos"]["probabilidad_precipitaciones"] == 70
    assert payloads["message"][0]["prevision_productos"][0]["categoria"] == "Platos Principales"


def test_train_sales_forecast_model_returns_predictor() -> None:
    data = pd.DataFrame(
        [
            {"fecha": "2024-01-01", "evento_festivo": False, "condicion_clima": "soleado", "ventas_totales": 100.0},
            {"fecha": "2024-01-02", "evento_festivo": False, "condicion_clima": "nublado", "ventas_totales": 90.0},
            {"fecha": "2024-01-03", "evento_festivo": True, "condicion_clima": "lluvioso", "ventas_totales": 140.0},
            {"fecha": "2024-01-04", "evento_festivo": False, "condicion_clima": "soleado", "ventas_totales": 110.0},
        ]
    )
    data["fecha"] = pd.to_datetime(data["fecha"])

    model = train_sales_forecast_model(data)

    assert model is not None
    assert hasattr(model, "predict")
