import geopandas as gpd
import pandas as pd

def get_sector_from_point(zonas_gdf, punto):
    """
    Retorna el valor de la columna "Sector" del polígono que contiene al punto.
    Retorna None si el punto no está contenido por ningún polígono.
    """
    zonas_containing = zonas_gdf[zonas_gdf.geometry.contains(punto)]
    
    if len(zonas_containing) == 0:
        return None
    
    return zonas_containing.iloc[0]["Sector"]

def get_id_tariff_zone_from_point(zonas_gdf, punto):
    """
    Retorna el valor de la columna "id_zona" del polígono que contiene al punto.
    Retorna None si el punto no está contenido por ningún polígono.
    """
    zonas_containing = zonas_gdf[zonas_gdf.geometry.contains(punto)]
    
    if len(zonas_containing) == 0:
        return None
    
    return zonas_containing.iloc[0]["id"]

def check_OD_validity(origen_lat, origen_lon, destino_lat, destino_lon):

    zonas_gdf = gpd.read_file("data/poligonos/validacion_od.shp")

    origen_gdf = gpd.points_from_xy([origen_lon], [origen_lat], crs="EPSG:4326").to_crs(zonas_gdf.crs)
    destino_gdf = gpd.points_from_xy([destino_lon], [destino_lat], crs="EPSG:4326").to_crs(zonas_gdf.crs)

    origen_zona = get_sector_from_point(zonas_gdf, origen_gdf[0])
    destino_zona = get_sector_from_point(zonas_gdf, destino_gdf[0])

    if origen_zona is None or destino_zona is None:
        return False, origen_zona, destino_zona
    
    else:
        if (origen_zona == "CCP" and destino_zona != "CCP") or (origen_zona != "CCP" and destino_zona == "CCP"):
            return True, origen_zona, destino_zona
        else:
            return False, origen_zona, destino_zona

def identify_tariff_zones(origen_lat, origen_lon, destino_lat, destino_lon):

    zonas_gdf = gpd.read_file("data/poligonos/zonas_tarifarias.shp")

    origen_gdf = gpd.points_from_xy([origen_lon], [origen_lat], crs="EPSG:4326").to_crs(zonas_gdf.crs)
    destino_gdf = gpd.points_from_xy([destino_lon], [destino_lat], crs="EPSG:4326").to_crs(zonas_gdf.crs)

    origen_zona = get_id_tariff_zone_from_point(zonas_gdf, origen_gdf[0])
    destino_zona = get_id_tariff_zone_from_point(zonas_gdf, destino_gdf[0])

    tarifas_df = pd.read_csv("data/Tarifas.csv", sep = ";")
    tarifa = tarifas_df[(tarifas_df["ZT_ORI"] == origen_zona) & (tarifas_df["ZT_DES"] == destino_zona)].iloc[0,2]

    return int(tarifa)