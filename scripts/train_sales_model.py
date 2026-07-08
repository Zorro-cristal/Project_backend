from __future__ import annotations

import argparse

from src.infraestructura.services.prediccion_ventas_service import train_and_save_sales_forecast_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Entrena el modelo de predicción de ventas y lo guarda localmente")
    parser.add_argument("--limite", type=int, default=None, help="Cantidad máxima de días de historial a usar")
    args = parser.parse_args()

    result = train_and_save_sales_forecast_model(limite=args.limite)
    print(result)


if __name__ == "__main__":
    main()
