import asyncio
import sqlite3

from src.infraestructura.services import orden_service, stock_service
from src.infraestructura.services import orden_stock
from src.shell.adapters.database import generic_crud


def test_obtener_stocks_con_stock_filters_positive_quantities(monkeypatch, tmp_path):
    database_path = tmp_path / "stocks.sqlite"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE stocks (
            id INTEGER PRIMARY KEY,
            id_detalleproductofk TEXT,
            cant_mostrador INTEGER,
            cant_deposito INTEGER,
            cant_reservado INTEGER,
            fecha_vencimiento TEXT
        )
        """
    )
    connection.executemany(
        """
        INSERT INTO stocks
            (id, id_detalleproductofk, cant_mostrador, cant_deposito,
             cant_reservado, fecha_vencimiento)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (1, "SKU-1", 0, 3, 0, "2026-01-01"),
            (2, "SKU-1", 2, 0, 0, "2026-02-01"),
            (3, "SKU-1", 0, 0, 5, "2026-03-01"),
        ],
    )
    connection.commit()
    connection.close()
    monkeypatch.setattr(
        generic_crud,
        "get_turso_connection",
        lambda: sqlite3.connect(database_path, check_same_thread=False),
    )

    async def no_related_data(stocks):
        return stocks

    monkeypatch.setattr(stock_service, "attach_related_data", no_related_data)

    stocks = asyncio.run(
        stock_service.obtener_stocks(
            filtros={"id_detalleproductofk": "SKU-1", "con_stock": 1}
        )
    )

    assert [stock["id"] for stock in stocks] == [1, 2]


def test_actualizar_orden_a_entregado_liberates_reservation_once(monkeypatch):
    released = []
    updates = []
    current_order = {
        "id": 8,
        "estado": 3,
        "cantidad": 2,
        "id_detalleproductofk": "SKU-1",
    }

    async def obtener_ordenes(**_kwargs):
        return [current_order.copy()]

    async def desreservar(**kwargs):
        released.append(kwargs)

    async def actualizar(payload, order_id):
        updates.append((payload, order_id))
        current_order.update(payload)
        return {"id": order_id, **payload}

    monkeypatch.setattr(orden_service, "obtenerOrdenes", obtener_ordenes)
    monkeypatch.setattr(orden_service, "desreservar_stock_para_orden", desreservar)
    monkeypatch.setattr(orden_service, "actualizarOrden", actualizar)

    result = asyncio.run(orden_service.actualizar_orden_por_id(8, {"estado": 4}))
    asyncio.run(orden_service.actualizar_orden_por_id(8, {"estado": 4}))

    assert released == [
        {"id_detalleproductofk": "SKU-1", "cantidad_a_liberar": 2}
    ]
    assert updates == [({"estado": 4}, 8), ({"estado": 4}, 8)]
    assert result == {"id": 8, "estado": 4}


def test_desreservar_orden_de_comida_aplica_multiplicador_por_ingrediente(monkeypatch):
    released = []

    async def obtener_detalles_productos(filtros, include_producto):
        if "cod_barra" in filtros:
            return [{"producto": {"id": 15, "es_comida": True}}]
        assert include_producto is False
        return [{"cod_barra": "ING-1"}]

    async def obtener_ingredientes(filtros):
        assert filtros == {"id_producto_finalfk": 15}
        return [
            {
                "id_producto_ingredientefk": 16,
                "cantidad": 3,
            }
        ]

    async def desreservar(**kwargs):
        released.append(kwargs)

    monkeypatch.setattr(
        orden_stock, "obtener_detalles_productos", obtener_detalles_productos
    )
    monkeypatch.setattr(orden_stock, "obtener_ingredientes", obtener_ingredientes)
    monkeypatch.setattr(
        orden_stock, "_desreservar_stock_fifo_por_detalle", desreservar
    )

    asyncio.run(
        orden_stock.desreservar_stock_para_orden(
            id_detalleproductofk="PLATO-1",
            cantidad_a_liberar=2,
        )
    )

    assert released == [
        {"id_detalleproductofk": "ING-1", "cantidad_a_liberar": 6}
    ]
