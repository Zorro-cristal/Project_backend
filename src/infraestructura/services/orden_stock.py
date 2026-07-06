from __future__ import annotations

from typing import Iterable

from .stock_service import obtener_stocks
from ..repositories.stock_repository import actualizarStock
from .detalles_producto_service import obtener_detalles_productos
from .ingrediente_service import obtener_ingredientes


async def _consumir_stock_fifo_por_detalle(
    *,
    id_detalleproductofk: str,
    cantidad_a_consumir: int,
) -> None:
    if cantidad_a_consumir <= 0:
        return

    stocks = await obtener_stocks(
        {
            "id_detalleproductofk": id_detalleproductofk,
            "con_stock": 1,
        }
    )

    if not stocks:
        raise ValueError("No hay stock disponible para el producto solicitado")

    restante = cantidad_a_consumir
    stocks_actualizados: list[dict] = []

    for stock in stocks:
        if restante <= 0:
            break

        cant_mostrador = int(stock.get("cant_mostrador") or 0)
        cant_deposito = int(stock.get("cant_deposito") or 0)

        if cant_mostrador <= 0 and cant_deposito <= 0:
            continue

        consumido_en_mostrador = min(cant_mostrador, restante) if cant_mostrador > 0 else 0

        restante_despues_mostrador = restante - consumido_en_mostrador
        consumido_en_deposito = 0
        if restante_despues_mostrador > 0 and cant_deposito > 0:
            consumido_en_deposito = min(cant_deposito, restante_despues_mostrador)

        consumido_total = consumido_en_mostrador + consumido_en_deposito
        if consumido_total <= 0:
            continue

        restante -= consumido_total

        new_cant_mostrador = cant_mostrador - consumido_en_mostrador
        new_cant_deposito = cant_deposito - consumido_en_deposito
        new_cant_reservado = int(stock.get("cant_reservado") or 0) + consumido_total

        stocks_actualizados.append(
            {
                "id": stock.get("id"),
                "cant_mostrador": new_cant_mostrador,
                "cant_deposito": new_cant_deposito,
                "cant_reservado": new_cant_reservado,
            }
        )

    if restante > 0:
        raise ValueError("Stock insuficiente para la cantidad solicitada")

    for s in stocks_actualizados:
        if s["id"] is None:
            raise ValueError("Stock inválido: no existe id para actualizar")
        await actualizarStock(
            {
                "cant_mostrador": s["cant_mostrador"],
                "cant_deposito": s["cant_deposito"],
                "cant_reservado": s["cant_reservado"],
            },
            s["id"],
        )


async def consumir_stock_para_orden(
    *,
    id_detalleproductofk: str,
    cantidad_a_consumir: int,
) -> None:
    await _consumir_stock_fifo_por_detalle(
        id_detalleproductofk=id_detalleproductofk,
        cantidad_a_consumir=cantidad_a_consumir,
    )


async def consumir_ingredientes_para_producto_comida(
    *,
    id_producto_comida: int,
    cantidad_producto_comida: int,
) -> None:
    """
    Si el producto es comida, consume stock de sus ingredientes.

    - Busca ingredientes por id_producto_finalfk == id_producto_comida
    - Para cada ingrediente, obtiene su detalles_producto (cod_barra) usando id_productofk == id_producto_ingredientefk
    - Consume stock usando ese cod_barra como id_detalleproductofk
    - Cantidad ingrediente a consumir = ingrediente.cantidad * cantidad_producto_comida
    """
    ingredientes = await obtener_ingredientes({"id_producto_finalfk": id_producto_comida})
    if not ingredientes:
        return

    for ing in ingredientes:
        id_producto_ingrediente = ing.get("id_producto_ingredientefk")
        cant_ing = ing.get("cantidad") or 0

        if id_producto_ingrediente is None or cant_ing <= 0:
            continue

        # Obtener el detalle del producto ingrediente para tener cod_barra (id_detalleproductofk)
        detalles_ing = await obtener_detalles_productos(
            filtros={"id_productofk": int(id_producto_ingrediente)},
            include_producto=False,
        )

        if not detalles_ing:
            raise ValueError(f"No se encontraron detalles_producto para ingrediente productofk={id_producto_ingrediente}")

        # En la práctica deberían existir 1 detalle para el ingrediente, pero tomamos el primero con cod_barra
        detalle_cod_barra = next((d.get("cod_barra") for d in detalles_ing if d.get("cod_barra") is not None), None)
        if detalle_cod_barra is None:
            raise ValueError(f"No existe cod_barra en detalles_producto para ingrediente productofk={id_producto_ingrediente}")

        cantidad_a_consumir = int(cant_ing) * int(cantidad_producto_comida)

        await _consumir_stock_fifo_por_detalle(
            id_detalleproductofk=str(detalle_cod_barra),
            cantidad_a_consumir=cantidad_a_consumir,
        )


async def _desreservar_stock_fifo_por_detalle(
    *,
    id_detalleproductofk: str,
    cantidad_a_liberar: int,
) -> None:
    """
    Desreserva (libera) stock consumido por una venta.

    Regla requerida:
    - Solo disminuir stocks.cant_reservado
    - No modificar cant_mostrador ni cant_deposito

    FIFO por fecha_vencimiento (con el mismo ordering de obtener_stocks).
    """
    if cantidad_a_liberar <= 0:
        return

    stocks = await obtener_stocks(
        {
            "id_detalleproductofk": id_detalleproductofk,
            # No usamos con_stock; queremos únicamente reservas
            # Usamos cant_reservado > 0 directamente con Supabase.
        },
        columnas="*",
    )

    # Filtrar en memoria porque obtener_stocks/con_stock no cubre este caso
    # (y generic_crud no ofrece OR/gt robusto sobre cant_reservado).
    stocks = [s for s in (stocks or []) if int(s.get("cant_reservado") or 0) > 0]

    if not stocks:
        raise ValueError("No hay stock reservado disponible para el producto solicitado")

    restante = int(cantidad_a_liberar)
    stocks_actualizados: list[dict] = []

    for stock in stocks:
        if restante <= 0:
            break

        cant_reservado = int(stock.get("cant_reservado") or 0)
        if cant_reservado <= 0:
            continue

        liberado = min(cant_reservado, restante)
        if liberado <= 0:
            continue

        restante -= liberado
        new_cant_reservado = cant_reservado - liberado

        stocks_actualizados.append(
            {
                "id": stock.get("id"),
                "cant_reservado": new_cant_reservado,
            }
        )

    if restante > 0:
        raise ValueError("Stock insuficiente reservado para liberar la cantidad solicitada")

    for s in stocks_actualizados:
        if s["id"] is None:
            raise ValueError("Stock inválido: no existe id para actualizar")
        await actualizarStock(
            {
                "cant_reservado": s["cant_reservado"],
            },
            s["id"],
        )


async def desreservar_stock_para_venta(
    *,
    id_detalleproductofk: str,
    cantidad_a_liberar: int,
) -> None:
    await _desreservar_stock_fifo_por_detalle(
        id_detalleproductofk=id_detalleproductofk,
        cantidad_a_liberar=cantidad_a_liberar,
    )
