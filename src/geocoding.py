import requests


def georreferenciar(direccion):
    print("Georreferenciando dirección:", direccion)

    # URL base para la API de geocodificación de Google Maps
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    # Parámetros de la solicitud
    params = {
        'address': direccion,
        'key': "AIzaSyAKqyYtw4VH_3LEo0_c1gSv2yfS2PsFxPQ"
    }
    
    # Realizar la solicitud GET
    respuesta = requests.get(url, params=params)

    # Verificar si la solicitud fue exitosa
    if respuesta.status_code == 200:
        datos = respuesta.json()
        print(datos['results'][0].keys())
        
        # Si la respuesta tiene resultados, obtener la latitud y longitud
        if datos['status'] == 'OK':
            latitud = datos['results'][0]['geometry']['location']['lat']
            longitud = datos['results'][0]['geometry']['location']['lng']
            tipo = datos['results'][0]['geometry']['location_type']
            partial = datos['results'][0]['partial_match'] if 'partial_match' in datos['results'][0] else False
            return latitud, longitud, tipo, partial
        else:
            return None
    else:
        return None