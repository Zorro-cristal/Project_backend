import logging
from datetime import datetime, timezone
from typing import Optionali import printer_api
from src.infraestructura.services import orden_service, print_service
from ..repositories.mesa_repository import obtenerMesa import ConnectionManager
from ..repositories.orden_repository import actualizarOrden
from ..websockets.connection_manager import connection_manager
from ..services.orden_service import obtener_orden_por_idclass DummyWebSocket:

logger = logging.getLogger(__name__)        self.sent = []

# Estados de impresión soportados
ESTADO_IMPRESION_PENDIENTE = "PENDIENTE"
ESTADO_IMPRESION_IMPRESO = "IMPRESO"
ESTADO_IMPRESION_FALLO = "FALLO"    async def send_json(self, payload):

# Mensajes de error estandarizados
ERROR_LOCAL_OFFLINE = "Local sin conexión activa"
ERROR_SIN_LOCAL = "La orden no tiene un local asociado (mesa sin local)"        return None


def build_ticket_payload(orden: dict) -> dict:
    """Construye el payload del ticket de impresión a partir de la orden creada.    manager = ConnectionManager()

    El payload es una estructura simple serializable (dict) que el cliente
    Flutter usará para renderizar el ticket. La orden puede llegar como dict
    (resultado de Supabase) o como dataclass `Orden`.ert manager.is_connected("local-7")
    """"local-7", {"event": "print_job", "job_id": "42"})) is True
    if hasattr(orden, '__dataclass_fields__'):
        orden = _dataclass_to_dict(orden)    asyncio.run(manager.disconnect("local-7"))

    detalle_producto = orden.get("detalle_producto") or {}
    producto = detalle_producto.get("producto") or {}
    mesa = orden.get("mesa") or {}def test_connection_manager_reports_active_connections():
= ConnectionManager()
    return {
        "event": "print_job",
        "job_id": str(orden.get("id")),al-7") is False
        "orden_id": orden.get("id"),-7"))
        "cantidad": orden.get("cantidad"),ue
        "observacion": orden.get("observacion"),ons["local-7"]) == 1
        "estado": orden.get("estado"),
        "mesa": {
            "id": mesa.get("id"),_antes_del_dispatch(monkeypatch):
            "nombre": mesa.get("nombre"),
            "id_local": mesa.get("id_local") or mesa.get("id_localfk"),
        },talles_productos(filtros, include_producto=True, **_kwargs):
        "producto": {
            "id": producto.get("id"),
            "nombre": producto.get("nombre"),
            "descripcion": producto.get("descripcion"),  "id_productofk": {
        },
        "detalle_producto": {
            "cod_barra": detalle_producto.get("cod_barra"),,
            "color": detalle_producto.get("color"),      "es_comida": False,
        },
        "precio": {
            "id": (orden.get("precio") or {}).get("id"),
            "monto": (orden.get("precio") or {}).get("monto"),def fake_stock(**kwargs):
        },
        "fecha_creado": orden.get("fecha_creado"),
    }    async def fake_update(payload):
        return {

def _dataclass_to_dict(orden) -> dict:
    """Convierte una dataclass `Orden` a dict (solo campos primitivos).""": "2000000001",
    from dataclasses import asdict            "id_preciofk": 3,
1,
    data = asdict(orden)
    # Eliminar objetos anidados (mesa, precio, usuario) que no son primitivos
    for key in ("mesa", "precio", "usuario"):
        data.pop(key, None)
    return data    async def fake_attach_related(orders):
        orders[0]["mesa"] = {"id": 7, "nombre": "Mesa 7", "id_localfk": 1}

async def resolve_id_local(orden: dict) -> Optional[int]:
    """Resuelve el `id_local` al que pertenece la orden a través de su mesa o tipo.            "cod_barra": "2000000001",

    La orden tiene `id_mesafk`; la mesa tiene `id_localfk`. Si no se puede
    resolver (orden sin mesa o mesa sin local), retorna `None`.         "id": 15,
    """",
    id_mesafk = orden.get("id_mesafk")": "Carne, queso y pan",
    tipo = orden.get("tipo")            },

    if id_mesafk is None:
        # Si es delivery (tipo 2), no intentamos resolver local por mesa para impresión automática
        if tipo == 2:atch(order):
            return Noneappend(order)
        return None
_productos", fake_detalles_productos)
    mesas = await obtenerMesa(filtros={"id": id_mesafk})etattr(orden_service, "consumir_stock_para_orden", fake_stock)
    if not mesas:attr(orden_service, "actualizarOrden", fake_update)
        return None    monkeypatch.setattr(orden_service, "attach_related_data", fake_attach_related)
attr(orden_service, "dispatch_print_job", fake_dispatch)
    mesa = mesas[0]
    return mesa.get("id_localfk")    result = asyncio.run(orden_service.crear_orden({
        "cantidad": 1,

async def get_pending_print_orders(id_local: str) -> list[dict]:
    """Obtiene las órdenes pendientes de impresión de un local."""
    from ..repositories.orden_repository import obtenerOrdenes
    from .orden_service import attach_related_data    }))

    pending_orders = await obtenerOrdenes(
        filtros={"estado_impresion": ESTADO_IMPRESION_PENDIENTE},atched) == 1
        limite=100,ched[0]["mesa"]["id_localfk"] == 1
        offset=0,ssert dispatched[0]["detalle_producto"]["producto"]["nombre"] == "Hamburguesa"
    )
    if not pending_orders:
        return []def test_dispatch_print_job_marks_local_offline(monkeypatch):

    pending_orders = await attach_related_data(pending_orders)
    local_id = int(id_local)ve_id_local(_orden):
    matching_orders = []
    for order in pending_orders:
        if await resolve_id_local(order) == local_id:id):
            matching_orders.append(order)den_id, payload))
    return matching_orders        return {"id": orden_id, **payload}

_local", fake_resolve_id_local)
async def dispatch_print_job(orden: dict) -> None:
    """Tarea en segundo plano que despacha el trabajo de impresión.    async def fake_send_print_job(*_args, **_kwargs):

    - Obtiene el payload del ticket formateado a partir de la orden creada.
    - Intenta enviar el payload por el `ConnectionManager` al local de la orden., fake_send_print_job)
    - Si el local no está conectado (o no se puede resolver), actualiza lapdate)
      orden con `last_print_error` y `estado_impresion = FALLO`.
    """afk": 7}
    orden_id = orden.get("id")cio.run(print_service.dispatch_print_job(orden))
    try:
        # 1) Resolver el local asociado a la orden
        id_local = await resolve_id_local(orden)tado_impresion"] == "FALLO"
        if id_local is None: conexión activa"
            await _marcar_error(orden_id, ERROR_SIN_LOCAL)
            return
monkeypatch):
        # 2) Construir payload del ticket
        payload = build_ticket_payload(orden)

        # Imprimir en la terminal los datos enviados para depuración
        logger.info(f"Despachando print_job para orden {orden_id} al local {id_local}: {payload}")        return {"id": orden_id, **payload}

        # 3) Intentar el envío
        enviado = await connection_manager.send_print_job(str(id_local), payload)
nt_service.process_print_ack({
        if enviado:
            await actualizarOrden({
                "estado_impresion": ESTADO_IMPRESION_PENDIENTE,SS",
            }, orden_id)r_message": None,
        else:
            await _marcar_error(orden_id, ERROR_LOCAL_OFFLINE)
    except Exception as exc:
        logger.exception(f"Error en dispatch_print_job para orden {orden_id}: {exc}")
        await _marcar_error(orden_id, f"Error al despachar impresión: {exc}")    assert updates[0][1]["last_print_error"] is None


async def _marcar_error(rders_filters_by_local(monkeypatch):
    orden_id: Optional[int],filtros, limite, offset):
    error_message: str,sert filtros == {"estado_impresion": "PENDIENTE"}
) -> None:
    """Actualiza la orden marcándola como FALLO con el error correspondiente.""" 0
    if orden_id is None:
        logger.error(f"No se pudo actualizar estado de impresión: {error_message}")id": 1, "estado_impresion": "PENDIENTE", "id_mesafk": 10},
        returnd": 2, "estado_impresion": "IMPRESO", "id_mesafk": 11},
    updates = {
        "estado_impresion": ESTADO_IMPRESION_FALLO,
        "last_print_error": error_message,sync def fake_attach(orders):
    }return orders
    try:
        await actualizarOrden(updates, orden_id)rder):
    except Exception as exc:
        logger.error(f"No se pudo marcar error en orden {orden_id}: {exc}")
    monkeypatch.setattr(
ository.obtenerOrdenes",
async def process_print_ack(message: dict) -> None:
    """Procesa una confirmación (ACK) de impresión proveniente del cliente.    )

    El formato esperado del mensaje:c.infraestructura.services.orden_service.attach_related_data",
    ```json   fake_attach,
    {
      "event": "print_ack",ce, "resolve_id_local", fake_resolve)
      "job_id": "uuid-de-la-orden",
      "status": "SUCCESS",  // o "FALLO"rint_service.get_pending_print_orders("7"))
      "error_message": null
    }ert [order["id"] for order in pending] == [1]
    ```
    """
    if message.get("event") != "print_ack":ng_print_orders_endpoint_returns_jobs(monkeypatch):
        return    async def fake_pending(_id_local):
_impresion": "PENDIENTE"}]
    job_id = message.get("job_id")
    if job_id is None:nt_orders", fake_pending)
        logger.warning("ACK de impresión sin job_id")
        return    response = asyncio.run(printer_api.pending_print_orders("7"))

    status = message.get("status", "FALLO")
    error_message = message.get("error_message")    assert response["orders"][0]["print_job"] == {
",
    if status == "SUCCESS":42",
        updates = {
            "estado_impresion": ESTADO_IMPRESION_IMPRESO,
            "last_print_error": None,observacion": None,
        }
        logger.info(f"Impresión confirmada para orden {job_id}")mesa": {"id": None, "nombre": None, "id_local": None},
    else: {"id": None, "nombre": None, "descripcion": None},
        updates = {: None},
            "estado_impresion": ESTADO_IMPRESION_FALLO,
            "last_print_error": error_message or "Fallo reportado por el cliente",fecha_creado": None,
        }
        logger.warning(f"Impresión fallida para orden {job_id}: {error_message}")    try:        # 1) Actualizar la base de datos primero        await actualizarOrden(updates, job_id)        
        # 2) Obtener detalles de la orden para saber a qué local notificar
        orden = await obtener_orden_por_id({'id': int(job_id)})
        if orden and 'mesa' in orden and orden['mesa']:
            id_local = order['mesa'].get('id_local') or order['mesa'].get('id_localfk')
            if id_local:
                # 3) Enviar notificación por WebSocket para actualización en tiempo real
                notification = {
                    "event": "order_status_changed",
                    "orden_id": job_id,
                    "estado_impresion": updates["estado_impresion"],
                    "last_print_error": updates["last_print_error"]
                }
                connection_manager.send_notification(str(id_local), notification)
                logger.info(f"Notificación de estado enviada al local {id_local} para la orden {job_id}")

    except Exception as exc:
        logger.error(f"No se pudo actualizar o notificar la orden {job_id}: {exc}")
