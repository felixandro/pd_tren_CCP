import requests

def get_google_directions(origin, destination, mode, api_key):
    """
    origin, destination: (lat, lng) tuples
    mode: 'driving' or 'transit'
    Devuelve diccionario con tiempos (segundos) y distancias (metros).
    - Para 'driving': una sola etapa (drive).
    - Para 'transit': access, travel, egress.
    """
    if mode not in ('transit', 'bus', 'rail'):
        raise ValueError("mode must be 'transit', 'bus' or 'rail'")

    data = single_request(origin, destination, mode, api_key)

    status = data.get('status')
    if status != 'OK':
        return {'error': status, 'details': data.get('error_message')}
    
    # Procesar la respuesta

    if mode == 'transit' or mode == 'bus':
        route = data['routes'][0]
        leg = route['legs'][0]
            
    elif mode == "rail":
        best_route_rail = select_route_min_walking_with_heavy_rail(data)

        if best_route_rail is None:
            return {'error': 'No valid heavy rail route found'}
        
        leg = best_route_rail['legs'][0]

    return summarize_transit_leg_times(leg)

def single_request(origin, destination, mode, api_key):
    
    url = 'https://maps.googleapis.com/maps/api/directions/json'

    params = {
            'origin': f"{origin[0]},{origin[1]}",
            'destination': f"{destination[0]},{destination[1]}",
            'key': api_key,
            'language': 'es'
            
        }

    if mode == 'transit':
        params['mode'] = mode

    else:
        params['mode'] = 'transit'
        params['transit_mode'] = mode

        if mode == "rail":
            params["transit_routing_preference"] = "less_walking"
            params["alternatives"] = "true"

    # 20/05/2026 08:00 AM (America/Santiago) en formato Unix epoch.
    params['departure_time'] = 1779278400

    resp = requests.get(url, params=params)
    data = resp.json()

    return data

def route_has_heavy_rail(route):
    """
    Retorna True si la ruta contiene al menos una etapa TRANSIT con vehiculo HEAVY_RAIL.
    """
    legs = route.get('legs', [])
    if not legs:
        return False

    for step in legs[0].get('steps', []):
        if step.get('travel_mode', '').upper() != 'TRANSIT':
            continue

        vehicle_type = (
            step.get('transit_details', {})
            .get('line', {})
            .get('vehicle', {})
            .get('type', '')
            .upper()
        )
        if vehicle_type == 'HEAVY_RAIL':
            return True

    return False

def walking_distance_in_route(route):
    """
    Suma la caminata total de una ruta en metros.
    """
    legs = route.get('legs', [])
    if not legs:
        return float('inf')

    return sum(
        step.get('distance', {}).get('value', 0)
        for step in legs[0].get('steps', [])
        if step.get('travel_mode', '').upper() == 'WALKING'
    )

def select_route_min_walking_with_heavy_rail(data):
    """
    Desde la respuesta completa (data) de Directions API, retorna una ruta que:
    - Incluya al menos una etapa HEAVY_RAIL.
    - Tenga la menor caminata total entre las que cumplen la condicion.

    Si no hay rutas validas, retorna None.
    """
    routes = data.get('routes', [])
    heavy_rail_routes = [route for route in routes if route_has_heavy_rail(route)]

    if not heavy_rail_routes:
        return None

    return min(
        heavy_rail_routes,
        key=lambda route: (
            walking_distance_in_route(route),
            route.get('legs', [{}])[0].get('duration', {}).get('value', float('inf')),
        ),
    )

def summarize_transit_leg_times(leg):
    """
    Procesa un transit leg y retorna un diccionario con:
    - tiempos totales (minutos) en etapas WALKING, BUS y HEAVY_RAIL
    - cantidad de etapas BUS
    """
    summary = {
        't_walking_min': 0.0,
        't_bus_min': 0.0,
        't_heavy_rail_min': 0.0,
        'n_bus_stages': 0,
    }

    for step in leg.get('steps', []):
        duration_min = step.get('duration', {}).get('value', 0) / 60
        travel_mode = step.get('travel_mode', '').upper()

        if travel_mode == 'WALKING':
            summary['t_walking_min'] += duration_min
            continue

        if travel_mode != 'TRANSIT':
            continue

        vehicle_type = (
            step.get('transit_details', {})
            .get('line', {})
            .get('vehicle', {})
            .get('type', '')
            .upper()
        )

        if vehicle_type == 'BUS':
            summary['t_bus_min'] += duration_min
            summary['n_bus_stages'] += 1
        elif vehicle_type == 'HEAVY_RAIL':
            summary['t_heavy_rail_min'] += duration_min

    summary['t_walking_min'] = round(summary['t_walking_min'], 2)
    summary['t_bus_min'] = round(summary['t_bus_min'], 2)
    summary['t_heavy_rail_min'] = round(summary['t_heavy_rail_min'], 2)

    return summary


# SIN USO
def process_driving_leg(leg):
    distance = leg.get('distance', {}).get('value', 0)
    duration = leg.get('duration', {}).get('value', 0)
    return {
        'dv_liv': round(distance/1000,3), #km
        'tv_liv': round(duration/60,2), #min
    }

# SIN USO
def process_transit_leg(leg):
    steps = leg.get('steps', [])
    transit_indices = [i for i, s in enumerate(steps) if s.get('travel_mode', '').upper() == 'TRANSIT']
    if not transit_indices:
        walk_distance = sum(s.get('distance', {}).get('value', 0) for s in steps)
        walk_duration = sum(s.get('duration', {}).get('value', 0) for s in steps)
        return {
            'dca_txb': round(0.05* walk_distance/1000,3), #km
            'tca_txb': round(0.05* walk_distance/1000,3) / 5 * 60, #min
            'dv_txb' : round(0.90* walk_distance/1000,3), #km
            'tv_txb' : round(0.90* walk_distance/1000,3) / 20 * 60, #min
            'dce_txb': round(0.05* walk_distance/1000,3), #km
            'tce_txb': round(0.05* walk_distance/1000,3) / 5 * 60} #min
     
    first_transit_idx = transit_indices[0]
    last_transit_idx = transit_indices[-1]
    access_steps = steps[:first_transit_idx]
    travel_steps = steps[first_transit_idx:last_transit_idx + 1]
    egress_steps = steps[last_transit_idx + 1:]

    access_distance = sum(s.get('distance', {}).get('value', 0) for s in access_steps)
    access_duration = sum(s.get('duration', {}).get('value', 0) for s in access_steps)
    access_travel_mode = [s.get('travel_mode', '').upper() for s in access_steps]
    travel_distance = sum(s.get('distance', {}).get('value', 0) for s in travel_steps)
    travel_duration = sum(s.get('duration', {}).get('value', 0) for s in travel_steps)
    travel_travel_mode = [s.get('travel_mode', '').upper() for s in travel_steps]
    egress_distance = sum(s.get('distance', {}).get('value', 0) for s in egress_steps)
    egress_duration = sum(s.get('duration', {}).get('value', 0) for s in egress_steps)
    egress_travel_mode = [s.get('travel_mode', '').upper() for s in egress_steps]

    print("Access travel modes:", access_travel_mode)
    print("Travel travel modes:", travel_travel_mode)
    print("Egress travel modes:", egress_travel_mode)

    assert all(mode == 'WALKING' for mode in access_travel_mode), "Access segment contains non-walking modes"
    assert all(mode == 'TRANSIT' for mode in travel_travel_mode), "Travel segment contains non-transit modes"
    assert all(mode == 'WALKING' for mode in egress_travel_mode), "Egress segment contains non-walking modes"

    return {
        'dca_txb': round(access_distance/1000,3), #km
        'tca_txb': round(access_duration/60,2), #min
        'dv_txb' : round(travel_distance/1000,3), #km
        'tv_txb' : round(travel_duration/60,2), #min
        'dce_txb': round(egress_distance/1000,3), #km
        'tce_txb': round(egress_duration/60,2)} #min

# SIN USO
def process_rail_leg(leg):
    """
    Convierte un leg de Google Directions en una lista de etapas.
    Cada etapa se representa como una tupla: (modo, tiempo_min, distancia_km).
    """
    steps = leg.get('steps', [])
    stages = []

    for step in steps:
        travel_mode = step.get('travel_mode', '').upper()
        duration_min = round(step.get('duration', {}).get('value', 0) / 60, 2)
        distance_km = round(step.get('distance', {}).get('value', 0) / 1000, 3)

        if travel_mode == 'TRANSIT':
            vehicle_type = (
                step.get('transit_details', {})
                .get('line', {})
                .get('vehicle', {})
                .get('type', 'TRANSIT')
                .upper()
            )
            mode = vehicle_type
        else:
            mode = travel_mode

        stages.append((mode, duration_min, distance_km))

    return stages