"""
wikidata_figuras_politicas.py
=============================
Descarga figuras políticas argentinas desde Wikidata.
Clasifica por partido madre (PJ, UCR, PRO, PS, etc.)
Separa próceres pre-partido en categoría aparte.

Output:
  - figuras_con_partido.csv   → para análisis correlacional
  - figuras_proceres.csv      → para análisis descriptivo solamente

Requiere: pip install requests pandas
"""

import requests
import pandas as pd
import time
from pathlib import Path

WIKIDATA_URL = "https://query.wikidata.org/sparql"
HEADERS = {
    "User-Agent": "POC-Calles-CABA/1.0 (proyecto-local)",
    "Accept": "application/json"
}

# ---------------------------------------------------------------------------
# MAPEO DE PARTIDO MADRE
# Wikidata devuelve partidos históricos y frentes electorales.
# Este dict los normaliza al partido madre.
# IMPORTANTE: después de la primera corrida, revisá "Sin clasificar"
# en el output y ampliá este dict según lo que aparezca.
# ---------------------------------------------------------------------------

PARTIDO_MADRE = {
    # Peronismo / PJ
    "Partido Justicialista":                    "PJ",
    "Frente para la Victoria":                  "PJ",
    "Unión por la Patria":                      "PJ",
    "Frente de Todos":                          "PJ",
    "Frente Justicialista de Liberación":       "PJ",
    "Partido Laborista":                        "PJ",
    "Partido Único de la Revolución Nacional":  "PJ",
    "Unidad Ciudadana":                          "PJ",
    "Frente Patria Grande":                   "PJ",
    "Partido Peronista Femenino":                   "PJ",
    "Frente Renovador":                   "PJ",
    "Movimiento Popular Neuquino":                   "PJ",
    "peronismo":                   "PJ",
    "Partido de la Concordia Social":                   "PJ",
    "Peronismo Federal":                   "PJ",
    "Juventud Peronista":                   "PJ",







    # Radicalismo / UCR
    "Unión Cívica Radical":                     "UCR",
    "Unión Cívica":                             "Liberalismo",
    "Frente Cívico y Social":                   "UCR",
    "Unión Cívica Radical Intransigente":        "UCR",
    "Coalición Cívica ARI":                   "UCR",
    "Movimiento de Integración y Desarrollo": "UCR",
    "Frente Cívico de Córdoba":                   "UCR",
    "Unión Cívica Nacional":                   "Liberalismo",
    "Unión Cívica Radical del Pueblo":                   "UCR",
    "Unión Cívica Radical Antipersonalista":                   "UCR",
    "Juntos Somos Río Negro":                   "UCR",



    # PRO / Cambiemos / JxC
    "Propuesta Republicana":                    "PRO",
    "Cambiemos":                                "PRO",
    "Juntos por el Cambio":                     "PRO",

    # Socialismo
    "Partido Socialista":                       "PS",
    "Partido Socialista Democrático":           "PS",
    "Partido Socialista Popular":               "PS",
        "Partido Socialista Obrero Español":       "PS",
        "Los Verdes":                            "PS",
        "Partido Social Patagónico":       "PS",
            "Frente País Solidario":                   "PS",
    "Movimiento al Socialismo":                   "PS",
    "Partido de los Trabajadores Socialistas":                   "PS",
    "desarrollismo":                   "PS",
    "Generación para un Encuentro Nacional":                   "PS",
    "Partido Nuevo contra la Corrupción, por la Honestidad y la Transparencia":                   "PS",




    # Liberalismo
    "Partido Autonomista Nacional":             "Liberalismo",
    "Partido Nacional Democrático":             "Liberalismo",
    "Partido Demócrata":                        "Liberalismo",
    "Partido Demócrata Progresista":            "Liberalismo",
    "Partido Demócrata (Argentina)":              "Liberalismo",
    "Acción por la República":                   "Liberalismo",
    "Partido Demócrata Cristiano":                   "Liberalismo",
    "Vox":                   "Liberalismo",
    "Avanza Libertad":                   "Liberalismo",
    "La Libertad Avanza":                   "Liberalismo",
    "Partido Conservador":                   "Liberalismo",
    "Partido Federal":                   "Liberalismo",
    "Recrear para el Crecimiento":                   "Liberalismo",
    "Partido Demócrata Progresista":                   "Liberalismo",
    "Partido Liberal de Corrientes":                   "Liberalismo",
    "Unión del Centro Democrático":                   "Liberalismo",
    "Partido Demócrata de Córdoba":                   "Liberalismo",
    "Partido Demócrata de Mendoza":                   "Liberalismo",
    "Partido Libertario":                   "Liberalismo",


    # Izquierda
    "Partido Comunista de Argentina":           "Izquierda",
    "Partido Obrero":                           "Izquierda",
    "Frente de Izquierda y de los Trabajadores": "Izquierda",
    "Partido Comunista":                      "Izquierda",
    "Frente Grande":                      "PJ",
    "Partido Operário Revolucionário Trotskista": "Izquierda",
    "Partido Colorado":                      "Izquierda",
    "Nuevo Encuentro":                      "Izquierda",
    "Montoneros":                      "Izquierda",
    "Izquierda Socialista":                      "Izquierda",
    "Movimiento Socialista de los Trabajadores":                      "Izquierda",
    "Política Obrera":                      "Izquierda",

    # Gobiernos de facto
    "Proceso de Reorganización Nacional":       "Dictadura",
    "Revolución Libertadora":                   "Dictadura",
    "Revolución Argentina":                     "Dictadura",
    "partido militar":                            "Dictadura",
    "Partido Nazi":                            "Dictadura",
    "político independiente":                            "Dictadura",
    "Alianza Libertadora Nacionalista": "Dictadura",
    "Fuerza Republicana": "Dictadura",

}

# ---------------------------------------------------------------------------
# QUERIES SPARQL
# ---------------------------------------------------------------------------

# Presidentes: Q35715 = presidente de Argentina
QUERY_PRESIDENTES = """
SELECT DISTINCT ?persona ?personaLabel ?alias ?partidoLabel ?inicio ?fin
       (COUNT(DISTINCT ?sitelink) AS ?sitelinks) WHERE {
  ?persona wdt:P39 wd:Q12969145 .
  OPTIONAL { ?persona skos:altLabel ?alias FILTER(LANG(?alias) = "es") }
  OPTIONAL { ?persona wdt:P102 ?partido }
  OPTIONAL {
    ?persona p:P39 ?stmt .
    ?stmt ps:P39 wd:Q12969145 .
    OPTIONAL { ?stmt pq:P580 ?inicio }
    OPTIONAL { ?stmt pq:P582 ?fin }
  }
  OPTIONAL { ?sitelink schema:about ?persona }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en" }
}
GROUP BY ?persona ?personaLabel ?alias ?partidoLabel ?inicio ?fin
ORDER BY ?inicio
"""
 
QUERY_PROCERES = """
SELECT DISTINCT ?persona ?personaLabel ?alias
       (COUNT(DISTINCT ?sitelink) AS ?sitelinks) WHERE {
  ?persona wdt:P27 wd:Q414 .
  ?persona wdt:P31 wd:Q5 .
  {
    ?persona wdt:P106 wd:Q82955 .
  } UNION {
    ?persona wdt:P106 wd:Q47064 .
  } UNION {
    ?persona wdt:P106 wd:Q372436 .
  }
  ?persona wdt:P569 ?nacimiento .
  FILTER(YEAR(?nacimiento) < 1850)
  OPTIONAL { ?persona skos:altLabel ?alias FILTER(LANG(?alias) = "es") }
  OPTIONAL { ?sitelink schema:about ?persona }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en" }
}
GROUP BY ?persona ?personaLabel ?alias
"""
 
QUERY_POLITICOS_XX = """
SELECT DISTINCT ?persona ?personaLabel ?alias ?partidoLabel
       (COUNT(DISTINCT ?sitelink) AS ?sitelinks) WHERE {
  ?persona wdt:P27 wd:Q414 .
  ?persona wdt:P31 wd:Q5 .
  ?persona wdt:P106 wd:Q82955 .
  ?persona wdt:P102 ?partido .
  ?persona wdt:P569 ?nacimiento .
  FILTER(YEAR(?nacimiento) >= 1850)
  OPTIONAL { ?persona skos:altLabel ?alias FILTER(LANG(?alias) = "es") }
  OPTIONAL { ?sitelink schema:about ?persona }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en" }
}
GROUP BY ?persona ?personaLabel ?alias ?partidoLabel
LIMIT 3000
"""

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def fetch_wikidata(query: str, label: str) -> list[dict]:
    print(f"\n[Wikidata] {label}...")
    try:
        r = requests.get(
            WIKIDATA_URL,
            params={"format": "json", "query": query},
            headers=HEADERS,
            timeout=60
        )
        r.raise_for_status()
        results = r.json()["results"]["bindings"]
        print(f"  -> {len(results)} filas")
        return results
    except Exception as e:
        print(f"  ERROR: {e}")
        return []


def bindings_to_df(bindings: list[dict], tipo: str) -> pd.DataFrame:
    rows = []
    for b in bindings:
        rows.append({
            "wikidata_id":    b.get("persona", {}).get("value", "").split("/")[-1],
            "nombre":         b.get("personaLabel", {}).get("value", ""),
            "alias":          b.get("alias", {}).get("value", ""),
            "partido_raw":    b.get("partidoLabel", {}).get("value", ""),
            "inicio_mandato": b.get("inicio", {}).get("value", "")[:4] if b.get("inicio") else "",
            "fin_mandato":    b.get("fin", {}).get("value", "")[:4] if b.get("fin") else "",
            "sitelinks":      int(b.get("sitelinks", {}).get("value", 0)),
            "tipo":           tipo,
        })
    return pd.DataFrame(rows)


def mapear_partido_madre(partido_raw: str) -> str:
    return PARTIDO_MADRE.get(partido_raw, "Sin clasificar" if partido_raw else "")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    out_dir = Path(".")

    # 1. Descargar
    df_pres = bindings_to_df(fetch_wikidata(QUERY_PRESIDENTES,  "Presidentes"), "presidente")
    time.sleep(2)
    df_proc = bindings_to_df(fetch_wikidata(QUERY_PROCERES,     "Próceres pre-1850"), "procer")
    time.sleep(2)
    df_xx   = bindings_to_df(fetch_wikidata(QUERY_POLITICOS_XX, "Políticos s. XX/XXI"), "politico")

    # 2. Consolidar figuras con partido
    df = pd.concat([df_pres, df_xx], ignore_index=True)
    df = df[df["nombre"].str.len() > 0]
    df = df.drop_duplicates(subset=["wikidata_id", "alias"])
    df["partido_madre"] = df["partido_raw"].apply(mapear_partido_madre)

    # 3. Limpiar próceres
    df_proc = df_proc[df_proc["nombre"].str.len() > 0].drop_duplicates(subset=["wikidata_id", "alias"])
    df_proc["partido_madre"] = "Prócer"

    # 4. Excluir IDs de próceres del dataset correlacional
    ids_proceres = set(df_proc["wikidata_id"].unique())
    df = df[~df["wikidata_id"].isin(ids_proceres)]
    df_con_partido = df[df["partido_madre"] != ""].copy()

    # sitelinks máximo por figura (para desambiguación posterior)
    for df_out, fname in [(df_con_partido, "figuras_con_partido.csv"), (df_proc, "figuras_proceres.csv")]:
        sl = df_out.groupby("wikidata_id")["sitelinks"].max().reset_index().rename(columns={"sitelinks":"sitelinks_max"})
        df_out = df_out.merge(sl, on="wikidata_id", how="left")
        df_out.to_csv(out_dir / fname, index=False, encoding="utf-8-sig")
        print(f"[OK] {fname}")
 
    print(f"\nFiguras con partido: {df_con_partido['wikidata_id'].nunique()}")
    print(f"Próceres:            {df_proc['wikidata_id'].nunique()}")

    # 5. Resumen
    print("\n====== RESUMEN ======")
    print(f"Figuras con partido (correlacional): {df_con_partido['wikidata_id'].nunique()}")
    print(f"Próceres (solo descriptivo):         {df_proc['wikidata_id'].nunique()}")
    print("\nDistribución partido madre:")
    print(
        df_con_partido.drop_duplicates("wikidata_id")["partido_madre"]
        .value_counts()
        .to_string()
    )
    print("\nTop 20 'Sin clasificar' (partido_raw sin mapear):")
    sin = (
        df_con_partido[df_con_partido["partido_madre"] == "Sin clasificar"]
        .drop_duplicates("wikidata_id")[["nombre", "partido_raw"]]
        .groupby("partido_raw")
        .size()
        .sort_values(ascending=False)
        .reset_index(name="cantidad")
    )

    print(sin.head(20).to_string(index=False))



if __name__ == "__main__":
    main()