import streamlit as st
from src.directions import get_google_directions

def get_origin():
    lat = st.session_state["responses"]["od_screen"].get("Origen_latitude", None)
    lon = st.session_state["responses"]["od_screen"].get("Origen_longitude", None)
    if lat is not None and lon is not None:
        return (lat, lon)
    else:
        return None

def get_destination():
    lat = st.session_state["responses"]["od_screen"].get("Destino_latitude", None)
    lon = st.session_state["responses"]["od_screen"].get("Destino_longitude", None)
    if lat is not None and lon is not None:
        return (lat, lon)
    else:
        return None

def sumar_nivels_dict(dict1, dict2):
    """
    Suma los tiempos y distancias de dos diccionarios de niveles de servicio.
    Si una clave no está presente en alguno de los diccionarios, se asume valor 0 para esa clave.
    """
    result = {}
    for key in set(dict1.keys()).union(set(dict2.keys())):
        result[key] = dict1.get(key, 0) + dict2.get(key, 0)
    return result

def save_api_nivels(api_key, origen_zona, destino_zona, pc):
    if "api_nivels" not in st.session_state["responses"]:

        origen = get_origin()
        destino = get_destination()
                
        if pc == "Estación Concepción BT":

            estacion_ccp = (-36.83042001186013, -73.0610319325143)

            if origen_zona == "CCP" and destino_zona != "CCP":
                # Etapa Origen a Estación Concepción BT
                comple_nivels_dict = get_google_directions(origen, estacion_ccp, 'transit', api_key)

                # Etapa Estación Concepción BT a Destino (RAIL)
                rail_nivels_dict = get_google_directions(estacion_ccp, destino, 'rail', api_key)
                
                
            elif origen_zona != "CCP" and destino_zona == "CCP":
                # Etapa Origen a Estación Concepción BT (RAIL)
                rail_nivels_dict = get_google_directions(origen, estacion_ccp, 'rail', api_key)

                # Etapa Estación Concepción BT a Destino
                comple_nivels_dict = get_google_directions(estacion_ccp, destino, 'transit', api_key)
                
            else:
                st.error("Error: Origen y Destino no válidos para PC Estación Concepción BT")
                return
            
            print("Nivels etapa Completa (Origen-CCP o CCP-Destino):", comple_nivels_dict)
            print("Nivels etapa Rail (Origen-CCP o CCP-Destino):", rail_nivels_dict)
            
            api_nivels_dict = sumar_nivels_dict(comple_nivels_dict, rail_nivels_dict)
            
            st.session_state["responses"]["rail_api_nivels"] = rail_nivels_dict
            st.session_state["responses"]["comple_api_nivels"] = comple_nivels_dict
            st.session_state["responses"]["api_nivels"] = api_nivels_dict