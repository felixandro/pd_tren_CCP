import streamlit as st
import pandas as pd
import geopandas as gpd
import random

def get_modo_PR():
    modo_PR = st.session_state["responses"]["screen3"].get("modo_PR", False)
    return modo_PR

def get_nivels_PR():

    screen_list = ["screen51", "screen52", "screen53"]
    
    for screen in screen_list:
        if screen in st.session_state["responses"]:
            return st.session_state["responses"][screen]
    
    return None

def get_nivels_api():
    return st.session_state["responses"].get("api_nivels", None)

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

def get_nearest_multiple(x1, x2):
    """
    Retorna el múltiplo de x2 más cercano a x1.
    
    Args:
        x1: Valor de referencia
        x2: Base del múltiplo
    
    Returns:
        El múltiplo de x2 más cercano a x1
    """
    return round(x1 / x2) * x2

### ------------------------------------------
### Funciones para calcular niveles de servicio PD
### Alternativa Actual (modo_PR)
### ------------------------------------------

def compute_c_pd_current_mode(modo_PR, nivels_rail):

    if modo_PR == "Biotren - Taxibus":

        tarifa = nivels_rail.get("tarifa", 700) 
        c_pd =tarifa + 200

    c_pd_list = [int(c_pd)] * 8
    return c_pd_list

def compute_tv_pd_current_mode(modo_PR, nivels_rail, nivels_comple):

    if modo_PR == "Biotren - Taxibus":

        tv_rail = nivels_rail.get("t_bus_min", 0) + nivels_rail.get("t_heavy_rail_min", 0)
        tv_comple = nivels_comple.get("t_bus_min", 0) + nivels_comple.get("t_heavy_rail_min", 0)
        tv_pd = int(tv_rail + tv_comple)

    tv_pd_list = [tv_pd] * 8
    return tv_pd_list

def compute_tc_pd_current_mode(modo_PR, nivels_rail, nivels_comple):

    if modo_PR == "Biotren - Taxibus":

        tc_rail = nivels_rail.get("t_walking_min", 0)
        tc_comple = nivels_comple.get("t_walking_min", 0)
        tc_pd = min(int(tc_rail + tc_comple), 25)

    tc_pd_list = [tc_pd] * 8
    return tc_pd_list
    
def compute_te_pd_current_mode(modo_PR):

    if modo_PR == "Biotren - Taxibus":

        te_pd = 12

    te_pd_list = [te_pd] * 8
    return te_pd_list

### ------------------------------------------
### Funciones para calcular niveles de servicio PD
### Alternativa Hipotética (Tren, Tranvía, BRT)
### ------------------------------------------

def compute_c_pd_new_mode():
    columna_c_pd_list = [0,0,1,1,2,2,1,1]
    niveles_c_pd = {0: "x", 1: "x", 2: "x"}
    c_pd_list = [niveles_c_pd[c] for c in columna_c_pd_list]
    return c_pd_list

def compute_tc_pd_new_mode(modo_nuevo, nivels_rail, nivels_proy):

    if modo_nuevo == "Biotren - Metro":

        tc_rail = nivels_rail.get("t_walking_min", 0)
        tc_proy = nivels_proy.get("tv_wlk", 0)
        tc_pd = min(int(tc_rail + tc_proy), 25)

        columna_tc_pd_list = [0,1,0,1,1,0,1,0]
    
        niveles_tc_pd = {0: tc_pd, 
                         1: tc_pd + 5}
    
        tc_pd_list = [niveles_tc_pd[tc] for tc in columna_tc_pd_list]

        return tc_pd_list

    
def compute_tv_pd_new_mode(modo_nuevo, nivels_rail, nivels_proy):

    columna_tv_pd_list = [0,0,1,1,0,0,1,1]

    if modo_nuevo == "Biotren - Metro":

        tv_rail = nivels_rail.get("t_bus_min", 0) + nivels_rail.get("t_heavy_rail_min", 0)
        tv_proy = nivels_proy.get("tv_metro", 0)
        tv_pd = int(tv_rail + tv_proy)

        niveles_tv_pd = {0: int(tv_rail + tv_proy), 
                         1: int(tv_rail * 0.9 + tv_proy * 0.7)}
    
        tv_pd_list = [niveles_tv_pd[tv] for tv in columna_tv_pd_list]

        return tv_pd_list
    
def compute_te_pd_new_mode(modo_nuevo):

    columna_te_pd_list = [0,1,0,1,0,1,0,1]

    if modo_nuevo == "Biotren - Metro":
        niveles_te_pd = {0: 4, 
                         1: 8}
                
    te_pd_list = [niveles_te_pd[te] for te in columna_te_pd_list]
    return te_pd_list

### ------------------------------------------
### Función para generar diseño experimental PD
### ------------------------------------------

def generate_choice_set_df():

    modo_PR = "Biotren - Taxibus"
    modo_nuevo = "Biotren - Metro"
    nivels_PR = get_nivels_PR()
    nivels_api = get_nivels_api()

    nivels_rail = st.session_state["responses"].get("rail_api_nivels", None)
    nivels_comple = st.session_state["responses"].get("comple_api_nivels", None)
    nivels_proy = st.session_state["responses"].get("proy_nivels", None)

    tj_list = list(range(1, 9))
    block_list = [1,2,1,2,2,1,2,1]

    label1_list = [modo_PR] * 8
    c1_list = compute_c_pd_current_mode(modo_PR, nivels_rail)
    tc1_list = compute_tc_pd_current_mode(modo_PR, nivels_rail, nivels_comple)
    tv1_list = compute_tv_pd_current_mode(modo_PR, nivels_rail, nivels_comple)
    te1_list = compute_te_pd_current_mode(modo_PR)
    
    label2_list = [modo_nuevo] * 8
    c2_list = compute_c_pd_new_mode()
    tc2_list = compute_tc_pd_new_mode(modo_nuevo, nivels_rail, nivels_proy)
    tv2_list = compute_tv_pd_new_mode(modo_nuevo, nivels_rail, nivels_proy)
    te2_list = compute_te_pd_new_mode(modo_nuevo)

    df_dict = {
        "tj": tj_list,
        "block": block_list,
        "label1": label1_list,
        "c1": c1_list,
        "tv1": tv1_list,
        "tc1": tc1_list,
        "te1": te1_list,
        "label2": label2_list,
        "c2": c2_list,
        "tv2": tv2_list,
        "tc2": tc2_list,
        "te2": te2_list
    }

    df = pd.DataFrame(df_dict)
    df.set_index("tj", inplace=True)

    df_modified = apply_deltas_to_choice_set_df(modo_PR, df)
    
    block = random.choice([1,2])
    df_block = df_modified[df_modified["block"] == block].copy()

    return df_block

def apply_deltas_to_choice_set_df(modo_PR, df):

    df_modified = df.copy()

    delta_c = pd.Series([0,50,20,0]*2, index=df.index) 
    delta_tv = pd.Series([0,1,2]*2 + [0,1], index=df.index) 
    delta_tc = pd.Series([0,1]*4, index=df.index)
    delta_te = pd.Series([1,0]*4, index=df.index)

    delta_c = pd.Series([0]*8, index=df.index) 
    delta_tv = pd.Series([0]*8 , index=df.index) 
    delta_tc = pd.Series([0]*8, index=df.index)
    delta_te = pd.Series([0]*8, index=df.index)


    df_modified["c1"] = df_modified["c1"] + delta_c
    df_modified["tv1"] = df_modified["tv1"] + delta_tv
    df_modified["tc1"] = df_modified["tc1"] + delta_tc
    df_modified["te1"] = df_modified["te1"] + delta_te if modo_PR != "Auto Particular" else df_modified["te1"]

    #df_modified["c2"] = df_modified["c2"] + delta_c
    df_modified["tv2"] = df_modified["tv2"] + delta_tv
    df_modified["tc2"] = df_modified["tc2"] + delta_tc
    df_modified["te2"] = df_modified["te2"] + delta_te if modo_PR != "Auto Particular" else df_modified["te2"]

    return df_modified

def compute_differences(df):
    df_diff = pd.DataFrame()
    #df_diff['delta_c'] = df['c2'] - df['c1']
    df_diff['delta_tv'] = df['tv2'] - df['tv1']
    df_diff['delta_tc'] = df['tc2'] - df['tc1']
    df_diff['delta_te'] = df['te2'] - df['te1']
    return df_diff