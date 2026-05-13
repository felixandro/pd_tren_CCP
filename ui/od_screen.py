import streamlit as st
import pandas as pd
import time
from streamlit_geolocation import streamlit_geolocation
import folium
from streamlit_folium import st_folium

from src.geocoding import georreferenciar

def get_surveyor_location():

    st.subheader("Ubicación del Encuestador")

    location = streamlit_geolocation()

    st.divider()

    if location["latitude"] and location["longitude"]:
        surveyor_location = {"surveyor_lat": location["latitude"], 
                             "surveyor_lon": location["longitude"],
                             "surveyor_acc": location["accuracy"]}
        return surveyor_location
    
    else:
        empty_surveyor_location = {"surveyor_lat": "", 
                                   "surveyor_lon": "",
                                   "surveyor_acc": ""}
        return empty_surveyor_location

#--------------------------------------------------
# Helper Functions
#--------------------------------------------------

def all_responded(responses_dict):
    """Verifica que todas las preguntas hayan sido contestadas."""
    for _, value in responses_dict.items():
        if value == "":
            return False
    return True

#--------------------------------------------------
# Location Question Widgets Generation
#--------------------------------------------------

def selectbox_question(label: str, options: list, key: str):
    selectbox = st.selectbox(
        label=label,
        options=[""] + options,
        key=key
    )
    return selectbox

def generate_location_question_widget(od):

    st.subheader(f"{od} del viaje")

    responses_dict = {f"{od}": ""}

    location_type = selectbox_question(
        label="Tipo de ubicación",
        options=["Dirección","Intersección","Hito"],
        key=f"{od}_location_type_selectbox"
    )

    if location_type == "Dirección":
        responses_dict = direction_input_question(od)

    elif location_type == "Intersección":
        responses_dict = intersection_input_question(od)

    elif location_type == "Hito":
        responses_dict = landmark_input_question(od)

    adress = responses_dict.get(f"{od}", "")

    if adress != "":
        location = generate_geocode_button(od, adress)
        responses_dict[f"{od}_latitude"] = location[0] if location else ""
        responses_dict[f"{od}_longitude"] = location[1] if location else ""

        if adress == st.session_state.get(f"{od}_geocoded", ""):
            #st.success("Coincide la Dirección Ingresada con la Georreferenciada")
            #st.write(st.session_state["responses"][f"{od}_location_type"])
            pass

    st.divider()

    return responses_dict

def direction_input_question(od):
    
    calle = st.text_input(
        label="Nombre de la Calle",
        key=f"{od}_direction_input"
    )

    nro_calle = st.text_input(
        label="Número",
        key=f"{od}_nro_calle_input"
    )

    comuna = st.text_input(
        label="Comuna",
        key=f"{od}_comuna_input"
    )

    if calle != "" and nro_calle != "" and comuna != "":
        adress = f"{calle} #{nro_calle}, {comuna}, Chile"

        responses_dict = {}
        responses_dict[f"{od}"] = adress
        responses_dict[f"{od}_calle"] = calle
        responses_dict[f"{od}_nro_calle"] = nro_calle
        responses_dict[f"{od}_comuna"] = comuna
        return responses_dict
    
    else:
        empty_responses_dict = {}
        empty_responses_dict[f"{od}"] = ""
        empty_responses_dict[f"{od}_calle"] = ""
        empty_responses_dict[f"{od}_nro_calle"] = ""
        empty_responses_dict[f"{od}_comuna"] = ""
        return empty_responses_dict

def intersection_input_question(od):
    calle1 = st.text_input(
        label="Calle 1",
        key=f"{od}_intersection_calle1_input"
    )
    calle2 = st.text_input(
        label="Calle 2",
        key=f"{od}_intersection_calle2_input"
    )
    comuna = st.text_input(
        label="Comuna",
        key=f"{od}_comuna_input"
    )

    if calle1 != "" and calle2 != "" and comuna != "":
        adress = f"{calle1} & {calle2}, {comuna}, Chile"

        responses_dict = {}
        responses_dict[f"{od}"] = adress
        responses_dict[f"{od}_calle1"] = calle1
        responses_dict[f"{od}_calle2"] = calle2          
        responses_dict[f"{od}_comuna"] = comuna
        return responses_dict   
    else:
        empty_responses_dict = {}
        empty_responses_dict[f"{od}"] = ""
        empty_responses_dict[f"{od}_calle1"] = ""
        empty_responses_dict[f"{od}_calle2"] = ""
        empty_responses_dict[f"{od}_comuna"] = ""
        return empty_responses_dict

def landmark_input_question(od):
    landmark = st.text_input(
        label="Nombre del Hito",
        key=f"{od}_landmark_input"
    )

    comuna = st.text_input(
        label="Comuna",
        key=f"{od}_comuna_input"
    )

    if landmark != "" and comuna != "":        
        adress = f"{landmark}, {comuna}, Chile"

        responses_dict = {}
        responses_dict[f"{od}"] = adress
        responses_dict[f"{od}_hito"] = landmark
        responses_dict[f"{od}_comuna"] = comuna
        return responses_dict  
    
    else:
        empty_responses_dict = {}
        empty_responses_dict[f"{od}"] = ""
        empty_responses_dict[f"{od}_hito"] = ""
        empty_responses_dict[f"{od}_comuna"] = ""
        return empty_responses_dict

#--------------------------------------------------
# Geocoding  Button
#--------------------------------------------------

def generate_geocode_button(od, adress: str):

    geocode_button = st.button(
                            label=f"Georreferenciar {od}",
                            key=f"geocode_{od}_button")
        
    if geocode_button:

        st.session_state[f"{od}_geocoded"] = adress
        location = georreferenciar(adress)

        if location:
            st.session_state[f"coords_{od.lower()}"] = location[:2]
            st.session_state["responses"][f"{od}_location_type"] = location[2] + " " + str(location[3])

        else:
            st.session_state[f"coords_{od.lower()}"] = None
            st.error("No se encontró la ubicación")

    location = st.session_state.get(f"coords_{od.lower()}", None)
    deploy_map(location, od)

    return location

def deploy_map(location, od):

    if location:
        map = folium.Map(location=location, zoom_start=13)
        folium.Marker(
            location=location,
            popup=od,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(map)

    else:
        map = folium.Map(location=(-33.5070883501777, -70.60581992774767), 
                         zoom_start= 13)

    st_folium(map, width=300, height = 300 ,returned_objects=[], key=f"map_{od}")

#--------------------------------------------------
# Button for Next Screen
#--------------------------------------------------

def od_screen_button():

    def set_true_state_variable():
        st.session_state["od_screen_completed"] = True
        st.session_state["time_list"].append(time.time())

    st.button(
        label="Siguiente",
        key="od_screen_button",
        use_container_width= True,
        on_click=set_true_state_variable
    )

#--------------------------------------------------
# Main Function for Screen
#--------------------------------------------------


def generate_od_screen():
    st.title("Origen y Destino del Viaje")

    # Screen Responses Dictionary
    responses_dict = {}

    # Surveyor Location
    surveyor_location = get_surveyor_location()
    responses_dict.update(surveyor_location)

    # Origin Question
    origin_responses_dict = generate_location_question_widget(od="Origen")
    responses_dict.update(origin_responses_dict)

    # Destination Question
    destination_responses_dict = generate_location_question_widget(od="Destino")
    responses_dict.update(destination_responses_dict)

    # Store answers in the state variable 'responses'
    st.session_state["responses"][f"od_screen"] = responses_dict

    if all_responded(responses_dict):
        od_screen_button()