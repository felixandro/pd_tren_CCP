import geopandas as gpd
import networkx as nx
import requests
from shapely.geometry import Point
import streamlit as st

def load_gdf(gdf_path):
    gdf = gpd.read_file(gdf_path)
    return gdf

def build_network(edges_gdf):
    network = nx.DiGraph() #Grafo Dirigido Vacío
    for _, row in edges_gdf.iterrows():
        start_node = int(row["NODOA"])
        end_node = int(row["NODOB"])
        weight = float((row["LENGTH"]/1000) / 40 * 60) # Convertir longitud a tiempo asumiendo velocidad de 40 km/h
        network.add_edge(start_node, end_node, weight = weight)
    return network

def get_walk_route(punto_origen, punto_destino):
    """
    Calcula una ruta mínima caminando entre dos puntos usando la API de Directions de Mapbox.

    Parámetros:
    - punto_origen (shapely.geometry.Point): punto de partida (en EPSG:4326)
    - punto_destino (shapely.geometry.Point): punto de llegada (en EPSG:4326)
    - token (str): token de acceso a Mapbox

    Retorna:
    - GeoDataFrame con una línea que representa la ruta, y atributos como distancia y duración.
    """
    lon1, lat1 = punto_origen.x, punto_origen.y
    lon2, lat2 = punto_destino.x, punto_destino.y

    url = f"https://api.mapbox.com/directions/v5/mapbox/walking/{lon1},{lat1};{lon2},{lat2}"
    params = {
        "geometries": "geojson",
        "overview": "full",
        "access_token": st.secrets["OSM_TOKEN"]
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        route = data["routes"][0]
        duration_min = route["duration"] / 60

        return duration_min

    except Exception as e:
        print("Error al calcular ruta:", e)
        return 10.0
    
def generate_connectors(network, point_lat, point_lon, nodos_gdf):
    if nodos_gdf.empty:
        return nodos_gdf.copy(), 0

    point_gdf = gpd.GeoDataFrame(
        {'point_id': [1]},
        geometry=[Point(point_lon, point_lat)],
        crs='EPSG:4326'
    )

    point_in_nodes_crs = point_gdf.to_crs(nodos_gdf.crs).geometry.iloc[0]

    radius_m = 800
    nodos_with_distance = nodos_gdf.copy()
    nodos_with_distance['distance_m'] = nodos_with_distance.geometry.distance(point_in_nodes_crs)
    contained_nodes = nodos_with_distance.loc[(nodos_with_distance['distance_m'] <= radius_m) & (nodos_with_distance['CONEC'] == 1)].copy()

    while len(contained_nodes) < 2:
        radius_m += 100
        contained_nodes = nodos_with_distance.loc[(nodos_with_distance['distance_m'] <= radius_m) & (nodos_with_distance['CONEC'] == 1)].copy()

    for _, row in contained_nodes.to_crs("EPSG:4326").iterrows():
        od_point = point_gdf.geometry.iloc[0]        
        nodo_id = int(row["ID"])
        nodo_point = row.geometry
        walk_duration = get_walk_route(od_point, nodo_point)
        network.add_edge(0, nodo_id, weight=walk_duration)

    return network

def save_proy_nivels(lat, lon):

    # Cargar Grafo de Biotren
    nodos_gdf = load_gdf("data/redes_proyectos/nodos_proyectos.shp")
    edges_gdf = load_gdf("data/redes_proyectos/arcos_proyectos.shp")

    # Generar Grafo de arcos de biotren
    network = build_network(edges_gdf)

    # Generar Conectores
    network = generate_connectors(network, lat, lon, nodos_gdf)

    # Calcular Ruta Mínima
    min_route = nx.shortest_path(network, source=0, target=990000, weight='weight')
    print("Ruta mínima (incluyendo conectores):", min_route)
    walking_time = sum(network[u][v]['weight'] for u, v in zip([min_route[0]], [min_route[1]]))
    metro_time = sum(network[u][v]['weight'] for u, v in zip(min_route[1:-1], min_route[2:]))

    # Retornar Diccionario de tiempos 
    proy_nivels_dict = {'tv_wlk': round(walking_time, 2), #min
                        'tv_metro': round(metro_time, 2), #min
                        'tv_total': round(walking_time + metro_time, 2) #mintime + metro_time, 2) #min
    }

    st.session_state["responses"]["proy_nivels"] = proy_nivels_dict