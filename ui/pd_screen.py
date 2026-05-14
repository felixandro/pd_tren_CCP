import streamlit as st
import time
import base64
from pathlib import Path

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
                    text_color="#000000",
                    centrar=True,
                    bold=True):
    padding = "0.8rem"
    font_size = "18px"
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
    index = ["Minutos de Viaje", "Minutos de Caminata", "Minutos de Espera", "Costo"]

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
        if i == 3:
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

def perfil_eleccion_hibrido_flechas(
    niveles_a,
    niveles_b,
    image_path_actual=None,
    image_path_nuevo=None,
):
    """
    Renderiza un perfil de eleccion alternativo usando una grilla comparativa
    con flechas centradas para indicar si la alternativa B mejora, empeora o
    mantiene cada atributo respecto de la alternativa A.
    """

    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def format_currency(value):
        ivalue = safe_int(value)
        if ivalue is None:
            return "_________"
        return f"${ivalue:,}".replace(",", ".")

    def compare_direction(base_value, new_value):
        """
        Retorna la direccion del cambio para atributos donde menor es mejor.
        """
        base_int = safe_int(base_value)
        new_int = safe_int(new_value)
        if base_int is None or new_int is None:
            return "same"
        if new_int < base_int:
            return "better"
        if new_int > base_int:
            return "worse"
        return "same"

    def format_delta(base_value, new_value, suffix=""):
        """
        Retorna la diferencia (nuevo - actual) con signo visible.
        """
        base_int = safe_int(base_value)
        new_int = safe_int(new_value)
        if base_int is None or new_int is None:
            return "Sin dato"

        delta = new_int - base_int
        sign = "+" if delta > 0 else ""
        suffix_text = f" {suffix}" if suffix else ""
        return f"{sign}{delta}{suffix_text}"

    def arrow_svg(direction):
        if direction == "better":
            # Flecha hacia abajo = mejora = verde
            return (
                "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
                "<path d='M9 4 L9 14 M4 9 L9 14 L14 9' "
                "stroke='#1D9E75' stroke-width='2' stroke-linecap='round' "
                "stroke-linejoin='round'/></svg>"
            )
        if direction == "worse":
            # Flecha hacia arriba = empeora = rojo
            return (
                "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
                "<path d='M9 14 L9 4 M4 9 L9 4 L14 9' "
                "stroke='#D85A30' stroke-width='2' stroke-linecap='round' "
                "stroke-linejoin='round'/></svg>"
            )
        return (
            "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
            "<path d='M3 9 L15 9' stroke='#888780' stroke-width='2' "
            "stroke-linecap='round'/></svg>"
        )

    alt_a = niveles_a[0]
    alt_b = niveles_b[0]

    tv_a, tc_a, te_a, c_a = niveles_a[1], niveles_a[2], niveles_a[3], niveles_a[4]
    tv_b, tc_b, te_b, c_b = niveles_b[1], niveles_b[2], niveles_b[3], niveles_b[4]

    rows = [
        {
            "label": "Tiempo de viaje",
            "left": f"{tv_a} <span class='attr-unit'>min</span>",
            "right": f"{tv_b} <span class='attr-unit'>min</span>",
            "arrow": arrow_svg(compare_direction(tv_a, tv_b)),
            "direction": compare_direction(tv_a, tv_b),
            "delta": format_delta(tv_a, tv_b, "min"),
        },
        {
            "label": "Tiempo de espera",
            "left": f"{te_a} <span class='attr-unit'>min</span>",
            "right": f"{te_b} <span class='attr-unit'>min</span>",
            "arrow": arrow_svg(compare_direction(te_a, te_b)),
            "direction": compare_direction(te_a, te_b),
            "delta": format_delta(te_a, te_b, "min"),
        },
        {
            "label": "Tiempo de caminata",
            "left": f"{tc_a} <span class='attr-unit'>min</span>",
            "right": f"{tc_b} <span class='attr-unit'>min</span>",
            "arrow": arrow_svg(compare_direction(tc_a, tc_b)),
            "direction": compare_direction(tc_a, tc_b),
            "delta": format_delta(tc_a, tc_b, "min"),
        },
        # {
        #     "label": "Costo",
        #     "left": format_currency(c_a),
        #     "right": format_currency(c_b),
        #     "arrow": arrow_svg(compare_direction(c_a, c_b)),
        # },
    ]

    def load_image_b64(image_path):
        if not image_path:
            return ""

        cache_key = "_pd_hibrido_images_b64_cache"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = {}

        image_path_str = str(image_path)
        cache = st.session_state[cache_key]
        if image_path_str in cache:
            return cache[image_path_str]

        try:
            image_file_path = Path(image_path_str)
            if not image_file_path.is_absolute():
                image_file_path = Path(__file__).resolve().parents[1] / image_file_path
            image_b64 = base64.b64encode(image_file_path.read_bytes()).decode("ascii")
        except OSError:
            image_b64 = ""

        cache[image_path_str] = image_b64
        return image_b64

    left_image_b64 = load_image_b64(image_path_actual)
    right_image_b64 = load_image_b64(image_path_nuevo)
    card_background_css = "background: rgba(255, 255, 255, 0.95);"

    estilo = """
    <style>
    .pd-h-card {
        __CARD_BG__
        border: 0.5px solid #d8d8d8;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 0.75rem;
    }
    .pd-h-header {
        background: #f6f6f4;
        padding: 10px 1rem;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 0.5px solid #e1e1e1;
        flex-wrap: wrap;
    }
    .pd-h-tag {
        font-size: 10px;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 999px;
    }
    .pd-h-tag-a {
        background: #f0efea;
        color: #4b4a45;
    }
    .pd-h-tag-b {
        background: #e7f4ee;
        color: #0a5a47;
    }
    .pd-h-grid {
        display: grid;
        grid-template-columns: 1fr 64px 1fr;
        padding: 0.8rem 1rem 1rem 1rem;
        column-gap: 0;
        row-gap: 0;
        align-items: stretch;
    }
    .pd-h-col-title {
        font-size: 16px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding-bottom: 8px;
    }
    .pd-h-col-a {
        color: #66645f;
    }
    .pd-h-col-b {
        color: #66645f;
    }
    .pd-h-cell {
        display: flex;
        flex-direction: column;
        border-top: 0.5px solid #e7e7e7;
        padding: 8px 0;
    }
    .pd-h-cell-image {
        min-height: 160px;
        padding-top: 8px;
        padding-bottom: 0;
    }
    .pd-h-label {
        font-size: 13px;
        color: #777;
        margin-bottom: 3px;
    }
    .pd-h-value {
        font-size: 24px;
        font-weight: 600;
        line-height: 1.2;
        color: #222;
        width: 100%;
        text-align: center;
    }
    .attr-unit {
        font-size: 11px;
        font-weight: 400;
        color: #666;
    }
    .pd-h-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-top: 0.5px solid #e7e7e7;
        padding: 8px 0;
        gap: 8px;
    }
    .pd-h-delta {
        font-size: 14px;
        font-weight: 600;
        line-height: 1;
        text-align: center;
    }
    .pd-h-delta-better {
        color: #1D9E75;
    }
    .pd-h-delta-worse {
        color: #D85A30;
    }
    .pd-h-delta-same {
        color: #888780;
    }
    .pd-h-inline-image {
        width: 100% !important;
        max-width: 100%;
        height: auto;
        min-height: 140px;
        aspect-ratio: 16 / 9;
        display: block;
        align-self: stretch;
        object-fit: cover;
        border-radius: 0;
        border: 0.5px solid #d8d8d8;
    }
    .pd-h-no-image {
        font-size: 10px;
        color: #8a8a8a;
        font-weight: 500;
    }
    </style>
    """
    estilo = estilo.replace("__CARD_BG__", card_background_css)

    tabla = (
        "<div class='pd-h-card'>"
        "<div class='pd-h-grid'>"
        f"<div class='pd-h-col-title pd-h-col-a'>{alt_a}</div>"
        "<div class='pd-h-col-title'></div>"
        f"<div class='pd-h-col-title pd-h-col-b'>{alt_b}</div>"
    )

    if left_image_b64:
        left_image_html = (
            f"<img class='pd-h-inline-image' src='data:image/jpeg;base64,{left_image_b64}' "
            "alt='Referencia modo actual'/>"
        )
    else:
        left_image_html = "<div class='pd-h-no-image'>Sin imagen</div>"

    if right_image_b64:
        right_image_html = (
            f"<img class='pd-h-inline-image' src='data:image/jpeg;base64,{right_image_b64}' "
            "alt='Referencia modo nuevo'/>"
        )
    else:
        right_image_html = "<div class='pd-h-no-image'>Sin imagen</div>"

    #tabla += (
    #    "<div class='pd-h-cell pd-h-cell-image'>"
    #    f"{left_image_html}"
    #    "</div>"
    #    "<div class='pd-h-arrow'></div>"
    #    "<div class='pd-h-cell pd-h-cell-image'>"
    #    f"{right_image_html}"
    #    "</div>"
    #)

    for row in rows:
        tabla += (
            "<div class='pd-h-cell'>"
            f"<div class='pd-h-label'>{row['label']}</div>"
            f"<div class='pd-h-value'>{row['left']}</div>"
            "</div>"
            f"<div class='pd-h-arrow'>{row['arrow']}"
            f"<div class='pd-h-delta pd-h-delta-{row['direction']}'>{row['delta']}</div>"
            "</div>"
            "<div class='pd-h-cell'>"
            f"<div class='pd-h-label'>{row['label']}</div>"
            f"<div class='pd-h-value'>{row['right']}</div>"
            "</div>"
        )

    tabla += "</div></div>"

    st.markdown(estilo + tabla, unsafe_allow_html=True)

def tabla_comparativa_costos(
    costo_a,
    costo_b,
    nombre_modo_actual="Modo actual",
    nombre_modo_nuevo="Modo nuevo",
):
    """
    Renderiza una tabla comparativa de una sola fila para costo actual vs costo nuevo.
    """

    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def format_currency(value):
        ivalue = safe_int(value)
        if ivalue is None:
            return "_________"
        return f"${ivalue:,}".replace(",", ".")

    def compare_direction(base_value, new_value):
        base_int = safe_int(base_value)
        new_int = safe_int(new_value)
        if base_int is None or new_int is None:
            return "same"
        if new_int < base_int:
            return "better"
        if new_int > base_int:
            return "worse"
        return "same"

    def format_delta(base_value, new_value):
        base_int = safe_int(base_value)
        new_int = safe_int(new_value)
        if base_int is None or new_int is None:
            return "Sin dato"

        delta = new_int - base_int
        sign = "+" if delta > 0 else ""
        return f"{sign}${abs(delta):,}".replace(",", ".") if delta >= 0 else f"-${abs(delta):,}".replace(",", ".")

    def arrow_svg(direction):
        if direction == "better":
            return (
                "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
                "<path d='M9 4 L9 14 M4 9 L9 14 L14 9' "
                "stroke='#1D9E75' stroke-width='2' stroke-linecap='round' "
                "stroke-linejoin='round'/></svg>"
            )
        if direction == "worse":
            return (
                "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
                "<path d='M9 14 L9 4 M4 9 L9 4 L14 9' "
                "stroke='#D85A30' stroke-width='2' stroke-linecap='round' "
                "stroke-linejoin='round'/></svg>"
            )
        return (
            "<svg width='24' height='24' viewBox='0 0 18 18' fill='none'>"
            "<path d='M3 9 L15 9' stroke='#888780' stroke-width='2' "
            "stroke-linecap='round'/></svg>"
        )

    direction = compare_direction(costo_a, costo_b)
    delta = format_delta(costo_a, costo_b)

    estilo = """
    <style>
    .pd-c-card {
        background: rgba(255, 255, 255, 0.95);
        border: 0.5px solid #d8d8d8;
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 0.75rem;
    }
    .pd-c-grid {
        display: grid;
        grid-template-columns: 1fr 64px 1fr;
        padding: 0.8rem 1rem 1rem 1rem;
        column-gap: 0;
        row-gap: 0;
        align-items: stretch;
    }
    .pd-c-col-title {
        font-size: 16px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding-bottom: 8px;
        color: #66645f;
    }
    .pd-c-cell {
        display: flex;
        flex-direction: column;
        border-top: 0.5px solid #e7e7e7;
        padding: 10px 0;
    }
    .pd-c-label {
        font-size: 13px;
        color: #777;
        margin-bottom: 4px;
    }
    .pd-c-value {
        font-size: 24px;
        font-weight: 600;
        line-height: 1.2;
        color: #222;
        width: 100%;
        text-align: center;
    }
    .pd-c-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-top: 0.5px solid #e7e7e7;
        padding: 10px 0;
        gap: 8px;
    }
    .pd-c-delta {
        font-size: 14px;
        font-weight: 600;
        line-height: 1;
        text-align: center;
    }
    .pd-c-delta-better {
        color: #1D9E75;
    }
    .pd-c-delta-worse {
        color: #D85A30;
    }
    .pd-c-delta-same {
        color: #888780;
    }
    </style>
    """

    tabla = (
        "<div class='pd-c-card'>"
        "<div class='pd-c-grid'>"
        f"<div class='pd-c-col-title'>{nombre_modo_actual}</div>"
        "<div class='pd-c-col-title'></div>"
        f"<div class='pd-c-col-title'>{nombre_modo_nuevo}</div>"
        "<div class='pd-c-cell'>"
        "<div class='pd-c-label'>Costo</div>"
        f"<div class='pd-c-value'>{format_currency(costo_a)}</div>"
        "</div>"
        f"<div class='pd-c-arrow'>{arrow_svg(direction)}"
        f"<div class='pd-c-delta pd-c-delta-{direction}'>{delta}</div>"
        "</div>"
        "<div class='pd-c-cell'>"
        "<div class='pd-c-label'>Costo</div>"
        f"<div class='pd-c-value'>{format_currency(costo_b)}</div>"
        "</div>"
        "</div></div>"
    )

    st.markdown(estilo + tabla, unsafe_allow_html=True)

def get_nivels(id_pd_card):
    df = st.session_state["choice_set_df"]
    row = df.loc[id_pd_card]

    niveles_a = [
        row["label1"],
        row["tv1"],
        row["tc1"],
        row["te1"],
        row["c1"]
    ]

    niveles_b = [
        row["label2"],
        row["tv2"],
        row["tc2"],
        row["te2"],
        row["c2"]
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

def yes_no_button(label_alt, nro_alt, id_pd_card, nro_pregunta):

    def save_choice():
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_{nro_pregunta}"] = nro_alt
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_{nro_pregunta}_label"] = label_alt
   
    st.button(
        label=f"{label_alt}",
        key=f"pd_{id_pd_card}_alt_{nro_alt}_{nro_pregunta}_button",
        use_container_width= True,
        on_click=save_choice
    )

def yes_no_button_inline(id_pd_card, nro_pregunta, modo_actual, modo_nuevo):

    label_no = f"No, elijo {modo_actual}"
    label_yes = f"Sí, elijo {modo_nuevo}"

    def save_choice(label_alt, nro_alt):
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_{nro_pregunta}"] = nro_alt
        st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_{nro_pregunta}_label"] = label_alt

    col_no, col_yes = st.columns(2)

    with col_no:
        st.button(
            label=label_no,
            key=f"pd_{id_pd_card}_inline_no_{nro_pregunta}_button",
            use_container_width=True,
            on_click=save_choice,
            args=(label_no, 0)
        )

    with col_yes:
        st.button(
            label=label_yes,
            key=f"pd_{id_pd_card}_inline_yes_{nro_pregunta}_button",
            use_container_width=True,
            on_click=save_choice,
            args=(label_yes, 1)
        )

def next_pd_button(id_pd_card):

    def set_true_state_variable():
        st.session_state["order_pd_choice_sets"].pop(0)
        st.session_state["time_list"].append(time.time())
        st.session_state["pd_count"] += 1

    st.divider()

    st.button(
        label="Siguiente Pregunta",
        key=f"next_pd_{id_pd_card}_button",
        use_container_width= True,
        on_click=set_true_state_variable
    )

def get_figure_path(alternativa):

    if alternativa == "Auto Particular":
        return "data/figuras/auto.png"
    
    elif alternativa == "Taxibus":
        return "data/figuras/taxibus.png"
    
    elif alternativa == "Taxicolectivo":
        return "data/figuras/taxicolectivo.png"

    elif alternativa == "Tren":
        return "data/figuras/tren.png"
    
    elif alternativa == "Tranvía":
        return "data/figuras/tranvia.png"
        
    elif alternativa == "Corredor de Buses":
        return "data/figuras/corredor.png"

def get_costo_b_list(costo_a):

    cb_list = [int(costo_a), 
               int(costo_a + 300), 
               int(costo_a + 600)]

    for i in range(len(cb_list)):
        if f"cb_{i}" not in st.session_state["responses"]["choice_dict"]:
            st.session_state["responses"]["choice_dict"][f"cb_{i}"] = cb_list[i]

    return cb_list

def generate_pd_screen(id_pd_card):
    def format_currency_safe(value):
        try:
            ivalue = int(float(value))
            return f"${ivalue:,}".replace(",", ".")
        except (TypeError, ValueError):
            return "$---"

    pd_count = st.session_state["pd_count"]
    st.title(f"PD {pd_count}")

    st.markdown(
        "<p style='font-size: 16px; margin-bottom: 1rem;'>Suponga que repite su viaje actual y tiene las siguientes alternativas:</p>",
        unsafe_allow_html=True
    )

    # Perfil de Elección
    niveles_a, niveles_b = get_nivels(id_pd_card)

    alt_a = niveles_a[0]
    costo_a = niveles_a[4]

    alt_b = niveles_b[0]
    
    perfil_eleccion_hibrido_flechas(
        niveles_a,
        niveles_b,
        image_path_actual=get_figure_path(alt_a),
        image_path_nuevo=get_figure_path(alt_b),
    )

    alt_a = niveles_a[0]
    costo_a = niveles_a[4]

    alt_b = niveles_b[0]
    costo_b_list = get_costo_b_list(costo_a)
    costo_b_ref = costo_b_list[1]
    costo_b_bajo = costo_b_list[0]
    costo_b_alto = costo_b_list[2]

    #st.divider()

    st.markdown(
        (
            "<p style='font-size: 16px; margin-bottom: 1rem;'>"
            f"Si el <strong>{alt_a}</strong> le cuesta <strong>{format_currency_safe(costo_a)}</strong> "
            f"¿Utilizaría el <strong>{alt_b}</strong> si costara <strong>{format_currency_safe(costo_b_ref)}</strong>?"
            "</p>"
        ),
        unsafe_allow_html=True
    )

    tabla_comparativa_costos(
        costo_a,
        costo_b_ref,
        nombre_modo_actual=alt_a,
        nombre_modo_nuevo=alt_b,
    )

    # Alternative 1 Button
    #label_a = niveles_a[0]
    #choice_alt_button(label_a,1, id_pd_card)
    
    # Alternative 2 Button
    label_b = niveles_b[0]
    #choice_alt_button(label_b,2, id_pd_card)

    #yes_no_button("Sí", 1, id_pd_card,1)
    #yes_no_button("No", 0, id_pd_card,1)

    yes_no_button_inline(id_pd_card, 1, modo_actual=alt_a, modo_nuevo=alt_b)

    if f"choice_tj_{id_pd_card}_1" in st.session_state["responses"]["choice_dict"]:
        choice_alt_chosen = st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_1"]
        label_alt_chosen = st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_1_label"]

        st.markdown(
            (
                "<p style='font-size: 16px; margin-bottom: 1rem; text-align: center;'>"
                f"Seleccionaste <strong>{label_alt_chosen}</strong>"
                "</p>"
            ),
            unsafe_allow_html=True
        )

        #st.divider()

        if choice_alt_chosen == 1:

            st.markdown(
                (
                    "<p style='font-size: 16px; margin-bottom: 1rem; text-align: center;'>"
                    f"¿Y utilizaría <strong>{label_b}</strong> si tuviera que pagar "
                    f"<strong>{format_currency_safe(costo_b_alto)}</strong>?"
                    "</p>"
                ),
                unsafe_allow_html=True
            )

            tabla_comparativa_costos(
                costo_a,
                costo_b_alto,
                nombre_modo_actual=alt_a,
                nombre_modo_nuevo=alt_b,
            )

        elif choice_alt_chosen == 0:

            st.markdown(
                (
                    "<p style='font-size: 16px; margin-bottom: 1rem; text-align: center;'>"
                    f"¿Y utilizaría <strong>{label_b}</strong> si tuviera que pagar "
                    f"<strong>{format_currency_safe(costo_b_bajo)}</strong>?"
                    "</p>"
                ),
                unsafe_allow_html=True
            )

            tabla_comparativa_costos(
                costo_a,
                costo_b_bajo,
                nombre_modo_actual=alt_a,
                nombre_modo_nuevo=alt_b,
            )
            
        #yes_no_button("Sí", 1, id_pd_card,2)
        #yes_no_button("No", 0, id_pd_card,2)
        yes_no_button_inline(id_pd_card, 2, modo_actual=alt_a, modo_nuevo=alt_b)

        if f"choice_tj_{id_pd_card}_2" in st.session_state["responses"]["choice_dict"]:

            label_alt_chosen_2 = st.session_state["responses"]["choice_dict"][f"choice_tj_{id_pd_card}_2_label"]

            st.markdown(
                (
                    "<p style='font-size: 16px; margin-bottom: 1rem; text-align: center;'>"
                    f"Seleccionaste <strong>{label_alt_chosen_2}</strong>"
                    "</p>"
                ),
                unsafe_allow_html=True
            )

            # Next PD Button
            next_pd_button(id_pd_card)
    
