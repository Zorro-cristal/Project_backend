import json
from datetime import datetime

import openmeteo_requests
import requests_cache
from retry_requests import retry

from src.infraestructura.entidad.clima import Clima

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def obtenerInformacionClimatica(latitud, longitud, parametros):
    """Obtiene información climática actual de Open-Meteo API"""
    try:
        responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", {
            "latitude": latitud,
            "longitude": longitud,
            "current": parametros,
            "timezone": "auto",
            "forecast_days": 1
        })
        
        # Convertir la primera respuesta a diccionario JSON-serializable
        if responses:
            response = responses[0].Current()
            response= Clima(
                temperatura= float(response.Variables(0).Value()),
                sensacion_termica= float(response.Variables(2).Value()),
                humedad= float(response.Variables(1).Value()),
                velocidad_viento= float(response.Variables(11).Value()),
                weather_code= int(response.Variables(7).Value()),
                fecha= datetime.fromtimestamp(response.Time()),
                precipitaciones= float(response.Variables(5).Value()),
                lluvia= float(response.Variables(4).Value()),
            )
            return response
    except Exception as e:
        return {"error": str(e)}