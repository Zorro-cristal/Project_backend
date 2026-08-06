import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from ..services.print_service import process_print_ack
from ..websockets.connection_manager import connection_manager
from .schemas.printer_schemas import PrintAck

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/printer/{id_local}")
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
            else:
                logger.debug(f"Mensaje recibido de local {id_local}: {data}")
    except WebSocketDisconnect:
        logger.info(f"Cliente {id_local} desconectado del WebSocket")
    except Exception as exc:
        logger.exception(f"Error en WebSocket de local {id_local}: {exc}")
    finally:
        await connection_manager.disconnect(id_local)
