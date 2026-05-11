"""
wikidata_calles.py
==================
Consulta Wikidata para calles de CABA con propiedad P138 (named after).
Cruza con callejero_caba.xlsx para obtener matches verificados sin depender
de text-matching sobre el nombre de la figura.

Ventaja clave sobre ner.py:
  - Captura calles con apellido solo (RIVADAVIA AV., BELGRANO AV.)
    que el matching de nombre completo no alcanza.
  - Elimina ambigüedad: si Wikidata dice que "Av. Mitre" es por
    Bartolomé Mitre, no hay duda.

Flujo:
  1. Descarga Wikidata: calles en CABA (P131=Q1486) con P138 → persona → partido
  2. Normaliza los labels de calle (mismo criterio que ner.py).
  3. Cruza con callejero_caba.xlsx por nombre normalizado.
  4. Genera callejero_wikidata_match.csv (alta confianza, fuente=wikidata_p138).
  5. Merge con callejero_matched.csv de ner.py:
       - P138 tiene prioridad sobre text-match.
       - Salida: callejero_merged_match.csv, compatible con spatial_join.py.

Requiere: pip install requests pandas unidecode openpyxl
"""

import re
import sys
import time
from pathlib import Path

import urllib3
import pandas as pd
import requests
import warnings
from unidecode import unidecode

# Windows puede interceptar TLS con certificados corporativos que Python no reconoce.
# Para este script de investigación local, deshabilitamos la verificación.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------------------------------------------------------------------------
# REUTILIZAR PARTIDO_MADRE DE wiki.py
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent))
from wiki import PARTIDO_MADRE

# ---------------------------------------------------------------------------
# CONSTANTES
# ---------------------------------------------------------------------------
WIKIDATA_URL    = "https://query.wikidata.org/sparql"
HEADERS         = {
    "User-Agent": "POC-Calles-CABA/1.0 (proyecto-local)",
    "Accept":     "application/json",
}
CALLEJERO_PATH  = Path("data/callejero_caba.xlsx")
TEXT_MATCH_PATH = Path("data/callejero_matched.csv")   # output de ner.py
NO_MATCH_PATH   = Path("data/callejero_no_match.csv")  # output de ner.py
OUT_WIKIDATA    = Path("data/callejero_wikidata_match.csv")
OUT_MERGED      = Path("data/callejero_merged_match.csv")

# ---------------------------------------------------------------------------
# SPARQL — calles de CABA con P138 (named after)
#
# Cobertura doble:
#   - P131 directo a Q1486 (Ciudad Autónoma de Buenos Aires)
#   - P131 a un barrio/comuna que a su vez está en Q1486
#     (algunas calles tienen la división menor como ubicación)
#
# Filtramos ?persona wdt:P31 wd:Q5 para quedarnos solo con personas humanas
# (evita que P138 apunte a eventos, conceptos, etc.)
# ---------------------------------------------------------------------------
QUERY_P138 = """
SELECT DISTINCT ?calle ?calleLabel ?persona ?personaLabel ?partidoLabel WHERE {
  {
    ?calle wdt:P131 wd:Q1486 .
  } UNION {
    ?calle wdt:P131 ?intermedio .
    ?intermedio wdt:P131 wd:Q1486 .
  }
  ?calle wdt:P138 ?persona .
  ?persona wdt:P31 wd:Q5 .
  OPTIONAL { ?persona wdt:P102 ?partido }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en" }
}
ORDER BY ?calleLabel
"""

# ---------------------------------------------------------------------------
# NORMALIZACIÓN — idéntica a ner.py para que los tokens sean comparables
# ---------------------------------------------------------------------------
_TOKENS_ELIMINAR = re.compile(
    r"\b(AV|AVDA|AVENIDA|AUTOPISTA|COLECTORA|PJE|PASAJE|BLVD|DIAGONAL"
    r"|GRAL|GENERAL|COMOD|COMODORO|CNEL|CORONEL|TTE|TENIENTE"
    r"|SGTO|SARGENTO|CAP|CAPITAN|DR|DOCTOR|PDTE|PRESIDENTE|PRES"
    r"|ING|INGENIERO|INT|INTENDENTE|LIC|LICENCIADO)\.?"
    r"(?=\s|$)",
    re.IGNORECASE,
)


def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    s = texto.upper().strip()
    s = unidecode(s)
    if "," in s:
        partes = [p.strip() for p in s.split(",", 1)]
        s = " ".join(reversed(partes))
    s = _TOKENS_ELIMINAR.sub(" ", s)
    s = s.replace(",", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# DESCARGA WIKIDATA
# ---------------------------------------------------------------------------
def fetch_wikidata(query: str) -> list[dict]:
    print("[Wikidata] Consultando calles con P138...")
    try:
        r = requests.get(
            WIKIDATA_URL,
            params={"format": "json", "query": query},
            headers=HEADERS,
            timeout=90,
            verify=False,
        )
        r.raise_for_status()
        results = r.json()["results"]["bindings"]
        print(f"  -> {len(results)} resultados")
        return results
    except Exception as e:
        print(f"  ERROR al consultar Wikidata: {e}")
        return []


def bindings_to_df(bindings: list[dict]) -> pd.DataFrame:
    rows = []
    for b in bindings:
        rows.append({
            "calle_wikidata_id":    b.get("calle", {}).get("value", "").split("/")[-1],
            "calle_wikidata_label": b.get("calleLabel", {}).get("value", ""),
            "persona_wikidata_id":  b.get("persona", {}).get("value", "").split("/")[-1],
            "figura_nombre":        b.get("personaLabel", {}).get("value", ""),
            "partido_raw":          b.get("partidoLabel", {}).get("value", ""),
        })
    df = pd.DataFrame(rows)
    df["partido_madre"] = df["partido_raw"].apply(
        lambda x: PARTIDO_MADRE.get(x, "Sin clasificar" if x else "")
    )
    # Normalizar el label de la calle para el cruce
    df["calle_norm"] = df["calle_wikidata_label"].apply(normalizar)
    return df


# ---------------------------------------------------------------------------
# CRUCE CON CALLEJERO
# Estrategia A (primaria):  exact match en nombre normalizado
#   calle_norm_wikidata == nomoficial_norm_callejero
# Estrategia B (fallback):  substring bidireccional
#   calle_norm_wikidata IN nomoficial_norm  O  nomoficial_norm IN calle_norm_wikidata
#   Solo si el token más corto tiene al menos 2 tokens (evita ruido con nombres simples)
# ---------------------------------------------------------------------------
def cruzar_con_callejero(
    df_wiki: pd.DataFrame, df_cal: pd.DataFrame
) -> pd.DataFrame:
    # Construir lookup de callejero: norm → lista de índices
    cal_index: dict[str, list[int]] = {}
    for idx, row in df_cal.iterrows():
        key = row["nombre_norm"]
        cal_index.setdefault(key, []).append(idx)

    # Desduplicar entradas Wikidata: una fila por (calle_norm, persona)
    # Para una misma calle puede haber múltiples partidos si la persona
    # tuvo varios. Quedamos con el partido de mayor confianza (más matcheos).
    wiki_dedup = (
        df_wiki[df_wiki["calle_norm"].str.len() > 0]
        .drop_duplicates(subset=["calle_norm", "persona_wikidata_id"])
        .copy()
    )

    resultados = []

    for _, wrow in wiki_dedup.iterrows():
        norm = wrow["calle_norm"]
        tokens_wiki = norm.split()

        # ── Estrategia A: exact match ──────────────────────────────────────
        indices_cal = cal_index.get(norm, [])

        # ── Estrategia B: substring bidireccional ──────────────────────────
        if not indices_cal and len(tokens_wiki) >= 2:
            for cal_norm, cal_idxs in cal_index.items():
                tokens_cal = cal_norm.split()
                if len(tokens_cal) < 2:
                    continue
                if norm in cal_norm or cal_norm in norm:
                    indices_cal = cal_idxs
                    break

        for idx in indices_cal:
            cal_row = df_cal.loc[idx]
            resultados.append({
                "id":                  cal_row["id"],
                "nomoficial":          cal_row["nomoficial"],
                "nombre_norm":         cal_row["nombre_norm"],
                "barrio":              cal_row.get("barrio", ""),
                "barrio_par":          cal_row.get("barrio_par", ""),
                "barrio_imp":          cal_row.get("barrio_imp", ""),
                "comuna":              cal_row.get("comuna", ""),
                "tipo_c":              cal_row.get("tipo_c", ""),
                "long":                cal_row.get("long", 0),
                "geometry":            cal_row.get("geometry", ""),
                "wikidata_id":         wrow["persona_wikidata_id"],
                "figura_nombre":       wrow["figura_nombre"],
                "partido_madre":       wrow["partido_madre"],
                "partido_raw":         wrow["partido_raw"],
                "tipo_figura":         "politico",
                "fuente_match":        "wikidata_p138",
                "calle_wikidata_id":   wrow["calle_wikidata_id"],
                "calle_wikidata_label": wrow["calle_wikidata_label"],
            })

    df_out = pd.DataFrame(resultados)

    # Deduplicar por ID de callejero: si el mismo segmento matcheó con varias
    # entradas de Wikidata, conservar solo el match con partido_madre más
    # informativo (orden de prioridad: partido conocido > Sin clasificar > vacío).
    PRIORIDAD_PARTIDO = {
        "UCR":          0,
        "PJ":           0,
        "PRO":          0,
        "PS":           0,
        "Liberalismo":  0,
        "Izquierda":    0,
        "Prócer":       1,
        "Dictadura":    2,
        "Sin clasificar": 3,
        "":             4,
    }
    df_out["_prio"] = df_out["partido_madre"].map(
        lambda p: PRIORIDAD_PARTIDO.get(p, 3)
    )
    df_out = (
        df_out.sort_values("_prio")
        .drop_duplicates(subset=["id"])
        .drop(columns=["_prio"])
        .reset_index(drop=True)
    )
    return df_out


# ---------------------------------------------------------------------------
# MERGE: P138 tiene prioridad; text-match cubre lo que no alcanza Wikidata
# ---------------------------------------------------------------------------
def merge_con_text_match(
    df_p138: pd.DataFrame,
    df_text: pd.DataFrame,
    df_no_match: pd.DataFrame,
) -> pd.DataFrame:
    # IDs de calles ya cubiertas por P138
    ids_p138 = set(df_p138["id"].unique())

    # Del text-match, solo los que NO están en P138
    df_text_extra = df_text[~df_text["id"].isin(ids_p138)].copy()
    df_text_extra["fuente_match"] = "texto"
    df_text_extra["calle_wikidata_id"] = ""
    df_text_extra["calle_wikidata_label"] = ""

    merged = pd.concat([df_p138, df_text_extra], ignore_index=True)
    return merged


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    # 1. Descargar
    bindings = fetch_wikidata(QUERY_P138)
    if not bindings:
        print("Sin resultados de Wikidata. Abortando.")
        return
    time.sleep(1)

    df_wiki = bindings_to_df(bindings)
    print(f"\n[Wikidata] Entidades únicas de calles: {df_wiki['calle_wikidata_id'].nunique()}")
    print(f"[Wikidata] Personas únicas con P138:   {df_wiki['persona_wikidata_id'].nunique()}")
    print("\n[Wikidata] Distribución partido_madre:")
    print(
        df_wiki.drop_duplicates("calle_wikidata_id")["partido_madre"]
        .value_counts()
        .to_string()
    )

    # 2. Cargar callejero y normalizar
    print("\n[Callejero] Cargando...")
    df_cal = pd.read_excel(CALLEJERO_PATH)
    df_cal["nombre_norm"] = df_cal["nomoficial"].apply(normalizar)
    print(f"  -> {len(df_cal):,} segmentos")

    # 3. Cruzar
    print("\n[Cruce] Buscando correspondencias...")
    df_p138 = cruzar_con_callejero(df_wiki, df_cal)
    print(f"  -> {len(df_p138):,} segmentos con match P138")
    print(f"     ({df_p138['id'].nunique():,} IDs únicos, "
          f"{df_p138['figura_nombre'].nunique()} figuras)")

    # 4. Guardar resultado P138 puro
    df_p138.to_csv(OUT_WIKIDATA, index=False, encoding="utf-8-sig")
    print(f"\n[OK] {OUT_WIKIDATA}")

    # 5. Merge con text-match de ner.py
    if TEXT_MATCH_PATH.exists() and NO_MATCH_PATH.exists():
        print("\n[Merge] Combinando P138 + text-match...")
        df_text    = pd.read_csv(TEXT_MATCH_PATH, encoding="utf-8-sig")
        df_no_match = pd.read_csv(NO_MATCH_PATH,  encoding="utf-8-sig")

        df_merged = merge_con_text_match(df_p138, df_text, df_no_match)
        df_merged.to_csv(OUT_MERGED, index=False, encoding="utf-8-sig")
        print(f"[OK] {OUT_MERGED}")

        # Resumen comparativo
        print("\n====== COMPARATIVA ======")
        print(f"{'Fuente':<20} {'Segmentos':>10}  Distribución partido_madre")
        for fuente, grp in df_merged.groupby("fuente_match"):
            dist = grp["partido_madre"].value_counts().to_dict()
            print(f"  {fuente:<18} {len(grp):>10}  {dist}")
    else:
        print(
            "\n[Aviso] No se encontró callejero_matched.csv / callejero_no_match.csv.\n"
            "  Corré primero ner.py para generar el text-match, o usá solo\n"
            f"  {OUT_WIKIDATA} como fuente de alta confianza."
        )

    # 6. Resumen final P138
    print("\n====== RESUMEN P138 ======")
    pm = df_p138["partido_madre"].value_counts()
    print(pm.to_string())
    print(f"\nTop figuras (P138):")
    print(
        df_p138.drop_duplicates("id")
        .groupby("figura_nombre")["id"]
        .count()
        .sort_values(ascending=False)
        .head(20)
        .to_string()
    )
    sin_partido = df_p138[df_p138["partido_madre"].isin(["Sin clasificar", ""])]
    if len(sin_partido):
        print(f"\n[Aviso] {sin_partido['figura_nombre'].nunique()} figuras sin partido_madre mapeado.")
        print("  Revisá PARTIDO_MADRE en wiki.py para:")
        print(
            sin_partido.drop_duplicates("figura_nombre")[["figura_nombre", "partido_raw"]]
            .head(15)
            .to_string(index=False)
        )


if __name__ == "__main__":
    main()
