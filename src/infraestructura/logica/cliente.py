from src.infraestructura.database.cliente import actualizarCliente, obtenerCliente
from src.infraestructura.entidad.cliente import Cliente


def build_cliente_entity(payload: dict) -> Cliente:
    valid_fields = {key: value for key, value in payload.items() if key in Cliente.__annotations__}
    return Cliente(**valid_fields)


async def obtener_clientes(filtros: dict= None, columnas: str = '*'):
    return await obtenerCliente(filtros=filtros, columnas=columnas)


async def crear_cliente(payload: dict):
    cliente = build_cliente_entity(payload)
    return await actualizarCliente(cliente)


async def actualizar_cliente(id: int, payload: dict):
    if not payload:
        raise ValueError('No hay campos para actualizar')
    return await actualizarCliente(payload, id)
