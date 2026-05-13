from supabase import create_client
import streamlit as st

@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = init_supabase()

def process_responses_dict(responses_dict):
    
    output_dict = {}

    for key, value in responses_dict.items():
        if isinstance(value, dict):
            output_dict.update(value)
        else:
            output_dict[key] = value

    output_dict = set_lowercase_keys(output_dict)

    return output_dict

def set_lowercase_keys(input_dict):
    return {k.lower(): v for k, v in input_dict.items()}

def insert_row(row_dict):
    
    response = supabase.table("pd_antofa").insert(row_dict).execute()

def send_to_database(responses_dict):

    row_dict = process_responses_dict(responses_dict)

    insert_row(row_dict)

    st.session_state["responses_sent"] = True
