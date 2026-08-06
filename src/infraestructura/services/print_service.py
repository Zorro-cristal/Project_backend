import logging
from datetime import datetime, timezone
from typing import Optional

from ..repositories.mesa_repository import obtenerMesa
from ..repositories.orden_repository import actualizarOrden
from ..websockets.connection_manager import connection_manager

logger = logging.getLogger(__name__)

# Estados de impresión soportados
PRINT_STATUS_PENDING = "PENDING"
PRINT_STATUS_PRINTED = "PRINTED"
PRINT_STATUS_FAILED = "FAILED"

# Mensajes de error estandarizados
ERROR_LOCAL_OFFLINE = "Local sin conexión activa"
ERROR_SIN_LOCAL = "La orden no tiene un local asociado (mesa sin local)"


def build_ticket_payload(orden: dict) -> dict:
    """Construye el payload del ticket de impresión a partir de la orden creada.

    El payload es una estructura simple serializable (dict) que el cliente
    Flutter usará para renderizar el ticket. La orden puede llegar como dict
    (resultado de Supabase) o como dataclass `Orden`.
    """
    if hasattr(orden, '__dataclass_fields__'):
        orden = _dataclass_to_dict(orden)

    detalle_producto = orden.get("detalle_producto") or {}
    producto = detalle_producto.get("producto") or {}
    mesa = orden.get("mesa") or {}

    return {
        "event": "print_job",
        "job_id": str(orden.get("id")),
        "orden_id": orden.get("id"),
        "cantidad": orden.get("cantidad"),
        "observacion": orden.get("observacion"),
        "estado": orden.get("estado"),
        "mesa": {
            "id": mesa.get("id"),
            "nombre": mesa.get("nombre"),
        },
        "producto": {
            "id": producto.get("id"),
            "nombre": producto.get("nombre"),
            "descripcion": producto.get("descripcion"),
        },
        "detalle_producto": {
            "cod_barra": detalle_producto.get("cod_barra"),
            "color": detalle_producto.get("color"),
        },
        "precio": {
            "id": (orden.get("precio") or {}).get("id"),
            "monto": (orden.get("precio") or {}).get("monto"),
        },
        "fecha_creado": orden.get("fecha_creado"),
    }


def _dataclass_to_dict(orden) -> dict:
    """Convierte una dataclass `Orden` a dict (solo campos primitivos)."""
    from dataclasses import asdict

    data = asdict(orden)
    # Eliminar objetos anidados (mesa, precio, usuario) que no son primitivos
    for key in ("mesa", "precio", "usuario"):
        data.pop(key, None)
    return data


async def resolve_id_local(orden: dict) -> Optional[int]:
    """Resuelve el `id_local` al que pertenece la orden a través de su mesa.

    La orden tiene `id_mesafk`; la mesa tiene `id_localfk`. Si no se puede
    resolver (orden sin mesa o mesa sin local), retorna `None`.
    """
    id_mesafk = orden.get("id_mesafk")
    if id_mesafk is None:
        return None

    mesas = await obtenerMesa(filtros={"id": id_mesafk})
    if not mesas:
        return None

    mesa = mesas[0]
    return mesa.get("id_localfk")


async def dispatch_print_job(orden: dict) -> None:
    """Tarea en segundo plano que despacha el trabajo de impresión.

    - Obtiene el payload del ticket formateado a partir de la orden creada.
    - Intenta enviar el payload por el `ConnectionManager` al local de la orden.
    - Incrementa `print_attempts += 1`.
    - Si el local no está conectado (o no se puede resolver), actualiza la
      orden con `last_print_error` y `print_status = FAILED`.
    """
    orden_id = orden.get("id")
    try:
        # 1) Resolver el local asociado a la orden
        id_local = await resolve_id_local(orden)
        if id_local is None:
            await _marcar_error(orden_id, ERROR_SIN_LOCAL)
            return

        # 2) Construir payload del ticket
        payload = build_ticket_payload(orden)

        # 3) Intentar el envío
        enviado = await connection_manager.send_print_job(str(id_local), payload)

        # 4) Incrementar intentos
        attempts = int(orden.get("print_attempts") or 0) + 1
        if enviado:
            await actualizarOrden({
                "print_status": PRINT_STATUS_PENDING,
                "print_attempts": attempts,
            }, orden_id)
        else:
            await _marcar_error(orden_id, ERROR_LOCAL_OFFLINE, attempts=attempts)
    except Exception as exc:
        logger.exception(f"Error en dispatch_print_job para orden {orden_id}: {exc}")
        await _marcar_error(orden_id, f"Error al despachar impresión: {exc}")


async def _marcar_error(
    orden_id: Optional[int],
    error_message: str,
    attempts: Optional[int] = None,
) -> None:
    """Actualiza la orden marcándola como FAILED con el error correspondiente."""
    if orden_id is None:
        logger.error(f"No se pudo actualizar estado de impresión: {error_message}")
        return
    updates = {
        "print_status": PRINT_STATUS_FAILED,
        "last_print_error": error_message,
    }
    if attempts is not None:
        updates["print_attempts"] = attempts
    try:
        await actualizarOrden(updates, orden_id)
    except Exception as exc:
        logger.error(f"No se pudo marcar error en orden {orden_id}: {exc}")


async def process_print_ack(message: dict) -> None:
    """Procesa una confirmación (ACK) de impresión proveniente del cliente.

    El formato esperado del mensaje:
    ```json
    {
      "event": "print_ack",
      "job_id": "uuid-de-la-orden",
      "status": "SUCCESS",  // o "FAILED"
      "error_message": null
    }
    ```
    """
    if message.get("event") != "print_ack":
        return

    job_id = message.get("job_id")
    if job_id is None:
        logger.warning("ACK de impresión sin job_id")
        return

    status = message.get("status", "FAILED")
    error_message = message.get("error_message")

    if status == "SUCCESS":
        updates = {
            "print_status": PRINT_STATUS_PRINTED,
            "printed_at": datetime.now(timezone.utc).isoformat(),
            "last_print_error": None,
        }
        logger.info(f"Impresión confirmada para orden {job_id}")
    else:
        updates = {
            "print_status": PRINT_STATUS_FAILED,
            "printed_at": None,
            "last_print_error": error_message or "Fallo reportado por el cliente",
        }
        logger.warning(f"Impresión fallida para orden {job_id}: {error_message}")

    try:
        await actualizarOrden(updates, job_id)
    except Exception as exc:
        logger.error(f"No se pudo actualizar la orden {job_id} con el ACK: {exc}")
