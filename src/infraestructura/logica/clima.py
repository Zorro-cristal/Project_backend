from src.infraestructura.entidad.clima import PronosticoClimatico

def pronosticoToArray(valores):
    result= []
    for i in range(len(valores['time'])):
        result.append(PronosticoClimatico(
            temperatura_min= valores['temperatura_min'][i],
            temperatura_max= valores['temperatura_max'][i],
            velocidad_viento= valores['velocidad_viento'][i],
            lluvia= valores['lluvia'][i],
            recipitaciones= valores['recipitaciones'][i],
            probabilidad_precipitaciones= valores['probabilidad_precipitaciones'][i],
            fecha= valores['time'][i]
        ))
    
    return result