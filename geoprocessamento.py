from geopy.distance import distance  

def distancia_km(p1: tuple, p2: tuple) -> float:
    return distance(p1, p2).km

def listar_em_raio(lista_locais: list, origem: tuple, raio_km: float):
    resultado = []
    for loc in lista_locais:
        d = distancia_km(origem, (loc['latitude'], loc['longitude']))
        if d <= raio_km:
            loc_copy = loc.copy()
            loc_copy['distancia_km'] = d
            resultado.append(loc_copy)
    resultado.sort(key=lambda x: x['distancia_km'])
    return resultado