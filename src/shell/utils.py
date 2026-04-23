from dataclasses import asdict, is_dataclass
from typing import Any, Dict, Optional, Union

def prepararPayloadDb(
    data: Union[Any, Dict],
    exclude_fields: Optional[list[str]] = None
) -> Dict:
    """
    Convierte una instancia de dataclass o un diccionario en un diccionario
    apto para operaciones de base de datos.
    Excluye el campo 'id' y cualquier campo especificado en 'exclude_fields'.
    """
    if is_dataclass(data):
        payload = asdict(data)
    else:
        payload = dict(data) # Asegura que sea un dict mutable

    payload.pop("id", None) # El 'id' se maneja por separado (en la URL, etc.)

    if exclude_fields:
        for field in exclude_fields:
            payload.pop(field, None)

    return payload