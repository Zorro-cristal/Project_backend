from src.infraestructura.services.compra_service import \
    obtener_compra_solo as obtener_compra_solo_service
from src.infraestructura.services.compra_service import \
    obtener_compras as obtener_compras_service
from src.infraestructura.services.detalle_compra_service import \
    obtener_detalle_compras
from src.infraestructura.services.local_service import obtener_locales
from src.infraestructura.services.proveedor_service import obtener_proveedores
from src.shell.utils import attach_grouped, attach_related


async def obtener_compras(filtros: dict = None):
    return await obtener_compras_service(filtros)


async def obtener_compra_solo(id: int):
    return await obtener_compra_solo_service(id)


async def obtener_compra_con_detalles(id: int, solo_detalles: bool = False):
    compra = await obtener_compra_solo_service(id)
    if not compra:
        return compra

    compra = await attach_related_data([compra])
    compra = compra[0] if compra else None

    if solo_detalles:
        return compra.get('detalles', []) if compra else []

    return compra



    compras = await attach_related(compras, 'id_clientefk', obtener_clientes, 'id', 'id', 'cliente')
    compras = await attach_related(compras, 'id_localfk', obtener_locales, 'id', 'id', 'local')
    compras = await attach_related(compras, 'id_proveedorfk', obtener_proveedores, 'id', 'id', 'proveedor')
    compras = await attach_grouped(compras, 'id', obtener_detalle_compras, 'id_comprafk', 'id_comprafk', 'detalles')
    return compras
