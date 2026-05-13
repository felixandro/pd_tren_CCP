import streamlit as st
from datetime import datetime, timedelta


def process_time_list():
    """Calcula las diferencias de tiempo entre entradas consecutivas en time_list."""
    
    time_list = st.session_state["time_list"]
    time_differences_dict = {}
    
    for i in range(1, len(time_list)):
        difference = time_list[i] - time_list[i - 1]
        time_differences_dict[f"s{i+1}_seconds"] = round(difference,1)

    st.session_state["responses"]["time_differences"] = time_differences_dict

def record_datetime():
    """Registra la fecha y hora actuales en las respuestas (UTC-3 para Chile)."""

    if "datetime" not in st.session_state["responses"]:
        utc_time = datetime.now()    
        chile_time = utc_time - timedelta(hours=3)
        current_datetime = chile_time.strftime("%Y-%m-%d %H:%M:%S")
        st.session_state["responses"]["datetime"] = current_datetime