"""
spatial_join.py
===============
- Spatial join calles matcheadas → circuitos electorales
- Agrega metros lineales por (circuito, partido_madre)
- Excluye próceres del denominador de pct_metros
- Merge electoral por partido_electoral (Opción B: UCR+PRO → Centroderecha)
- Controles censales via spatial join radio censal → circuito (no por comuna)
- Output: tabla_analisis.csv

Requiere: pip install pandas geopandas openpyxl shapely
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
from shapely import wkt


OUT_DIR = Path(".")

CALLEJERO_MATCHED   = r"data/callejero_matched.csv"
CIRCUITOS_PATH      = r"data/circuitos_electorales.csv"
CALLEJERO_GEO_PATH  = r"data/callejero_caba.xlsx"
VOTOS_PATH          = r"data/votos_normalizados.csv"
CENSO_NBI_PATH      = r"data/nbi_total_Radio.csv"
CENSO_EDU_PATH      = r"data/nivel_mas_alto_al_que_asistio_Radio.csv"

# Shapefile de radios censales CABA (Censo 2022, INDEC)
# Descargá de: https://www.indec.gob.ar/indec/web/Nivel4-Tema-2-41-165
# (o usá el path que corresponda)
RADIOS_CENSALES_PATH = r"data/radio_censal/cabaxrdatos.shp"

CRS_CALLEJERO = "EPSG:4326"

# ---------------------------------------------------------------------------
# Opción B — mapeo partido_madre (calles) → partido_electoral (votos)
# UCR y PRO comparten bloque electoral porque desde 2015 la UCR no presenta
# candidato presidencial propio.
# ---------------------------------------------------------------------------

PARTIDO_ELECTORAL = {
    "PJ":          "PJ",
    "UCR":         "Centroderecha",
    "PRO":         "Centroderecha",
    "PS":          "PS",
    "Liberalismo": "Liberalismo",
    "Izquierda":   "Izquierda",
}

PESOS_EDU = {
    "PNIV_ASI_Sin instrucción":                                              0,
    "PNIV_ASI_Primario incompleto":                                          1,
    "PNIV_ASI_Primario completo":                                            2,
    "PNIV_ASI_EGB incompleto":                                               2,
    "PNIV_ASI_EGB completo":                                                 3,
    "PNIV_ASI_Secundario incompleto":                                        3,
    "PNIV_ASI_Secundario completo":                                          5,
    "PNIV_ASI_Polimodal incompleto":                                         4,
    "PNIV_ASI_Polimodal completo":                                           5,
    "PNIV_ASI_Terciario no universitario incompleto":                        6,
    "PNIV_ASI_Terciario no universitario completo":                          7,
    "PNIV_ASI_Universitario de grado incompleto":                            7,
    "PNIV_ASI_Universitario de grado completo":                              9,
    "PNIV_ASI_Posgrado (especialización, maestría o doctorado) incompleto":  9,
    "PNIV_ASI_Posgrado (especialización, maestría o doctorado) completo":   10,
}


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def calcular_indice_edu(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in PESOS_EDU if c in df.columns]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    total = df[cols].sum(axis=1)
    ponderado = sum(df[c] * PESOS_EDU[c] for c in cols)

    result = df[["radios", "cod_depto"]].copy()
    result["indice_educacion"] = (ponderado / total.replace(0, 1)).round(2)
    return result


def parse_wkt_safe(g):
    try:
        return wkt.loads(g) if isinstance(g, str) and g.strip() else None
    except Exception:
        return None


def normalizar_circuito(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    if s == "":
        return None
    try:
        return str(int(float(s)))
    except Exception:
        s = s.lstrip("0")
        return s if s != "" else "0"


def normalizar_partido(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return " ".join(s.split()) if s else None


# ---------------------------------------------------------------------------
# CONTROLES CENSALES — spatial join radio censal → circuito
# ---------------------------------------------------------------------------

def incorporar_censo_por_radio(gdf_circuitos, df_nbi_path, df_edu_path, radios_path):
    """
    Hace spatial join de radios censales a circuitos electorales.
    Agrega NBI e índice educativo a nivel circuito (ponderado por población).

    Si el shapefile de radios no existe, retorna None (y el caller usa fallback).

    NOTA sobre codificación: el shapefile de INDEC codifica comunas CABA como
    departamentos 001-015 (secuencial), pero los CSVs censales usan la
    codificación oficial donde cada comuna es múltiplo de 7 (007, 014, ..., 105).
    Convertimos el código del SHP al del censo para poder hacer el merge.
    """
    print("    Intentando spatial join radio censal → circuito...")

    try:
        gdf_radios = gpd.read_file(radios_path)
    except Exception as e:
        print(f"    No se pudo leer shapefile de radios ({e})")
        return None

    # Asegurar mismo CRS
    if gdf_radios.crs != gdf_circuitos.crs:
        gdf_radios = gdf_radios.to_crs(gdf_circuitos.crs)

    # Identificador del radio
    radio_id_col = None
    for candidate in ["link", "REDCODE", "radio_id", "radios", "LINK", "COD_RADIO"]:
        if candidate in gdf_radios.columns:
            radio_id_col = candidate
            break

    if radio_id_col is None:
        print(f"    Columnas disponibles en radios: {gdf_radios.columns.tolist()}")
        print("    No se encontró columna de ID de radio. Agregá el nombre correcto.")
        return None

    print(f"    Columna ID radio: {radio_id_col}")
    print(f"    Radios cargados: {len(gdf_radios)}")

    # Spatial join: asignar cada radio al circuito donde cae su centroide
    # Reproyectar para centroide correcto
    gdf_radios_proj = gdf_radios.to_crs("EPSG:22185")
    centroides = gdf_radios_proj.geometry.centroid.to_crs(CRS_CALLEJERO)

    gdf_radios_pts = gpd.GeoDataFrame(
        gdf_radios.drop(columns=["geometry"]),
        geometry=centroides,
        crs=CRS_CALLEJERO,
    )

    gdf_radio_circ = gpd.sjoin(
        gdf_radios_pts,
        gdf_circuitos[["circuito_geo_id", "geometry"]],
        how="left",
        predicate="within"
    )

    asignados = gdf_radio_circ["circuito_geo_id"].notna().sum()
    print(f"    Radios asignados a circuito: {asignados} / {len(gdf_radio_circ)}")

    # Cargar datos censales
    try:
        df_nbi = pd.read_csv(df_nbi_path, encoding="utf-8-sig", dtype=str)
        df_edu_raw = pd.read_csv(df_edu_path, encoding="utf-8-sig", dtype=str)
    except FileNotFoundError as e:
        print(f"    Archivo censal no encontrado: {e}")
        return None

    df_nbi["HNBI_TOT_Sí"] = pd.to_numeric(df_nbi["HNBI_TOT_Sí"], errors="coerce").fillna(0)
    df_nbi["Total"] = pd.to_numeric(df_nbi["Total"], errors="coerce").fillna(0)

    df_edu_idx = calcular_indice_edu(df_edu_raw)

    # -----------------------------------------------------------------------
    # Convertir radio_key del SHP a la codificación censal
    # SHP: "02001" + fracción + radio (depto secuencial 001-015)
    # CSV: "02007" + fracción + radio (depto = comuna * 7)
    # Conversión: extraer depto del SHP (posiciones 2:5), multiplicar por 7,
    # reensamblar con el mismo sufijo de fracción+radio
    # -----------------------------------------------------------------------
    def shp_to_censo_key(link: str) -> str:
        """Convierte código de radio del SHP al formato censal."""
        if not isinstance(link, str) or len(link) < 5:
            return link
        prov = link[:2]              # "02"
        depto_shp = int(link[2:5])   # 1-15
        sufijo = link[5:]            # fracción + radio (ej: "0302")
        depto_censo = depto_shp * 7  # 7, 14, 21, ..., 105
        return f"{prov}{depto_censo:03d}{sufijo}"

    gdf_radio_circ["radio_key"] = (
        gdf_radio_circ[radio_id_col].astype(str).str.strip().apply(shp_to_censo_key)
    )
    df_nbi["radio_key"] = df_nbi["radios"].astype(str).str.strip()
    df_edu_idx["radio_key"] = df_edu_idx["radios"].astype(str).str.strip()

    # Diagnóstico de match
    set_shp = set(gdf_radio_circ["radio_key"])
    set_nbi = set(df_nbi["radio_key"])
    set_edu = set(df_edu_idx["radio_key"])
    print(f"    Keys SHP (convertidas): {len(set_shp)}, NBI: {len(set_nbi)}, EDU: {len(set_edu)}")
    print(f"    Intersección SHP∩NBI: {len(set_shp & set_nbi)}")
    print(f"    Intersección SHP∩EDU: {len(set_shp & set_edu)}")

    df_merged = gdf_radio_circ[["radio_key", "circuito_geo_id"]].merge(
        df_nbi[["radio_key", "HNBI_TOT_Sí", "Total"]],
        on="radio_key", how="left"
    ).merge(
        df_edu_idx[["radio_key", "indice_educacion"]],
        on="radio_key", how="left"
    )

    n_nbi = df_merged["HNBI_TOT_Sí"].notna().sum()
    n_edu = df_merged["indice_educacion"].notna().sum()
    print(f"    Radios con NBI tras merge: {n_nbi} / {len(df_merged)}")
    print(f"    Radios con EDU tras merge: {n_edu} / {len(df_merged)}")

    # Agregar a nivel circuito
    circ_censo = (
        df_merged
        .groupby("circuito_geo_id")
        .agg(
            nbi_si=("HNBI_TOT_Sí", "sum"),
            nbi_total=("Total", "sum"),
            indice_edu_circuito=("indice_educacion", "mean"),
        )
        .reset_index()
    )
    circ_censo["tasa_nbi_circuito"] = (
        circ_censo["nbi_si"] / circ_censo["nbi_total"].replace(0, 1) * 100
    ).round(2)
    circ_censo["indice_edu_circuito"] = circ_censo["indice_edu_circuito"].round(2)

    n_con_nbi = circ_censo["tasa_nbi_circuito"].notna().sum()
    print(f"    Circuitos con NBI: {n_con_nbi}")
    print(f"    Circuitos con edu: {circ_censo['indice_edu_circuito'].notna().sum()}")

    return circ_censo[["circuito_geo_id", "tasa_nbi_circuito", "indice_edu_circuito"]]


def incorporar_censo_por_comuna(df_tabla, df_nbi_path, df_edu_path, circuitos_path):
    """
    Fallback: controles censales a nivel comuna (15 valores).
    Se usa solo si el spatial join por radio falla.
    """
    print("    Fallback: controles censales a nivel COMUNA (baja granularidad)...")

    try:
        df_nbi = pd.read_csv(df_nbi_path, encoding="utf-8-sig", dtype=str)
        df_edu_raw = pd.read_csv(df_edu_path, encoding="utf-8-sig", dtype=str)
    except FileNotFoundError as e:
        print(f"    Censo no encontrado ({e}), continuando sin controles.")
        return df_tabla

    df_nbi["HNBI_TOT_Sí"] = pd.to_numeric(df_nbi["HNBI_TOT_Sí"], errors="coerce")
    df_nbi["Total"] = pd.to_numeric(df_nbi["Total"], errors="coerce")

    # INDEC codifica comunas de CABA como cod_depto múltiplos de 7:
    # Comuna 1 = 02007, Comuna 2 = 02014, ..., Comuna 15 = 02105
    # Entonces: (cod_depto % 1000) // 7 = número de comuna
    df_nbi["comuna_id"] = (
        df_nbi["cod_depto"].astype(str).str.lstrip("0").astype(int) % 1000 // 7
    ).astype(str)

    df_edu_idx = calcular_indice_edu(df_edu_raw)
    df_edu_idx["comuna_id"] = (
        df_edu_idx["cod_depto"].astype(str).str.lstrip("0").astype(int) % 1000 // 7
    ).astype(str)

    nbi_comuna = (
        df_nbi.groupby("comuna_id")
        .apply(lambda x: x["HNBI_TOT_Sí"].sum() / x["Total"].sum() * 100, include_groups=False)
        .reset_index()
        .rename(columns={0: "tasa_nbi_circuito"})  # misma columna para consistencia
    )

    edu_comuna = (
        df_edu_idx.groupby("comuna_id")["indice_educacion"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"indice_educacion": "indice_edu_circuito"})
    )

    df_circ_comuna = pd.read_csv(circuitos_path, encoding="utf-8-sig", dtype=str)[["CIRCUITO_N", "COMUNA"]]
    df_circ_comuna["circ_key"] = df_circ_comuna["CIRCUITO_N"].apply(normalizar_circuito)
    df_circ_comuna["comuna_key"] = df_circ_comuna["COMUNA"].astype(str).str.strip().str.lstrip("0")

    df_tabla = df_tabla.merge(df_circ_comuna[["circ_key", "comuna_key"]], on="circ_key", how="left")
    df_tabla = df_tabla.merge(nbi_comuna, left_on="comuna_key", right_on="comuna_id", how="left")
    df_tabla = df_tabla.merge(edu_comuna, left_on="comuna_key", right_on="comuna_id", how="left")
    df_tabla = df_tabla.drop(columns=["comuna_key", "comuna_id_x", "comuna_id_y"], errors="ignore")

    print("    Controles del censo incorporados (nivel COMUNA — baja granularidad).")
    return df_tabla


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("[1/7] Cargando datos...")

    df_matched = pd.read_csv(CALLEJERO_MATCHED, encoding="utf-8-sig")
    df_matched = df_matched[df_matched["partido_madre"].notna()].copy()
    df_matched["partido_madre"] = df_matched["partido_madre"].apply(normalizar_partido)

    print("    Leyendo geometrías del Excel original...")
    df_geo_raw = pd.read_excel(CALLEJERO_GEO_PATH, usecols=["id", "geometry", "long"])

    df_matched = df_matched.drop(columns=["geometry", "long"], errors="ignore")
    df_matched = df_matched.merge(df_geo_raw, on="id", how="left")

    n_total = len(df_matched)
    n_str = df_matched["geometry"].apply(lambda g: isinstance(g, str)).sum()
    sample = df_matched["geometry"].dropna().iloc[0] if n_str > 0 else None

    print(f"    Geometrías string: {n_str} / {n_total}")
    print(f"    Sample WKT (80 chars): {str(sample)[:80] if sample else 'NINGUNA'}")

    df_matched["geometry"] = df_matched["geometry"].apply(parse_wkt_safe)
    n_valid = df_matched["geometry"].notna().sum()
    print(f"    Geometrías válidas: {n_valid} / {n_total}")

    if n_valid == 0:
        raise ValueError(
            "Ninguna geometría válida. Verificá que el Excel tenga columna 'geometry' con WKT tipo LINESTRING."
        )

    gdf_calles = gpd.GeoDataFrame(df_matched, geometry="geometry", crs=CRS_CALLEJERO)
    print(f"    Bounds callejero: {gdf_calles.total_bounds.round(4)}")

    df_circ_raw = pd.read_csv(CIRCUITOS_PATH, encoding="utf-8-sig", dtype=str)
    df_circ_raw["geometry"] = df_circ_raw["WKT"].apply(parse_wkt_safe)

    n_circ_valid = df_circ_raw["geometry"].notna().sum()
    gdf_circuitos = gpd.GeoDataFrame(df_circ_raw, geometry="geometry", crs=CRS_CALLEJERO)

    print(f"    Circuitos válidos:  {n_circ_valid} / {len(df_circ_raw)}")
    print(f"    Bounds circuitos:   {gdf_circuitos.total_bounds.round(4)}")

    gdf_circuitos = gdf_circuitos[["CIRCUITO_N", "COMUNA", "geometry"]].rename(
        columns={"CIRCUITO_N": "circuito_geo_id", "COMUNA": "comuna_circ"}
    )
    print(f"    Sample ids circuito: {gdf_circuitos['circuito_geo_id'].head(5).tolist()}")

    # -----------------------------------------------------------------------
    # [2/7] Spatial join tramos → circuitos (por centroide, sin duplicados)
    # -----------------------------------------------------------------------
    print("[2/7] Spatial join tramos → circuitos (por centroide)...")

    # Reproyectar a CRS proyectado para calcular centroide correctamente
    gdf_calles_proj = gdf_calles.to_crs("EPSG:22185")
    centroides = gdf_calles_proj.geometry.centroid.to_crs(CRS_CALLEJERO)

    # Crear GDF de centroides (sin tocar la columna "geometry" original)
    gdf_centroides = gpd.GeoDataFrame(
        gdf_calles.drop(columns=["geometry"]),
        geometry=centroides,
        crs=CRS_CALLEJERO,
    )

    gdf_joined = gpd.sjoin(
        gdf_centroides,
        gdf_circuitos,
        how="left",
        predicate="within"
    )

    # Restaurar geometría de línea original para cálculos posteriores
    gdf_joined = gdf_joined.drop(columns=["geometry"])
    gdf_joined = gpd.GeoDataFrame(
        gdf_joined,
        geometry=gdf_calles.loc[gdf_joined.index, "geometry"].values,
        crs=CRS_CALLEJERO,
    )

    n_antes = len(gdf_calles[gdf_calles["geometry"].notna()])
    n_despues = len(gdf_joined)
    print(f"    Tramos: {n_antes} -> {n_despues} (dups: {n_despues - n_antes})")

    sin_circ = gdf_joined["circuito_geo_id"].isna().sum()
    print(f"    Sin circuito: {sin_circ} ({100 * sin_circ / len(gdf_joined):.1f}%)")

    # -----------------------------------------------------------------------
    # [3/7] Agregar metros lineales por (circuito, partido_madre)
    #        EXCLUIR PRÓCERES del denominador de pct_metros
    # -----------------------------------------------------------------------
    print("[3/7] Agregando metros lineales (próceres excluidos del denominador)...")

    df_agg = (
        gdf_joined
        .groupby(["circuito_geo_id", "partido_madre"], dropna=True)
        .agg(metros_lineales=("long", "sum"))
        .reset_index()
    )

    # Denominador: solo partidos políticos (sin próceres, sin Dictadura, sin Sin clasificar)
    partidos_validos = set(PARTIDO_ELECTORAL.keys())
    df_denominador = (
        df_agg[df_agg["partido_madre"].isin(partidos_validos)]
        .groupby("circuito_geo_id")["metros_lineales"]
        .sum()
        .reset_index()
        .rename(columns={"metros_lineales": "total_metros_politicos"})
    )

    df_agg = df_agg.merge(df_denominador, on="circuito_geo_id", how="left")
    df_agg["pct_metros"] = (
        df_agg["metros_lineales"] / df_agg["total_metros_politicos"].replace(0, 1) * 100
    ).round(2)

    # Filtrar: solo partidos con contraparte electoral
    df_agg = df_agg[df_agg["partido_madre"].isin(partidos_validos)].copy()

    # Agregar partido_electoral para el merge con votos
    df_agg["partido_electoral"] = df_agg["partido_madre"].map(PARTIDO_ELECTORAL)

    n_proceres_excl = len(gdf_joined[gdf_joined["partido_madre"] == "Prócer"])
    print(f"    Tramos prócer excluidos: {n_proceres_excl}")
    print(f"    Filas con partidos válidos: {len(df_agg)}")

    # -----------------------------------------------------------------------
    # [4/7] Incorporar datos electorales (por partido_electoral)
    #        Calcula: promedio general (todas las elecciones) + por tipo
    # -----------------------------------------------------------------------
    print("[4/7] Incorporando datos electorales (merge por partido_electoral)...")

    df_votos = pd.read_csv(VOTOS_PATH, encoding="utf-8-sig", dtype=str)
    df_votos["pct_votos"] = pd.to_numeric(df_votos["pct_votos"], errors="coerce")
    df_votos["partido_electoral"] = df_votos["partido_electoral"].apply(normalizar_partido)
    df_votos["anio"] = df_votos["anio"].astype(str).str.strip()
    df_votos["tipo_eleccion"] = df_votos["tipo_eleccion"].astype(str).str.strip()

    # Normalizar circuito
    df_agg["circ_key"] = df_agg["circuito_geo_id"].apply(normalizar_circuito)
    df_votos["circ_key"] = df_votos["circuito_id"].apply(normalizar_circuito)

    # --- Promedio GENERAL (todas las elecciones) ---
    df_votos_gral = (
        df_votos
        .drop_duplicates(subset=["anio", "tipo_eleccion", "circ_key", "partido_electoral"])
        .groupby(["circ_key", "partido_electoral"], dropna=True)
        .agg(pct_votos_promedio=("pct_votos", "mean"))
        .round(2)
        .reset_index()
    )

    # --- Promedios por TIPO DE ELECCIÓN ---
    tipos = df_votos["tipo_eleccion"].unique()
    dfs_tipo = {}
    for tipo in tipos:
        col_name = f"pct_votos_{tipo}"
        df_t = (
            df_votos[df_votos["tipo_eleccion"] == tipo]
            .drop_duplicates(subset=["anio", "circ_key", "partido_electoral"])
            .groupby(["circ_key", "partido_electoral"], dropna=True)
            .agg(**{col_name: ("pct_votos", "mean")})
            .round(2)
            .reset_index()
        )
        dfs_tipo[tipo] = df_t
        print(f"    Tipo '{tipo}': {len(df_t)} filas")

    print(f"    Sample circ_key shapefile: {df_agg['circ_key'].dropna().unique()[:8].tolist()}")
    print(f"    Sample circ_key votos:     {df_votos_gral['circ_key'].dropna().unique()[:8].tolist()}")

    set_agg = set(df_agg["partido_electoral"].dropna().unique())
    set_vot = set(df_votos_gral["partido_electoral"].dropna().unique())
    print(f"    Partidos electorales solo en calles: {sorted(set_agg - set_vot)}")
    print(f"    Partidos electorales solo en votos:  {sorted(set_vot - set_agg)}")

    # Merge: promedio general
    df_tabla = df_agg.merge(
        df_votos_gral[["circ_key", "partido_electoral", "pct_votos_promedio"]],
        on=["circ_key", "partido_electoral"],
        how="left"
    )

    # Merge: promedios por tipo
    for tipo, df_t in dfs_tipo.items():
        col_name = f"pct_votos_{tipo}"
        df_tabla = df_tabla.merge(
            df_t[["circ_key", "partido_electoral", col_name]],
            on=["circ_key", "partido_electoral"],
            how="left"
        )

    match_v = df_tabla["pct_votos_promedio"].notna().sum()
    print(f"    Filas con datos electorales (general): {match_v} / {len(df_tabla)}")

    # -----------------------------------------------------------------------
    # [5/7] Controles censales — intenta por radio, fallback a comuna
    # -----------------------------------------------------------------------
    print("[5/7] Incorporando controles del censo...")

    censo_radio = incorporar_censo_por_radio(
        gdf_circuitos, CENSO_NBI_PATH, CENSO_EDU_PATH, RADIOS_CENSALES_PATH
    )

    if censo_radio is not None:
        df_tabla = df_tabla.merge(censo_radio, on="circuito_geo_id", how="left")
        n_con = df_tabla["tasa_nbi_circuito"].notna().sum()
        print(f"    Controles por RADIO incorporados. Filas con NBI: {n_con} / {len(df_tabla)}")
    else:
        print("    Spatial join por radio falló. Usando fallback por comuna.")
        df_tabla = incorporar_censo_por_comuna(
            df_tabla, CENSO_NBI_PATH, CENSO_EDU_PATH, CIRCUITOS_PATH
        )

    # -----------------------------------------------------------------------
    # [6/7] Calcular área de circuito para densidad absoluta
    # -----------------------------------------------------------------------
    print("[6/7] Calculando área de circuitos (para densidad absoluta)...")

    gdf_circ_proj = gdf_circuitos.to_crs("EPSG:22185")  # POSGAR 2007 faja 5 (Buenos Aires)
    gdf_circ_proj["area_km2"] = (gdf_circ_proj.geometry.area / 1e6).round(4)

    df_areas = gdf_circ_proj[["circuito_geo_id", "area_km2"]].copy()
    df_tabla = df_tabla.merge(df_areas, on="circuito_geo_id", how="left")
    df_tabla["metros_por_km2"] = (df_tabla["metros_lineales"] / df_tabla["area_km2"].replace(0, 1)).round(1)

    # -----------------------------------------------------------------------
    # [7/7] Guardar
    # -----------------------------------------------------------------------
    print("[7/7] Guardando...")

    cols_base = [
        "circuito_geo_id", "partido_madre", "partido_electoral",
        "metros_lineales", "pct_metros", "metros_por_km2", "area_km2",
        "pct_votos_promedio",
    ]
    # Agregar columnas de promedio por tipo dinámicamente
    cols_tipo = [c for c in df_tabla.columns if c.startswith("pct_votos_") and c != "pct_votos_promedio"]
    cols_control = ["tasa_nbi_circuito", "indice_edu_circuito"]

    cols_out = [c for c in cols_base + sorted(cols_tipo) + cols_control if c in df_tabla.columns]

    df_tabla[cols_out].to_csv(
        OUT_DIR / "tabla_analisis.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n[OK] tabla_analisis.csv  ({len(df_tabla):,} filas)")
    print(f"     Circuitos únicos: {df_tabla['circuito_geo_id'].nunique()}")
    print(f"     Partidos (calles): {sorted(df_tabla['partido_madre'].unique())}")
    print(f"     Partidos (electoral): {sorted(df_tabla['partido_electoral'].unique())}")

    print("\nPreview (con votos):")
    preview = df_tabla[cols_out].dropna(subset=["pct_votos_promedio"])
    print(preview.head(10).to_string(index=False) if len(preview) > 0 else "  SIN DATOS — revisá merge")

    # Diagnóstico: partidos sin match electoral
    sin_votos = df_tabla[df_tabla["pct_votos_promedio"].isna()]
    if len(sin_votos) > 0:
        print(f"\n[WARN] {len(sin_votos)} filas sin datos electorales:")
        print(sin_votos.groupby("partido_electoral").size().to_string())


if __name__ == "__main__":
    main()