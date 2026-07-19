from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel
from pydantic.config import ConfigDict

T = TypeVar("T")


class ExtraIgnoredModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class MessageEnvelope(ExtraIgnoredModel, Generic[T]):
    message: T


# ----------------------------
# Full models (for specific resources)
# ----------------------------

class RolFull(ExtraIgnoredModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    estado: Optional[int] = None


class LocalFull(ExtraIgnoredModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    estado: Optional[int] = None
    cod_num: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class CategoriaFull(ExtraIgnoredModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    estado: Optional[int] = None
    descripcion: Optional[str] = None


class CajaFull(ExtraIgnoredModel):
    id: Optional[int] = None
    monto_apertura: Optional[float] = None
    fecha_creado: Optional[datetime] = None
    monto_cierre: Optional[float] = None
    fecha_cierre: Optional[datetime] = None
    id_usuariofk: Optional[int] = None
    usuario: Optional[Any] = None


# ----------------------------
# FK-only models (for general GET endpoints)
# ----------------------------

class UsuarioFKOnly(ExtraIgnoredModel):
    alias: Optional[str] = None
    id_rolfk: Optional[int] = None
    id_personafk: Optional[int] = None


class UsuarioWithPersona(ExtraIgnoredModel):
    alias: Optional[str] = None
    id_rolfk: Optional[int] = None
    id_personafk: Optional[int] = None
    # attach_related en usuario_service agrega el objeto bajo la clave "persona"
    persona: Optional[Any] = None


class ProductoFKOnly(ExtraIgnoredModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[int] = None
    impuesto: Optional[int] = None
    pesable: Optional[bool] = None
    perecedero: Optional[bool] = None
    costeo: Optional[int] = None
    unidad_medida: Optional[str] = None
    es_ingrediente: Optional[bool] = None
    es_comida: Optional[bool] = None

    # FK-only (omit nested objects like categoria)
    id_categoriafk: Optional[int] = None
    id_marcafk: Optional[int] = None


class ProductoWithDetallesProducto(ExtraIgnoredModel):
    id: Optional[int] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    estado: Optional[int] = None
    impuesto: Optional[int] = None
    pesable: Optional[bool] = None
    perecedero: Optional[bool] = None
    costeo: Optional[int] = None
    unidad_medida: Optional[str] = None
    es_ingrediente: Optional[bool] = None
    es_comida: Optional[bool] = None

    # FK-only
    id_categoriafk: Optional[int] = None
    id_marcafk: Optional[int] = None

    # Se incluye cuando include=detallesProducto
    detalles_producto: Optional[Any] = None


class VentaFKOnly(ExtraIgnoredModel):
    id: Optional[int] = None
    fecha: Optional[datetime] = None
    estado: Optional[int] = None
    evento_festivo: Optional[bool] = None
    tipo_credito: Optional[int] = None

    # FK-only (omit nested objects like local/caja/rol/categoria)
    id_clientefk: Optional[int] = None
    id_localfk: Optional[int] = None
    id_cajafk: Optional[int] = None
    id_vendedorfk: Optional[int] = None


# ----------------------------
# Full models for specific resources in list endpoints
# ----------------------------

class RolListResponse(MessageEnvelope[List[RolFull]]):
    pass


class LocalListResponse(MessageEnvelope[List[LocalFull]]):
    pass


class CategoriaListResponse(MessageEnvelope[List[CategoriaFull]]):
    pass


class CajaListResponse(MessageEnvelope[List[CajaFull]]):
    pass


# ----------------------------
# FK-only list/obj response models (general endpoints)
# ----------------------------

class UsuarioListResponse(MessageEnvelope[List[UsuarioWithPersona]]):
    pass


class ProductoListResponse(MessageEnvelope[List[ProductoWithDetallesProducto]]):
    pass


class VentaListResponse(MessageEnvelope[List[VentaFKOnly]]):
    pass
