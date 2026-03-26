"""
matching_nombre_completo.py
============================
Matching callejero → figuras políticas usando SOLO nombres completos.
No se acepta ningún match por apellido solo.

Lógica:
  - Por cada figura del diccionario, generamos su nombre normalizado completo.
  - Una calle matchea si su nombre normalizado CONTIENE ese nombre completo.
  - Mínimo 2 tokens en el nombre de la figura para aceptarlo.
  - No hay fuzzy. Solo exact substring match.

Resultado: menos calles, pero cada match es confiable.

Requiere: pip install pandas unidecode openpyxl
"""

import re
import pandas as pd
from unidecode import unidecode
from pathlib import Path

CALLEJERO_PATH = r"data/callejero_caba.xlsx"
FIGURAS_PATH   = r"data/figuras_con_partido.csv"
PROCERES_PATH  = r"data/figuras_proceres.csv"
OUT_DIR        = Path(".")

# Tokens a eliminar en cualquier posición del nombre (globales, sin anclas)
TOKENS_ELIMINAR = re.compile(
    r"\b(AV|AVDA|AVENIDA|AUTOPISTA|COLECTORA|PJE|PASAJE|BLVD|DIAGONAL"
    r"|GRAL|GENERAL|COMOD|COMODORO|CNEL|CORONEL|TTE|TENIENTE"
    r"|SGTO|SARGENTO|CAP|CAPITAN|DR|DOCTOR|PDTE|PRESIDENTE|PRES"
    r"|ING|INGENIERO|INT|INTENDENTE|LIC|LICENCIADO)\.?"
    r"(?=\s|$)",
    re.IGNORECASE
)

# ---------------------------------------------------------------------------
# NORMALIZACIÓN
# ---------------------------------------------------------------------------

def normalizar(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    s = texto.upper().strip()
    s = unidecode(s)

    # Reordenar "APELLIDO, NOMBRE" → "NOMBRE APELLIDO" (antes de limpiar tokens)
    if "," in s:
        partes = [p.strip() for p in s.split(",", 1)]
        s = " ".join(reversed(partes))

    # Eliminar títulos y tipos de vía en cualquier posición
    s = TOKENS_ELIMINAR.sub(" ", s)

    # Eliminar comas residuales y espacios múltiples
    s = s.replace(",", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---------------------------------------------------------------------------
# CONSTRUIR CANDIDATOS
# ---------------------------------------------------------------------------

def construir_candidatos(df: pd.DataFrame) -> list[dict]:
    """
    Por cada figura genera todas sus variantes de nombre completo (≥2 tokens).
    Descarta cualquier variante de un solo token (apellido solo).
    """
    candidatos = []
    for _, row in df.iterrows():
        variantes = set()

        nombre_norm = normalizar(row["nombre"])
        if nombre_norm and len(nombre_norm.split()) >= 2:
            variantes.add(nombre_norm)

        # Aliases del campo aliases (pipe-separated)
        aliases_raw = str(row.get("aliases", "") or "")
        for alias in aliases_raw.split("|"):
            a = normalizar(alias.strip())
            if a and len(a.split()) >= 2:
                variantes.add(a)

        for v in variantes:
            candidatos.append({
                "variante":      v,
                "wikidata_id":   row["wikidata_id"],
                "figura_nombre": row["nombre"],
                "partido_madre": row.get("partido_madre", "Prócer"),
                "tipo":          row.get("tipo", ""),
            })

    # Ordenar por longitud descendente: matchear primero el nombre más largo
    # evita que "JOSE MARIA" matchee antes que "JOSE MARIA ROSA COMPLETO"
    candidatos.sort(key=lambda c: len(c["variante"]), reverse=True)
    return candidatos


# ---------------------------------------------------------------------------
# MATCHING
# ---------------------------------------------------------------------------

def match_calle(nombre_norm: str, candidatos: list[dict]) -> dict | None:
    """
    Recorre candidatos (ordenados por longitud desc) y devuelve el primero
    cuya variante esté contenida en el nombre de la calle.
    Esto garantiza que matchea el nombre más específico posible.
    """
    for c in candidatos:
        if c["variante"] in nombre_norm:
            return c
    return None

# ---------------------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------------------

def main():
    print("[1/4] Cargando datos...")
    df_cal  = pd.read_excel(CALLEJERO_PATH)
    df_fig  = pd.read_csv(FIGURAS_PATH,  encoding="utf-8-sig")
    df_proc = pd.read_csv(PROCERES_PATH, encoding="utf-8-sig")

    def agg(df):
        return (
            df.groupby("wikidata_id")
            .agg(
                nombre=("nombre", "first"),
                partido_madre=("partido_madre", "first"),
                tipo=("tipo", "first"),
                aliases=("alias", lambda x: " | ".join(x.dropna().astype(str).unique()))
            )
            .reset_index()
        )

    df_fig_agg  = agg(df_fig)
    df_proc_agg = agg(df_proc)
    df_todas    = pd.concat([df_fig_agg, df_proc_agg], ignore_index=True)

    print(f"    Calles:  {len(df_cal):,}")
    print(f"    Figuras: {len(df_todas):,}")

    print("[2/4] Construyendo candidatos (solo nombres completos ≥2 tokens)...")
    candidatos = construir_candidatos(df_todas)
    print(f"    Variantes únicas: {len(candidatos):,}")

    print("[3/4] Normalizando callejero y matcheando...")
    df_cal["nombre_norm"] = df_cal["nomoficial"].apply(normalizar)

    resultados = []
    for _, row in df_cal.iterrows():
        figura = match_calle(row["nombre_norm"], candidatos)
        resultados.append({
            "id":            row["id"],
            "nomoficial":    row["nomoficial"],
            "nombre_norm":   row["nombre_norm"],
            "barrio":        row.get("barrio", ""),
            "barrio_par":    row.get("barrio_par", ""),
            "barrio_imp":    row.get("barrio_imp", ""),
            "comuna":        row.get("comuna", ""),
            "tipo_c":        row.get("tipo_c", ""),
            "long":          row.get("long", 0),
            "geometry":      row.get("geometry", ""),
            "wikidata_id":   figura["wikidata_id"]   if figura else None,
            "figura_nombre": figura["figura_nombre"] if figura else None,
            "partido_madre": figura["partido_madre"] if figura else None,
            "tipo_figura":   figura["tipo"]          if figura else None,
        })

    print("[4/4] Guardando...")
    df_res   = pd.DataFrame(resultados)
    matched  = df_res[df_res["wikidata_id"].notna()]
    no_match = df_res[df_res["wikidata_id"].isna()]

    matched.to_csv(OUT_DIR  / "callejero_matched.csv",  index=False, encoding="utf-8-sig")
    no_match.to_csv(OUT_DIR / "callejero_no_match.csv", index=False, encoding="utf-8-sig")

    total = len(df_res)
    print("\n====== RESUMEN ======")
    print(f"Total calles:             {total:,}")
    print(f"Calles con figura:        {len(matched):,}  ({100*len(matched)/total:.1f}%)")
    print(f"Sin match:                {len(no_match):,}  ({100*len(no_match)/total:.1f}%)")
    print("\nDistribución partido madre:")
    print(matched["partido_madre"].value_counts().to_string())
    print("\nTop 20 figuras más frecuentes en calles:")
    print(matched["figura_nombre"].value_counts().head(20).to_string())
    print("\nSpot-check — 10 matches random:")
    print(
        matched[["nomoficial", "figura_nombre", "partido_madre"]]
        .sample(min(10, len(matched)))
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()