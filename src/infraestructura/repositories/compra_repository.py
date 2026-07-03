from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.compra import Compra


async def obtenerCompra(filtros=None, limite=100, offset=0, columnas="*", joins=None):
    return await get('compras', filtros, limite, offset, columns=columnas, joins=joins)


async def actualizarCompra(datos: Union[Compra, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['local', 'cliente', 'proveedor', 'detalles', 'usuario'])

    # DEBUG: verificar que monto_entrega viaje correctamente a Supabase
    # (dejar este print hasta confirmar el problema, luego se elimina)
    print("[DEBUG] actualizarCompra payload compras:", payload)

    if id is None:
        return await insert('compras', payload)
    return await update('compras', id, payload, key='id_compra')
