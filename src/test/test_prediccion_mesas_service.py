from __future__ import annotations

import calendar
from datetime import date

import pytest

import src.infraestructura.services.prediccion_mesas_service as prediccion_mesas_service


class DummyResponse:
    def __init__(self, data):
        self.data = data


class DummyTable:
    def __init__(self, data):
        self._data = data

    def select(self, *_args, **_kwargs):
        return self

    def execute(self):
        return DummyResponse(self._data)


class DummySupabaseClient:
    def __init__(self, data):
        self._data = data

    def table(self, _name: str):
        return DummyTable(self._data)


def test_entrenar_modelo_aborta_con_menos_de_10_registros(monkeypatch):
    monkeypatch.setattr(prediccion_mesas_service, "get_supabase_client", lambda: DummySupabaseClient([]))
    monkeypatch.setattr(prediccion_mesas_service, "MODEL_CACHE", None)

    with pytest.raises(ValueError, match="al menos 10"):
        prediccion_mesas_service.entrenar_modelo()


def test_predecir_tiempo_usa_formula_teorica_si_no_hay_modelo(monkeypatch):
    monkeypatch.setattr(prediccion_mesas_service, "MODEL_CACHE", None)

    resultado = prediccion_mesas_service.predecir_tiempo_ocupacion(4, "local-1", True)

    today = date.today()
    esperado = 30 + (15 * 4)
    if today.weekday() >= 5:
        esperado += 15
    if today.day >= calendar.monthrange(today.year, today.month)[1] - 1:
        esperado += 10
    esperado += 10

    assert resultado["tiempo_estimado_minutos"] == esperado
    assert resultado["metodo"] == "formula_teorica"
