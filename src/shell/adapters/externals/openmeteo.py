import json
from datetime import datetime

import openmeteo_requests
import os
import requests_cache
from retry_requests import retry

from src.infraestructura.models.clima import Clima

# Setup the Open-Meteo API client with cache and retry on error
cache_path = os.path.join("/tmp", "cache.sqlite")
cache_session = requests_cache.CachedSession(cache_path, expire_after=3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Parámetros por defecto para Open-Meteo
PARAMETROS_CLIMA = [
    "temperature_2m",            # 0
    "relative_humidity_2m",      # 1
    "apparent_temperature",      # 2
    "precipitation_probability", # 3
    "precipitation",             # 4
    "rain",                      # 5
    "showers",                   # 6
    "snowfall",                  # 7
    "weather_code",              # 8
    "cloud_cover",               # 9
    "pressure_msl",              # 10
    "surface_pressure",          # 11
    "wind_speed_10m",            # 12
    "wind_direction_10m",        # 13
    "wind_gusts_10m"             # 14
]

def obtenerInformacionClimatica(latitud, longitud, parametros=None):
    """Obtiene información climática actual de Open-Meteo API
    
    Args:
        latitud: Latitud de la ubicación
        longitud: Longitud de la ubicación
        parametros: Lista de parámetros a solicitar (opcional)
    
    Returns:
        dict: Diccionario con clima, temperatura y humedad listos para Venta
    """
    if parametros is None:
        parametros = PARAMETROS_CLIMA
    
    try:
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", {
            "latitude": latitud,
            "longitude": longitud,
            "current": parametros,
            "timezone": "auto",
            "forecast_days": 1
        })
        
        if responses:
            response = responses[0].Current()
            
            # Crear objeto Clima original
            clima_obj = Clima(
                temperatura=float(response.Variables(0).Value()),
                sensacion_termica=float(response.Variables(2).Value()),
                humedad=float(response.Variables(1).Value()),
                velocidad_viento=float(response.Variables(12).Value()),
                weather_code=int(response.Variables(8).Value()),
                fecha=datetime.fromtimestamp(response.Time()),
                precipitaciones=float(response.Variables(4).Value()),
                lluvia=float(response.Variables(5).Value()),
            )
            
            # Retornar diccionario compatible con modelo Venta
            # clima: weather_code (código del clima)
            # temperatura: temperatura actual en grados Celsius
            # humedad: humedad relativa en porcentaje
            return {
                "clima": clima_obj.weather_code,
                "temperatura": int(clima_obj.temperatura),
                "humedad": int(clima_obj.humedad),
                "velocidad_viento": round(float(clima_obj.velocidad_viento), 2),
                "lluvia": round(float(clima_obj.lluvia), 2),
                "precipitaciones": round(float(clima_obj.precipitaciones), 2),
                "probabilidad_precipitaciones": int(round(float(response.Variables(3).Value()))),
            }
    except Exception as e:
        print(f"[obtenerInformacionClimatica] Error: {str(e)}")
        return None
