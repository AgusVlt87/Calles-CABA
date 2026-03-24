"""
normalizar_electoral.py
========================
Normaliza los datos electorales de 2011, 2015, 2019, 2023 en un único
DataFrame con schema consistente. Agrega partido_madre por agrupacion.

Output:
  - votos_normalizados.csv  → una fila por (año, circuito, partido_madre)
                              con total de votos positivos y total de mesa

Requiere: pip install pandas
"""

import re
import pandas as pd
from pathlib import Path

OUT_DIR = Path(".")

# ---------------------------------------------------------------------------
# ARCHIVOS — cada entrada tiene (path, tipo_eleccion)
# Ajustá los nombres de archivo si difieren.
# ---------------------------------------------------------------------------

ARCHIVOS = [
    # Presidenciales
    (2023, r"data/elecciones/elecciones_2023.csv",           "presidencial"),
    (2019, r"data/elecciones/elecciones_2019.csv",           "presidencial"),
    (2015, r"data/elecciones/elecciones_2015.csv",           "presidencial"),
    (2011, r"data/elecciones/elecciones_2011.csv",           "presidencial"),
    # Legislativas (diputados nacionales)
    (2025, r"data/elecciones/legislativas_2025.csv",         "legislativa"),
    (2021, r"data/elecciones/legislativas_2021.csv",         "legislativa"),
    (2017, r"data/elecciones/legislativas_2017.csv",         "legislativa"),
    (2013, r"data/elecciones/legislativas_2013.csv",         "legislativa"),
    # Jefe de Gobierno CABA
    (2023, r"data/elecciones/jefe_gobierno_2023.csv",        "jefe_gobierno"),
    (2019, r"data/elecciones/jefe_gobierno_2019.csv",        "jefe_gobierno"),
]

# ---------------------------------------------------------------------------
# MAPEO AGRUPACION → PARTIDO MADRE
# Normalizamos nombres de frentes/alianzas al partido madre.
# Criterio: partido con mayor peso dentro del frente.
# Ampliá si aparecen agrupaciones no mapeadas en el output.
# ---------------------------------------------------------------------------

MAPEO_PARTIDO = {
    # PJ / Kirchnerismo
    "FRENTE PARA LA VICTORIA":              "PJ",
    "ALIANZA FRENTE PARA LA VICTORIA":      "PJ",
    "ALIANZA FRENTE PARA LA VICTORIA":      "PJ",
    "ALIANZA FRENTE PARA LA VICTORIA                                                                     ": "PJ",
    "FRENTE DE TODOS":                      "PJ",
    "UNION POR LA PATRIA":                  "PJ",
    "PARTIDO JUSTICIALISTA":                "PJ",
    "Alianza Frente Popular":             "PJ",
    "ALIANZA FRENTE POPULAR":             "PJ",
    "ALIANZA COMPROMISO FEDERAL":           "PJ",

    "Alianza Frente Popular                                                                               ": "PJ",
    "ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA)": "PJ",
    "ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA)                                                      ": "PJ",
    "ALIANZA COMPROMISO FEDERAL":           "PJ",
    "ALIANZA COMPROMISO FEDERAL                                                                          ": "PJ",
    "Alianza Frente para la Victoria                                                                     ": "PJ",
    "CONSENSO FEDERAL":                      "PJ",

    


    # UCR / Cambiemos / JxC
    "UNION CIVICA RADICAL":                 "UCR",
    "Alianza Unión para el Desarrollo Social": "UCR",
    "Alianza Unión para el Desarrollo Social                                                             ": "UCR",
    "Coalición Cívica - Afirmación para una República Igualitaria ARI": "UCR",
    "Coalición Cívica - Afirmación para una República Igualitaria ARI                                    ": "UCR",
    "CoaliciÃ³n CÃvica - AfirmaciÃ³n para una RepÃºblica Igualitaria ARI": "UCR",
    "CoaliciÃ³n CÃvica - AfirmaciÃ³n para una RepÃºblica Igualitaria ARI                                    ": "UCR",
    "COALICIÓN CÍVICA - AFIRMACIÓN PARA UNA REPÚBLICA IGUALITARIA ARI": "UCR",
    "Alianza UniÃ³n para el Desarrollo Social": "UCR",
    "UCR":                                  "UCR",
    "ALIANZA UNIÓN PARA EL DESARROLLO SOCIAL": "UCR",
    "Alianza UniÃ³n para el Desarrollo Social                                                             ": "UCR",
    
    # UCR
    "UCR": "UCR",
    "EVOLUCION": "UCR",
    "UNEN": "UCR",
    "CIUDADANOS UNIDOS": "UCR",


    # PRO solo
    "PROPUESTA REPUBLICANA":                "PRO",
    "PRO":                                  "PRO",
    "ALIANZA CAMBIEMOS                                                                                   ": "PRO",
        "CAMBIEMOS":                            "PRO",   
    "JUNTOS POR EL CAMBIO":                 "PRO",
    "ALIANZA CAMBIEMOS":                    "PRO",
    "ALIANZA JUNTOS POR EL CAMBIO":         "PRO",

    
    # PRO
    "ALIANZA CAMBIEMOS": "PRO",
    "JUNTOS POR EL CAMBIO": "PRO",
    "VAMOS JUNTOS": "PRO",
    "UNION PRO": "PRO",
    "HAGAMOS FUTURO": "PRO",

    # La Libertad Avanza
    "LA LIBERTAD AVANZA":                   "Liberalismo",
    "ALIANZA LA LIBERTAD AVANZA":           "Liberalismo",
    "UNITE POR LA LIBERTAD Y LA DIGNIDAD": "Liberalismo",
    "Frente NOS": "Liberalismo",
    "FRENTE NOS": "Liberalismo",
    "UNIÓN DEL CENTRO DEMOCRÁTICO": "Liberalismo",
    "UNIÃN DEL CENTRO DEMOCRÃTICO": "Liberalismo",
    "UNIÓN DEL CENTRO DEMOCRÁTICO": "Liberalismo",

    # Socialismo / izquierda
    "FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "Izquierda",
    "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES                                                   ": "Izquierda",
    "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES                                                                ": "Izquierda",
    "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "Izquierda",
    "Alianza Frente de Izquierda y de los Trabajadores                                                   ": "Izquierda",
    "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "Izquierda",
    "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "Izquierda",
    "PARTIDO SOCIALISTA":                   "PS",
    "Alianza Frente Amplio Progresista":   "PS",
    "ALIANZA FRENTE AMPLIO PROGRESISTA":   "PS",
    "Alianza Frente Amplio Progresista                                                                   ": "PS",
    "ALIANZA PROGRESISTAS":                 "PS",
    "ALIANZA PROGRESISTAS                                                                                ": "PS",

    "HACEMOS POR NUESTRO PAIS": "PS",

    "UNDEFINED": "En Blanco / Nulo",
    "UNDEFINED": "En Blanco / Nulo",


        # IZQUIERDA
    "ALIANZA FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "Izquierda",
    "FRENTE DE IZQUIERDA Y DE LOS TRABAJADORES": "Izquierda",
    "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "Izquierda",
    "FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD": "Izquierda",
    "LA IZQUIERDA EN LA CIUDAD": "Izquierda",
    "PARTIDO COMUNISTA": "Izquierda",
    "INSTRUMENTO ELECTORAL POR LA UNIDAD POPULAR": "Izquierda",
    "AUTODETERMINACION Y LIBERTAD": "Izquierda",
    "AUTODETERMINACIÃN Y LIBERTAD": "Izquierda",
    "AUTODETERMINACIÓN Y LIBERTAD": "Izquierda",


    # PS
    "ALIANZA FRENTE AMPLIO PROGRESISTA": "PS",
    "ALIANZA PROGRESISTAS": "PS",
    "FRENTE AMPLIO PROGRESISTA": "PS",
    "CAMINO POPULAR": "PS",
    "PARTIDO SOCIALISTA AUTENTICO": "PS",
    "GEN": "PS",

    # LIBERALISMO
    "LA LIBERTAD AVANZA": "Liberalismo",
    "ALIANZA LA LIBERTAD AVANZA": "Liberalismo",
    "UNITE POR LA LIBERTAD Y LA DIGNIDAD": "Liberalismo",
    "UNION DEL CENTRO DEMOCRATICO": "Liberalismo",
    "ALIANZA POTENCIA": "Liberalismo",
    "FRENTE PATRIOTA FEDERAL": "Liberalismo",
    "FRENTE NOS": "Liberalismo",

    # PJ
    "ALIANZA FRENTE PARA LA VICTORIA": "PJ",
    "FRENTE PARA LA VICTORIA": "PJ",
    "FRENTE DE TODOS": "PJ",
    "UNION POR LA PATRIA": "PJ",
    "FUERZA PATRIA": "PJ",
    "HACEMOS POR NUESTRO PAIS": "PJ",
    "COMPROMISO FEDERAL": "PJ",
    "ALIANZA COMPROMISO FEDERAL": "PJ",
    "ALIANZA UNIDOS POR UNA NUEVA ALTERNATIVA (UNA)": "PJ",
    "CONSENSO FEDERAL": "PJ",
    "UNIDAD PORTEÑA": "PJ",
    "AVANCEMOS HACIA 1PAIS MEJOR": "PJ",
    "INTEGRAR": "PJ",
    "FRENTE POPULAR": "PJ",
    "ALIANZA FRENTE POPULAR": "PJ",
    "PARTIDO FEDERAL": "PJ",
    "MOVIMIENTO PLURAL": "PJ",
    "MOVIMIENTO DE JUBILADOS Y JUVENTUD": "PJ",
}

# ---------------------------------------------------------------------------
# OPCIÓN B — PARTIDO ELECTORAL
# UCR y PRO comparten bloque electoral ("Centroderecha") porque desde 2015
# la UCR no presenta candidato presidencial propio.
# El resto se mapea 1:1 desde partido_madre.
# ---------------------------------------------------------------------------

PARTIDO_ELECTORAL = {
    "PJ":          "PJ",
    "UCR":         "Centroderecha",
    "PRO":         "Centroderecha",
    "PS":          "PS",
    "Liberalismo": "Liberalismo",
    "Izquierda":   "Izquierda",
    "Otros":       "Otros",
}


def normalizar_agrupacion(nombre: str) -> str:
    """Normaliza el nombre de la agrupación para el lookup."""
    if not isinstance(nombre, str):
        return ""
    s = nombre.upper().strip()
    s = re.sub(r"\s+", " ", s)
    # Quitar número de alianza al inicio (ej "0131 ALIANZA ..." → "ALIANZA ...")
    s = re.sub(r"^\d+\s+", "", s)
    return s

def mapear_partido(nombre_raw: str) -> str:
    clave = normalizar_agrupacion(nombre_raw)
    # Búsqueda exacta
    if clave in MAPEO_PARTIDO:
        return MAPEO_PARTIDO[clave]
    # Búsqueda parcial (el nombre puede tener sufijos)
    for k, v in MAPEO_PARTIDO.items():
        if k in clave:
            return v
    return "Otros"

# ---------------------------------------------------------------------------
# LECTURA Y NORMALIZACIÓN
# ---------------------------------------------------------------------------

COLS_NECESARIAS = [
    "anio", "seccion_id", "seccion_nombre",
    "circuito_id", "mesa_id", "mesa_electores",
    "votos_tipo", "votos_cantidad", "agrupacion_nombre",
]

def leer_anio(anio: int, path: str, tipo_eleccion: str) -> pd.DataFrame:
    print(f"\n  [{anio} / {tipo_eleccion}] Leyendo {path}...")
    try:
        df = pd.read_csv(path, encoding="latin-1", sep=",", dtype=str)
    except Exception as e:
        print(f"    ERROR: {e}")
        return pd.DataFrame()

    # Normalizar nombres de columnas (quitar espacios, minúsculas)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("ñ", "n", regex=False)
        .str.replace("año", "anio", regex=False)
        .str.replace("ã±o", "anio", regex=False)
    )

    # Renombrar columna año si tiene nombre raro por encoding
    for col in df.columns:
        if col in ("anio", "ano", "a\xf1o") or col.startswith("anio") or col.startswith("ano_"):
            df = df.rename(columns={col: "anio"})
            break

    # Asegurarse de que existe columna anio
    if "anio" not in df.columns:
        df["anio"] = str(anio)

    # Filtrar solo votos positivos (excluye NULO, BLANCO, IMPUGNADO, etc.)
    df["votos_tipo"] = df["votos_tipo"].str.strip().str.upper()
    df = df[df["votos_tipo"] == "POSITIVO"].copy()

    # Filtrar cargo según tipo de elección
    CARGO_FILTRO = {
        "presidencial":  "PRESIDENTE",
        "legislativa":   "DIPUTADO NACIONAL",
        "jefe_gobierno": "JEFE DE GOBIERNO",
    }
    cargo_keyword = CARGO_FILTRO[tipo_eleccion]
    df["cargo_nombre"] = df["cargo_nombre"].str.strip().str.upper()
    df = df[df["cargo_nombre"].str.contains(cargo_keyword, na=False)].copy()

    if len(df) == 0:
        print(f"    WARN: 0 filas tras filtrar cargo '{cargo_keyword}'. Cargos disponibles:")
        print(f"    {df['cargo_nombre'].unique() if 'cargo_nombre' in df.columns else 'N/A'}")

    # Limpiar circuito_id (espacios, ceros leading)
    df["circuito_id"] = df["circuito_id"].str.strip()

    df["votos_cantidad"] = pd.to_numeric(df["votos_cantidad"], errors="coerce").fillna(0)
    df["mesa_electores"] = pd.to_numeric(df["mesa_electores"], errors="coerce").fillna(0)
    df["anio"] = str(anio)
    df["tipo_eleccion"] = tipo_eleccion

    print(f"    Filas positivas: {len(df):,}")
    return df[["anio", "tipo_eleccion", "seccion_id", "seccion_nombre",
               "circuito_id", "mesa_id", "mesa_electores",
               "votos_tipo", "votos_cantidad", "agrupacion_nombre"]]


def main():
    dfs = []
    for anio, path, tipo_eleccion in ARCHIVOS:
        df = leer_anio(anio, path, tipo_eleccion)
        if not df.empty:
            dfs.append(df)

    df_todos = pd.concat(dfs, ignore_index=True)
    df_todos["partido_madre"] = df_todos["agrupacion_nombre"].apply(mapear_partido)
    df_todos["partido_electoral"] = df_todos["partido_madre"].map(PARTIDO_ELECTORAL).fillna("Otros")

    # Resumen de carga
    print(f"\nTotal filas cargadas: {len(df_todos):,}")
    print("\nElecciones por tipo:")
    print(df_todos.groupby("tipo_eleccion")["anio"].nunique().to_string())

    # Revisar qué quedó como "Otros"
    otros = (
        df_todos[df_todos["partido_madre"] == "Otros"]
        ["agrupacion_nombre"]
        .value_counts()
        .head(20)
    )
    print("\nTop 20 agrupaciones mapeadas a 'Otros' (revisá si alguna es importante):")
    print(otros.to_string())

    # -----------------------------------------------------------------------
    # Agregar votos por (año, tipo_eleccion, circuito, partido_electoral)
    # -----------------------------------------------------------------------

    # Primero a nivel partido_madre (para diagnóstico)
    df_circ = (
        df_todos
        .groupby(["anio", "tipo_eleccion", "seccion_id", "seccion_nombre",
                   "circuito_id", "partido_madre", "partido_electoral"])
        .agg(
            votos_positivos=("votos_cantidad", "sum"),
            total_electores=("mesa_electores", "sum"),
        )
        .reset_index()
    )

    # Reagregar a nivel partido_electoral (colapsa UCR+PRO→Centroderecha)
    df_circ_elec = (
        df_circ
        .groupby(["anio", "tipo_eleccion", "seccion_id", "seccion_nombre",
                   "circuito_id", "partido_electoral"])
        .agg(
            votos_positivos=("votos_positivos", "sum"),
            total_electores=("total_electores", "first"),
        )
        .reset_index()
    )

    # Total votos positivos por circuito, año y tipo (para calcular %)
    total_x_circ = (
        df_todos
        .groupby(["anio", "tipo_eleccion", "circuito_id"])["votos_cantidad"]
        .sum()
        .reset_index()
        .rename(columns={"votos_cantidad": "total_votos_positivos"})
    )
    df_circ_elec = df_circ_elec.merge(
        total_x_circ, on=["anio", "tipo_eleccion", "circuito_id"], how="left"
    )
    df_circ_elec["pct_votos"] = (
        df_circ_elec["votos_positivos"] / df_circ_elec["total_votos_positivos"] * 100
    ).round(2)

    df_circ_elec.to_csv(OUT_DIR / "votos_normalizados.csv", index=False, encoding="utf-8-sig")

    print(f"\n[OK] votos_normalizados.csv  ({len(df_circ_elec):,} filas)")
    print("\nDistribución partido_electoral (votos totales):")
    print(
        df_circ_elec.groupby("partido_electoral")["votos_positivos"]
        .sum()
        .sort_values(ascending=False)
        .to_string()
    )
    print("\nElecciones únicas por tipo:")
    resumen = df_circ_elec.groupby("tipo_eleccion").agg(
        anios=("anio", "nunique"),
        filas=("pct_votos", "count"),
    )
    print(resumen.to_string())

    print("\n--- PRÓXIMO PASO ---")
    print("Corrés spatial_join.py (usa partido_electoral para el merge con votos).")


if __name__ == "__main__":
    main()