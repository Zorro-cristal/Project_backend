import asyncio

from src.infraestructura.api import printer_api
from src.infraestructura.services import print_service
from src.infraestructura.websockets.connection_manager import ConnectionManager


class DummyWebSocket:
    def __init__(self):
        self.sent = []

    async def accept(self):
        return None

    async def send_json(self, payload):
        self.sent.append(payload)

    async def close(self):
        return None


def test_connection_manager_send_print_job_routes_by_local():
    manager = ConnectionManager()
    ws = DummyWebSocket()

    asyncio.run(manager.connect(ws, "local-7"))
    assert manager.is_connected("local-7")
    assert asyncio.run(manager.send_print_job("local-7", {"event": "print_job", "job_id": "42"})) is True

    asyncio.run(manager.disconnect("local-7"))
    assert manager.is_connected("local-7") is False


def test_connection_manager_reports_active_connections():
    manager = ConnectionManager()
    ws = DummyWebSocket()

    assert manager.is_connected("local-7") is False
    asyncio.run(manager.connect(ws, "local-7"))
    assert manager.is_connected("local-7") is True
    assert len(manager.active_connections["local-7"]) == 1


def test_dispatch_print_job_marks_local_offline(monkeypatch):
    updates = []

    async def fake_resolve_id_local(_orden):
        return 99

    async def fake_update(payload, orden_id):
        updates.append((orden_id, payload))
        return {"id": orden_id, **payload}

    monkeypatch.setattr(print_service, "resolve_id_local", fake_resolve_id_local)

    async def fake_send_print_job(*_args, **_kwargs):
        return False

    monkeypatch.setattr(print_service.connection_manager, "send_print_job", fake_send_print_job)
    monkeypatch.setattr(print_service, "actualizarOrden", fake_update)

    orden = {"id": 42, "id_mesafk": 7}
    asyncio.run(print_service.dispatch_print_job(orden))

    assert updates
    assert updates[0][1]["estado_impresion"] == "FALLO"
    assert updates[0][1]["last_print_error"] == "Local sin conexión activa"


def test_process_print_ack_marks_success(monkeypatch):
    updates = []

    async def fake_update(payload, orden_id):
        updates.append((orden_id, payload))
        return {"id": orden_id, **payload}

    monkeypatch.setattr(print_service, "actualizarOrden", fake_update)

    asyncio.run(print_service.process_print_ack({
        "event": "print_ack",
        "job_id": "42",
        "status": "SUCCESS",
        "error_message": None,
    }))

    assert updates
    assert updates[0][1]["estado_impresion"] == "IMPRESO"
    assert updates[0][1]["last_print_error"] is None


def test_get_pending_print_orders_filters_by_local(monkeypatch):
    async def fake_get(filtros, limite, offset):
        assert filtros == {"estado_impresion": "PENDIENTE"}
        assert limite == 100
        assert offset == 0
        return [
            {"id": 1, "estado_impresion": "PENDIENTE", "id_mesafk": 10},
            {"id": 2, "estado_impresion": "IMPRESO", "id_mesafk": 11},
        ]

    async def fake_attach(orders):
        return orders

    async def fake_resolve(order):
        return 7 if order["id"] == 1 else 8

    monkeypatch.setattr(
        "src.infraestructura.repositories.orden_repository.obtenerOrdenes",
        fake_get,
    )
    monkeypatch.setattr(
        "src.infraestructura.services.orden_service.attach_related_data",
        fake_attach,
    )
    monkeypatch.setattr(print_service, "resolve_id_local", fake_resolve)

    pending = asyncio.run(print_service.get_pending_print_orders("7"))

    assert [order["id"] for order in pending] == [1]


def test_pending_print_orders_endpoint_returns_jobs(monkeypatch):
    async def fake_pending(_id_local):
        return [{"id": 42, "estado_impresion": "PENDIENTE"}]

    monkeypatch.setattr(printer_api, "get_pending_print_orders", fake_pending)

    response = asyncio.run(printer_api.pending_print_orders("7"))

    assert response["count"] == 1
    assert response["orders"][0]["print_job"] == {
        "event": "print_job",
        "job_id": "42",
        "orden_id": 42,
        "cantidad": None,
        "observacion": None,
        "estado": None,
        "mesa": {"id": None, "nombre": None},
        "producto": {"id": None, "nombre": None, "descripcion": None},
        "detalle_producto": {"cod_barra": None, "color": None},
        "precio": {"id": None, "monto": None},
        "fecha_creado": None,
    }
