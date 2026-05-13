import streamlit as st
import pandas as pd
import time
import textwrap

#----------------------------------
# Load Questions Information
#----------------------------------

def load_questions_info(id_screen: int):

    path = f"data/screen{id_screen}_questions.csv"
    df = pd.read_csv(path, header = None, sep = ";")

    return df

#--------------------------------------------------
# Helper Functions
#--------------------------------------------------

def all_responded(responses_dict):
    """Verifica que todas las preguntas hayan sido contestadas."""
    for _, value in responses_dict.items():
        if value == "" or value is None:
            return False
    return True

def texto_con_fondo(texto, 
                    upper_margin="1rem", 
                    bg_color="rgba(255, 255, 255, 0.95)",
                    text_color="#000000"):
    padding = "0.8rem"
    font_size = "18px"
    bold = True
    centrar = True
    margen = f"0 0 {upper_margin} 0"
    weight = "bold" if bold else "normal"
    alineacion = "center" if centrar else "left"

    st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: {padding};
        margin: {margen};
        border-radius: 8px;
        font-size: {font_size};
        font-weight: {weight};
        color: {text_color};
        text-align: {alineacion};
        word-wrap: break-word;
        overflow-wrap: break-word;
    ">
        {texto}
    </div>
    """, unsafe_allow_html=True)

#--------------------------------------------------
# Question Widgets Generation
#--------------------------------------------------

def generate_question_widget(question_col_list, key_widget: str):
    """Genera el widget correspondiente según el tipo de pregunta."""
    
    question_type = question_col_list[0] #Selectbox o Number Input
    question_key = question_col_list[1] #Clave para almacenar la respuesta
    question_label = question_col_list[2] #Etiqueta de la pregunta
    question_label2 = question_col_list[3] if pd.notna(question_col_list[3]) else "" #Etiqueta secundaria (si aplica)

    if question_type == "title":
        st.title(question_label)
        return {}
    
    elif question_type == "text":
        texto_con_fondo(texto=question_label)
        return {}
    
    elif question_type == "selectbox":
        options = [opt for opt in question_col_list[4:] if pd.notna(opt)]
        response = selectbox_question(
            label=question_label,
            label2 = question_label2,
            options=options,
            key= key_widget
        )
        
    elif question_type == "number_input":
        min_value = int(question_col_list[4])
        max_value = int(question_col_list[5])
        response = number_input_question(
            label=question_label,
            label2=question_label2,
            min_value=min_value,
            max_value=max_value,
            key= key_widget
        )

    return {question_key: response}

def selectbox_question(label: str, label2: str, options: list, key: str):
    st.subheader(label)
    selectbox = st.selectbox(
        label=label2,
        options=[""] + options,
        key=key
    )
    return selectbox

def number_input_question(label: str, label2: str, min_value: int, max_value: int, key: str):
    st.subheader(label)
    number_input = st.number_input(
        value = None,
        label=label2,
        key=key,
        min_value=min_value,
        max_value=max_value,
        step=1
    )
    return number_input

#--------------------------------------------------
# Button for Next Screen
#--------------------------------------------------

def screen_button(id_screen: int):

    def set_true_state_variable(id_screen: int):
        st.session_state[f"screen{id_screen}_completed"] = True
        st.session_state[f"time_list"].append(time.time())

    st.button(
        label="Siguiente",
        key=f"screen{id_screen}_button",
        use_container_width= True,
        on_click=set_true_state_variable,
        args=(id_screen,)
    )


#--------------------------------------------------
# Main Function for Screen
#--------------------------------------------------

def generate_general_screen(id_screen: int):

    # Information Questions DataFrame
    questions_df = load_questions_info(id_screen)
    n_questions = len(questions_df.columns) - 1 # Number of questions

    # Screen Responses Dictionary
    responses_dict = {}

    # Questions
    for i in range(1, n_questions + 1):

        question_col_list = questions_df.iloc[:, i].tolist() # Question Information List
        key_widget = f"s{id_screen}_q{i}" # Key for the widget
        question_widget = generate_question_widget(question_col_list, key_widget) # Generate Question Widget
        
        responses_dict.update(question_widget) # Update Responses Dictionary

    # Store answers in the state variable 'responses'
    st.session_state["responses"][f"screen{id_screen}"] = responses_dict

    if all_responded(responses_dict):
        screen_button(id_screen)

