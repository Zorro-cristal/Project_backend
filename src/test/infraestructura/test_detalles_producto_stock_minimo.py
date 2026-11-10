import asyncio

from src.infraestructura.repositories import detalles_producto_repository


def test_stock_minimo_de_comidas_se_calcula_segun_ingredientes(monkeypatch):
    async def fake_get(table, filtros=None, limit=100, offset=0, columns="*"):
        filtros = filtros or {}
        if table == "detalles_producto" and "id_productofk" not in filtros:
            return [
                {
                    "cod_barra": "FOOD-1",
                    "id_productofk": 1,
                    "productos": {"id": 10, "es_comida": True},
                },
                {
                    "cod_barra": "FOOD-2",
                    "id_productofk": 2,
                    "productos": {"id": 20, "es_comida": True},
                },
            ]
        if table == "stocks":
            quantities = {
                "FOOD-1": (100, 0),
                "FOOD-2": (100, 0),
                "ING-A": (8, 0),
                "ING-B": (9, 0),
            }
            return [
                {
                    "id_detalleproductofk": code,
                    "cant_mostrador": quantities[code][0],
                    "cant_deposito": quantities[code][1],
                }
                for code in filtros["id_detalleproductofk"]
                if code in quantities
            ]
        if table == "ingredientes":
            return [
                {
                    "id_producto_finalfk": 10,
                    "id_producto_ingredientefk": 100,
                    "cantidad": 2,
                },
                {
                    "id_producto_finalfk": 10,
                    "id_producto_ingredientefk": 200,
                    "cantidad": 3,
                },
                {
                    "id_producto_finalfk": 20,
                    "id_producto_ingredientefk": 100,
                    "cantidad": 4,
                },
                {
                    "id_producto_finalfk": 20,
                    "id_producto_ingredientefk": 200,
                    "cantidad": 5,
                },
            ]
        if table == "detalles_producto":
            return [
                {"id_productofk": 100, "cod_barra": "ING-A"},
                {"id_productofk": 200, "cod_barra": "ING-B"},
            ]
        raise AssertionError(f"Consulta inesperada: {table}")

    monkeypatch.setattr(detalles_producto_repository, "get", fake_get)

    result = asyncio.run(
        detalles_producto_repository.obtenerDetalleProducto(
            filtros={"stock_minimo": 2},
            limite=10,
        )
    )

    assert [(item["cod_barra"], item["stock_total"]) for item in result] == [
        ("FOOD-1", 3)
    ]
    assert "producto" not in result[0]
    assert "productos" not in result[0]


def test_stock_minimo_de_comidas_excluye_si_no_alcanza_el_minimo(monkeypatch):
    async def fake_get(table, filtros=None, limit=100, offset=0, columns="*"):
        filtros = filtros or {}
        if table == "detalles_producto" and "id_productofk" not in filtros:
            return [
                {
                    "cod_barra": "FOOD-1",
                    "id_productofk": 1,
                    "productos": {"id": 10, "es_comida": True},
                }
            ]
        if table == "stocks":
            quantities = {"FOOD-1": 100, "ING-A": 8, "ING-B": 9}
            return [
                {
                    "id_detalleproductofk": code,
                    "cant_mostrador": quantities[code],
                    "cant_deposito": 0,
                }
                for code in filtros["id_detalleproductofk"]
                if code in quantities
            ]
        if table == "ingredientes":
            return [
                {
                    "id_producto_finalfk": 10,
                    "id_producto_ingredientefk": 100,
                    "cantidad": 2,
                },
                {
                    "id_producto_finalfk": 10,
                    "id_producto_ingredientefk": 200,
                    "cantidad": 3,
                },
            ]
        if table == "detalles_producto":
            return [
                {"id_productofk": 100, "cod_barra": "ING-A"},
                {"id_productofk": 200, "cod_barra": "ING-B"},
            ]
        raise AssertionError(f"Consulta inesperada: {table}")

    monkeypatch.setattr(detalles_producto_repository, "get", fake_get)

    result = asyncio.run(
        detalles_producto_repository.obtenerDetalleProducto(
            filtros={"stock_minimo": 4},
            limite=10,
        )
    )

    assert result == []
