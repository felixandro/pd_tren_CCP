import streamlit as st
import pandas as pd
import time


def show_screen1_responses():
    screen1_responses = st.session_state["responses"]["screen1"]
    st.write(f"**Encuestador**: {screen1_responses['id_encuestador']}")
    #st.write(f"**Punto de Control**: {screen1_responses['pc']}")

#--------------------------------------------------
# Button for Next Screen
#--------------------------------------------------

def restart_button():

    def restart_survey():

        screen1_responses_dict = st.session_state["responses"]["screen1"].copy()

        st.session_state.clear()
        st.session_state["screen1_completed"] = True
        st.session_state["responses"] = {}
        st.session_state["responses"]["screen1"] = screen1_responses_dict
        st.session_state["time_list"] = [time.time()]

    button = st.button(
        label="Nueva Encuesta",
        key="od_screen_button",
        use_container_width= True,
        on_click=restart_survey
    )
    return button

def change_screen1_responses_button():

    def restart_all_state_variable():

        st.session_state.clear()

    button = st.button(
        label="Cambiar Encuestador",
        key="change_screen1_responses_button",
        use_container_width= True,
        on_click=restart_all_state_variable
    )


#--------------------------------------------------
# Main Function for Screen
#--------------------------------------------------


def generate_restart_screen():
    st.title("Encuesta Finalizada")

    st.divider()

    show_screen1_responses()

    change_screen1_responses_button()

    st.divider()

    restart_button()