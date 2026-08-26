import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ..services.print_service import (build_ticket_payload, dispatch_print_job,
                                      get_pending_print_orders,
                                      process_print_ack)
from ..websockets.connection_manager import connection_manager
from .schemas.printer_schemas import PrintAck

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/printer/pending/{id_local}")
async def pending_print_orders(id_local: str):
    """Lista las órdenes pendientes de impresión de un local."""
    orders = await get_pending_print_orders(id_local)
    return {
        "id_local": str(id_local),
        "count": len(orders),
        "orders": [
            {
                **order,
                "print_job": build_ticket_payload(order),
            }
            for order in orders
        ],
    }


@router.post("/printer/pending/{id_local}/{order_id}/retry")
async def retry_pending_print(id_local: str, order_id: int):
    """Reenvía una orden pendiente al WebSocket del local."""
    orders = await get_pending_print_orders(id_local)
    order = next((item for item in orders if item.get("id") == order_id), None)
    if order is None:
        return {
            "id_local": str(id_local),
            "order_id": order_id,
            "sent": False,
            "message": "Orden pendiente no encontrada para este local",
        }

    await dispatch_print_job(order)
    return {
        "id_local": str(id_local),
        "order_id": order_id,
        "sent": connection_manager.is_connected(id_local),
        "message": "Orden reenviada al WebSocket",
    }


@router.get("/printer/status/{id_local}")
async def printer_status(id_local: str):
    """Devuelve si existe una aplicación de impresión conectada al local."""
    connections = connection_manager.active_connections.get(str(id_local), [])
    return {
        "id_local": str(id_local),
        "connected": bool(connections),
        "active_connections": len(connections),
        "message": (
            "Aplicación de impresión conectada"
            if connections
            else "No hay aplicación de impresión conectada"
        ),
        "limitation": (
            "Este endpoint confirma la conexión WebSocket con el backend, "
            "pero no verifica que la impresora física esté encendida o disponible."
        ),
    }


@router.websocket("/ws/printer/{id_local}")
async def printer_websocket_endpoint(websocket: WebSocket, id_local: str):
    """Endpoint WebSocket para impresión remota por local.

    - Acepta la conexión y la registra en el `ConnectionManager` bajo `id_local`.
    - Escucha mensajes entrantes del cliente con el evento `print_ack` para
      confirmar el resultado de la impresión.
    """
    await connection_manager.connect(websocket, id_local)
    logger.info(f"Conexión WebSocket establecida para local {id_local}")
    try:
        while True:
            # Espera el siguiente mensaje JSON del cliente
            raw_message = await websocket.receive_text()
            try:
                import json

                data = json.loads(raw_message)
            except json.JSONDecodeError:
                logger.warning(f"Mensaje no JSON recibido de local {id_local}: "
                               f"{raw_message[:200]}")
                continue

            # Procesar confirmaciones de impresión (ACK)
            if isinstance(data, dict) and data.get("event") == "print_ack":
                try:
                    ack = PrintAck(**data)
                    await process_print_ack(ack.model_dump())
                except ValidationError as exc:
                    logger.warning(f"ACK de impresión inválido de local "
                                   f"{id_local}: {exc.errors()}")
            elif isinstance(data, dict) and data.get("event") == "get_pending_prints":
                orders = await get_pending_print_orders(id_local)
                await websocket.send_json({
                    "event": "pending_prints",
                    "id_local": str(id_local),
                    "count": len(orders),
                    "orders": [
                        {
                            **order,
                            "print_job": build_ticket_payload(order),
                        }
                        for order in orders
                    ],
                })
            else:
                logger.debug(f"Mensaje recibido de local {id_local}: {data}")
    except WebSocketDisconnect:
        logger.info(f"Cliente {id_local} desconectado del WebSocket")
    except Exception as exc:
        logger.exception(f"Error en WebSocket de local {id_local}: {exc}")
    finally:
        await connection_manager.disconnect(id_local)
