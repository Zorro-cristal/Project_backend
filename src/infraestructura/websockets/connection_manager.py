import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Administra las conexiones WebSocket activas agrupadas por `id_local`.

    Mantiene un diccionario en memoria `active_connections` donde cada clave
    es un `id_local` (str) y el valor es la lista de WebSocket conectados
    para ese local. Un mismo local puede tener múltiples conexiones activas
    (ej. varios dispositivos): al enviar un trabajo de impresión se difunde
    a todas las conexiones de ese local.
    """

    def __init__(self) -> None:
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id_local: str) -> None:
        """Acepta y registra una conexión WebSocket para el `id_local` dado."""
        await websocket.accept()
        key = str(id_local)
        self.active_connections.setdefault(key, []).append(websocket)
        logger.info(f"WebSocket conectado para id_local={key}. "
                    f"Conexiones activas totales: {self.total_connections()}")

    async def disconnect(self, id_local: str) -> None:
        """Remueve todas las conexiones registradas del `id_local` dado."""
        key = str(id_local)
        connections = self.active_connections.pop(key, [])
        for ws in connections:
            try:
                await ws.close()
            except Exception as exc:  # pragma: no cover - cierre defensivo
                logger.debug(f"Error cerrando WebSocket de id_local={key}: {exc}")
        logger.info(f"WebSocket desconectado para id_local={key}. "
                    f"Conexiones restantes: {self.total_connections()}")

    async def _remove_connection(self, websocket: WebSocket, id_local: str) -> None:
        """Remueve una conexión puntual de la lista del local (sin cerrarla)."""
        key = str(id_local)
        connections = self.active_connections.get(key, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(key, None)

    async def send_print_job(self, id_local: str, payload: dict) -> bool:
        """Envía un trabajo de impresión a todas las conexiones del local.

        Retorna `True` si el payload se envió a al menos una conexión activa;
        `False` si el local no tiene conexiones activas.
        """
        key = str(id_local)
        connections = self.active_connections.get(key, [])
        if not connections:
            logger.warning(f"Local {key} sin conexión activa: no se pudo enviar "
                           f"el trabajo de impresión.")
            return False

        sent = False
        for ws in list(connections):
            try:
                await ws.send_json(payload)
                sent = True
            except Exception as exc:
                logger.warning(f"Error enviando trabajo de impresión a "
                               f"id_local={key}: {exc}")
                # Eliminar la conexión rota
                await self._remove_connection(ws, key)
        return sent

    def is_connected(self, id_local: str) -> bool:
        """Indica si existe al menos una conexión activa para el local."""
        return bool(self.active_connections.get(str(id_local)))

    def total_connections(self) -> int:
        """Retorna el total de conexiones activas en todos los locales."""
        return sum(len(ws_list) for ws_list in self.active_connections.values())


# Instancia singleton global reutilizada en toda la aplicación
connection_manager = ConnectionManager()
