from typing import Optional, Union

from src.shell.adapters.database.generic_crud import get, insert, update
from src.shell.utils import prepararPayloadDb

from ..models.egreso import Egreso


async def obtenerEgreso(filtros=None, limite=100, offset=0, columnas="*"):
    # Construir las relaciones (joins) necesarias siguiendo el patrón de cliente_repository.py
    
    joins = []

    if "cajas" in columnas.lower():
        joins.append({
            "table": "cajas",
            "foreign_key": "id_cajafk",
            "primary_key": "id",
            "type": "LEFT",
        })

    # Añadir usuarios si no están ya en columnas y se necesita la relación con cajas
    if len(joins) > 0 and ("usuarios" not in columnas.lower() or joins[0]["table"] == "cajas"):
        joins.append({
            "table": "usuarios",
            "foreign_key": "id_usuariofk",
            "primary_key": "cedula",
            "type": "LEFT",
        })

    # Añadir personas si no están ya en columnas y se está incluyendo usuarios/cajas
    if len(joins) >= 2 and ("personas" not in columnas.lower() or joins[1]["table"] == "usuarios"):
        joins.append({
            "table": "personas",
            "foreign_key": "id_personafk",
            "primary_key": "cedula",
            "type": "LEFT",
        })

    # Construir la cadena de columns con las relaciones si es necesario
    if len(joins) > 0:
        columnas_con_joins = f"{columnas}, cajas(id, fecha_creado, fecha_cierre, monto_apertura, monto_cierre, id_usuariofk)"
        
        # Añadir usuarios y personas a la cadena de columns solo si no están en columnas original
        if "usuarios" not in columnas.lower():
            columnas_con_joins += ", usuarios(alias, estado, id_rolfk)"
            
        if len(joins) >= 3 and "personas" not in columnas.lower():
            # Extraer los campos de personas que se necesitan (nombres, apellidos, telefono como en cliente_repository.py)
            columnas_con_joins += ", personas(nombres, apellidos, telefono)"

    return await get(
        'egresos',
        filtros,
        limite,
        offset,
        columns=columnas_con_joins if len(joins) > 0 else columnas,
        joins=joins if len(joins) > 0 and ("cajas" in columnas.lower() or "usuarios" not in columnas.lower()) else None,
    )


async def actualizarEgreso(datos: Union[Egreso, dict], id: Optional[int] = None):
    payload = prepararPayloadDb(datos, exclude_fields=['caja'])

    if id is None:
        return await insert('egresos', payload)
    return await update('egresos', id, payload)
