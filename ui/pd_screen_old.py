import streamlit as st
import time

def initialize_pd_responses():

    def generate_order_pd_choice_sets_dict():

        order_pd_choice_sets_dict = {}
        
        for index, pd_card in enumerate(st.session_state["order_pd_choice_sets"]):
            order_pd_choice_sets_dict[f"pd_{index+1}"] = pd_card
        
        return order_pd_choice_sets_dict

    if "order_pd_choice_sets" not in st.session_state["responses"]:
        order_dict = generate_order_pd_choice_sets_dict()
        st.session_state["responses"]["order_pd_choice_sets"] = order_dict

    if "choice_dict" not in st.session_state["responses"]:
        st.session_state["responses"]["choice_dict"] = {}

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

def perfil_eleccion(niveles_a, niveles_b):
    # Variables de estilo
    alpha = 0.95
    font_size_header = "18px"
    font_size_cells = "16px"

    # Datos
    index = ["Costo", "Minutos de Viaje", "Minutos de Caminata", "Minutos de Espera"]

    # Estilo CSS
    estilo_tabla = f"""
    <style>
    table {{
        border-collapse: collapse;
        width: 100%;
        table-layout: fixed;
    }}
    td {{
        border: 1px solid #ddd;
        padding: 6px 12px;
        text-align: center;
        vertical-align: middle;
        font-size: {font_size_cells};
    }}
    /* Estilo fila encabezado (primera fila) */
    tr:first-child td {{
        background-color: rgba(255, 255, 255, {alpha});
        font-size: {font_size_header};
        font-weight: bold;
    }}
    /* Anchos fijos columnas */
    tr:first-child td:nth-child(1),
    td:nth-child(1) {{
        width: 30%;
    }}
    tr:first-child td:nth-child(2),
    td:nth-child(2) {{
        width: 35%;
    }}
    tr:first-child td:nth-child(3),
    td:nth-child(3) {{
        width: 35%;
    }}
    /* Estilo primera columna */
    td.col-criterio {{
        color: black;
        font-weight: 600;
        background-color: rgba(255, 255, 255, {alpha});
    }}
    /* Estilo segunda columna (rojo) */
    td.col-a {{
        color: red;
        font-weight: bold;
        background-color: rgba(255, 255, 255, {alpha});
    }}
    /* Estilo tercera columna (azul) */
    td.col-b {{
        color: blue;
        font-weight: bold;
        background-color: rgba(255, 255, 255, {alpha});
    }}
    /* Filas pares con gris suave */
    tr:nth-child(even) td {{
        background-color: #f5f5f5;
    }}
    </style>
    """

    # Construcción de la tabla HTML
    tabla_html = estilo_tabla + "<table>"

    alt_a = niveles_a[0]
    alt_b = niveles_b[0]

    # Fila encabezado como primera fila con <td>
    tabla_html += (
        f"<tr>"
        f"<td class='col-criterio'></td>"
        f"<td class='col-a'>{alt_a} </td>"
        f"<td class='col-b'>{alt_b} </td>"
        f"</tr>"
    )

    # Filas de datos
    for i in range(len(index)):
        if i == 0:
            # Formatear los valores de costo con separador de miles y signo $
            try:
                niv_a = f"${niveles_a[i+1]:,}".replace(",", ".")
            except ValueError:
                niv_a = "_______________"
            try:
                niv_b = f"${niveles_b[i+1]:,}".replace(",", ".")
            except ValueError:
                niv_b = "_______________"
        else:
            niv_a = niveles_a[i+1]
            niv_b = niveles_b[i+1]
        tabla_html += (
            f"<tr>"
            f"<td class='col-criterio'>{index[i]}</td>"
            f"<td class='col-a'>{niv_a}</td>"
            f"<td class='col-b'>{niv_b}</td>"
            f"</tr>"
        )

    tabla_html += "</table>"

    # Mostrar en Streamlit
    st.markdown(tabla_html, unsafe_allow_html=True)

def get_nivels(id_pd_card):
    df = st.session_state["choice_set_df"]
    row = df.loc[id_pd_card]

    niveles_a = [
        row["label1"],
        row["c1"],
        row["tv1"],
        row["tc1"],
        row["te1"]
    ]

    niveles_b = [
        row["label2"],
        row["c2"],
        row["tv2"],
        row["tc2"],
        row["te2"]
    ]

    def rename_row_dict(row_dict, id_pd_card):
        renamed_dict = {}
        for key, value in row_dict.items():
            new_key = f"tj{id_pd_card}_{key}"
            renamed_dict[new_key] = value
        return renamed_dict

    renamed_row_dict = rename_row_dict(row.to_dict(), id_pd_card)

    if f"tj{id_pd_card}_atr" not in st.session_state["responses"]:
        st.session_state["responses"][f"tj{id_pd_card}_atr"] = renamed_row_dict

    return niveles_a, niveles_b

def choice_alt_button(label_alt, nro_alt, id_pd_card):

    def save_choice():
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}"] = nro_alt
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_label"] = label_alt
   
    st.button(
        label=f"{label_alt}",
        key=f"pd_{id_pd_card}_alt_{label_alt}_button",
        use_container_width= True,
        on_click=save_choice
    )

def next_pd_button(id_pd_card):

    def set_true_state_variable():
        st.session_state["order_pd_choice_sets"].pop(0)
        st.session_state["time_list"].append(time.time())
        st.session_state["pd_count"] += 1

    st.button(
        label="Siguiente",
        key=f"next_pd_{id_pd_card}_button",
        use_container_width= True,
        on_click=set_true_state_variable
    )

def generate_pd_screen(id_pd_card):
    pd_count = st.session_state["pd_count"]
    st.title(f"PD {pd_count}")

    # Perfil de Elección
    niveles_a, niveles_b = get_nivels(id_pd_card)
    perfil_eleccion(niveles_a, niveles_b)

    # Alternative 1 Button
    label_a = niveles_a[0]
    choice_alt_button(label_a,1, id_pd_card)
    
    # Alternative 2 Button
    label_b = niveles_b[0]
    choice_alt_button(label_b,2, id_pd_card)

    if f"choice_tj_{id_pd_card}" in st.session_state["responses"]["choice_dict"]:
        label_alt_chosen = st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_label"]
        texto_con_fondo(
            texto=f"Seleccionaste {label_alt_chosen}"
        )

        # Next PD Button
        next_pd_button(id_pd_card)
    
