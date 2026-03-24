"""
analisis_capa4.py
=================
Capa 4 — Análisis estadístico

1. Descriptivo: distribución de figuras por partido/circuito
2. Correlación de Spearman: pct_metros vs pct_votos_promedio por partido
3. Correlación parcial: controlando por tasa_nbi_circuito e indice_edu_circuito
4. Análisis espacial: Moran's I global + LISA para detectar clusters

Requiere: pip install pandas scipy pingouin matplotlib seaborn
Opcional (para Moran's I): pip install libpysal esda geopandas
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

TABLA_PATH = r"data/tabla_analisis.csv"
CIRCUITOS_PATH = r"data/circuitos_electorales.csv"
OUT_DIR = Path("output_capa4")
OUT_DIR.mkdir(exist_ok=True)


def parse_wkt_safe(g):
    from shapely import wkt
    try:
        return wkt.loads(g) if isinstance(g, str) and g.strip() else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 1. DESCRIPTIVO
# ---------------------------------------------------------------------------

def analisis_descriptivo(df):
    print("\n" + "=" * 60)
    print("1. ANÁLISIS DESCRIPTIVO")
    print("=" * 60)

    print("\n--- Filas por partido_madre ---")
    print(df["partido_madre"].value_counts().to_string())

    print("\n--- Circuitos únicos por partido_madre ---")
    print(df.groupby("partido_madre")["circuito_geo_id"].nunique().to_string())

    print("\n--- Estadísticas de pct_metros por partido ---")
    stats_metros = (
        df.groupby("partido_madre")["pct_metros"]
        .describe()
        .round(2)
    )
    print(stats_metros.to_string())

    print("\n--- Estadísticas de pct_votos_promedio por partido_electoral ---")
    stats_votos = (
        df.groupby("partido_electoral")["pct_votos_promedio"]
        .describe()
        .round(2)
    )
    print(stats_votos.to_string())

    print("\n--- Estadísticas de controles censales ---")
    for col in ["tasa_nbi_circuito", "indice_edu_circuito"]:
        if col in df.columns:
            print(f"\n  {col}:")
            print(f"    N válidos: {df[col].notna().sum()}")
            print(f"    Media:     {df[col].mean():.2f}")
            print(f"    Mediana:   {df[col].median():.2f}")
            print(f"    Min-Max:   {df[col].min():.2f} - {df[col].max():.2f}")
            print(f"    Std:       {df[col].std():.2f}")

    return stats_metros


# ---------------------------------------------------------------------------
# 2. CORRELACIÓN DE SPEARMAN (bivariada)
# ---------------------------------------------------------------------------

def correlacion_spearman(df, col_y="pct_votos_promedio", label="general"):
    print(f"\n  --- Spearman bivariado [{label}] (Y = {col_y}) ---")

    resultados = []

    for partido_elec in sorted(df["partido_electoral"].unique()):
        sub = df[df["partido_electoral"] == partido_elec].dropna(
            subset=["pct_metros", col_y]
        )
        n = len(sub)

        if n < 10:
            print(f"  [{partido_elec}] N={n} — insuficiente")
            resultados.append({
                "tipo": label, "partido_electoral": partido_elec,
                "n": n, "rho": np.nan, "p_value": np.nan,
                "significativo_005": False, "nota": "N insuficiente"
            })
            continue

        rho, p = stats.spearmanr(sub["pct_metros"], sub[col_y])

        sig = p < 0.05
        sig_01 = p < 0.01
        partidos_calles = sorted(sub["partido_madre"].unique())
        mag = "débil" if abs(rho) < 0.3 else "moderada" if abs(rho) < 0.5 else "fuerte"
        direccion = "positiva" if rho > 0 else "negativa"

        print(f"  [{partido_elec}] N={n}, rho={rho:.4f}, p={p:.4f} {'***' if sig_01 else '**' if sig else 'ns'} ({direccion} {mag})")

        resultados.append({
            "tipo": label,
            "partido_electoral": partido_elec,
            "partidos_calles": ", ".join(partidos_calles),
            "n": n,
            "rho": round(rho, 4),
            "p_value": round(p, 4),
            "significativo_005": sig,
            "magnitud": mag,
            "direccion": direccion,
        })

    return pd.DataFrame(resultados)


# ---------------------------------------------------------------------------
# 3. CORRELACIÓN PARCIAL (controlando por censo)
# ---------------------------------------------------------------------------

def correlacion_parcial(df, col_y="pct_votos_promedio", label="general"):
    print(f"\n  --- Parcial [{label}] (Y = {col_y}) ---")

    try:
        import pingouin as pg
    except ImportError:
        print("  [SKIP] Instalá pingouin: pip install pingouin")
        return None

    controles = ["tasa_nbi_circuito", "indice_edu_circuito"]
    controles_disponibles = [c for c in controles if c in df.columns and df[c].notna().sum() > 10]

    if not controles_disponibles:
        print("  [SKIP] No hay controles censales disponibles.")
        return None

    resultados = []

    for partido_elec in sorted(df["partido_electoral"].unique()):
        sub = df[df["partido_electoral"] == partido_elec].dropna(
            subset=["pct_metros", col_y] + controles_disponibles
        )
        n = len(sub)

        if n < 15:
            print(f"  [{partido_elec}] N={n} — insuficiente")
            continue

        try:
            result = pg.partial_corr(
                data=sub,
                x="pct_metros",
                y=col_y,
                covar=controles_disponibles,
                method="spearman"
            )

            r = result["r"].values[0]
            p_col = "p-val" if "p-val" in result.columns else "p_val"
            p = result[p_col].values[0]
            sig = p < 0.05

            print(f"  [{partido_elec}] N={n}, r={r:.4f}, p={p:.4f} {'*' if sig else 'ns'}")

            resultados.append({
                "tipo": label,
                "partido_electoral": partido_elec,
                "n": n,
                "r_parcial": round(r, 4),
                "p_value": round(p, 4),
                "significativo_005": sig,
                "controles": ", ".join(controles_disponibles),
            })
        except Exception as e:
            print(f"  [{partido_elec}] Error: {e}")

    return pd.DataFrame(resultados) if resultados else None


# ---------------------------------------------------------------------------
# 4. ANÁLISIS ESPACIAL — Moran's I + LISA
# ---------------------------------------------------------------------------

def analisis_espacial(df):
    print("\n" + "=" * 60)
    print("4. ANÁLISIS ESPACIAL (Moran's I + LISA)")
    print("=" * 60)

    try:
        import geopandas as gpd
        from libpysal.weights import Queen
        from esda.moran import Moran, Moran_Local
    except ImportError:
        print("  [SKIP] Instalá: pip install libpysal esda geopandas")
        return None

    # Cargar geometrías de circuitos
    try:
        df_circ_raw = pd.read_csv(CIRCUITOS_PATH, encoding="utf-8-sig", dtype=str)
        df_circ_raw["geometry"] = df_circ_raw["WKT"].apply(parse_wkt_safe)
        gdf_circ = gpd.GeoDataFrame(df_circ_raw, geometry="geometry", crs="EPSG:4326")
        gdf_circ = gdf_circ[["CIRCUITO_N", "geometry"]].rename(
            columns={"CIRCUITO_N": "circuito_geo_id"}
        )
    except Exception as e:
        print(f"  Error cargando circuitos: {e}")
        return None

    resultados_moran = []

    for partido_elec in sorted(df["partido_electoral"].unique()):
        sub = df[df["partido_electoral"] == partido_elec][
            ["circuito_geo_id", "pct_metros"]
        ].copy()
        sub["circuito_geo_id"] = sub["circuito_geo_id"].astype(str)

        if len(sub) < 20:
            print(f"\n  [{partido_elec}] N={len(sub)} — insuficiente para análisis espacial")
            continue

        # Merge con geometrías
        gdf_circ["circuito_geo_id"] = gdf_circ["circuito_geo_id"].astype(str)
        gdf = gdf_circ.merge(sub, on="circuito_geo_id", how="inner")
        gdf = gdf[gdf["geometry"].notna()].copy()

        if len(gdf) < 20:
            print(f"\n  [{partido_elec}] Solo {len(gdf)} con geometría — insuficiente")
            continue

        print(f"\n  [{partido_elec}] N={len(gdf)}")

        try:
            # Construir pesos espaciales (vecindad Queen)
            w = Queen.from_dataframe(gdf, silence_warnings=True)
            w.transform = "r"  # row-standardize

            # Moran's I global
            y = gdf["pct_metros"].values
            mi = Moran(y, w, two_tailed=True)

            print(f"    Moran's I = {mi.I:.4f}")
            print(f"    E[I]      = {mi.EI:.4f}")
            print(f"    p-value   = {mi.p_sim:.4f} (permutaciones)")
            print(f"    z-score   = {mi.z_sim:.4f}")

            sig = mi.p_sim < 0.05
            if sig:
                tipo = "clustering positivo" if mi.I > 0 else "dispersión"
                print(f"    => Autocorrelación espacial significativa ({tipo})")
            else:
                print(f"    => No hay autocorrelación espacial significativa")

            resultados_moran.append({
                "partido_electoral": partido_elec,
                "n": len(gdf),
                "morans_I": round(mi.I, 4),
                "expected_I": round(mi.EI, 4),
                "p_value": round(mi.p_sim, 4),
                "z_score": round(mi.z_sim, 4),
                "significativo_005": sig,
            })

            # LISA (Local Moran's I)
            lisa = Moran_Local(y, w, seed=42)

            gdf["lisa_I"] = lisa.Is
            gdf["lisa_p"] = lisa.p_sim
            gdf["lisa_q"] = lisa.q  # cuadrante: 1=HH, 2=LH, 3=LL, 4=HL

            # Solo significativos
            gdf["lisa_sig"] = gdf["lisa_p"] < 0.05
            gdf["lisa_cluster"] = "ns"
            cluster_map = {1: "High-High", 2: "Low-High", 3: "Low-Low", 4: "High-Low"}
            mask_sig = gdf["lisa_sig"]
            gdf.loc[mask_sig, "lisa_cluster"] = gdf.loc[mask_sig, "lisa_q"].map(cluster_map)

            n_sig = mask_sig.sum()
            print(f"    LISA: {n_sig} circuitos significativos de {len(gdf)}")
            if n_sig > 0:
                print(gdf[mask_sig]["lisa_cluster"].value_counts().to_string())

            # Guardar LISA
            lisa_out = gdf[["circuito_geo_id", "pct_metros", "lisa_I", "lisa_p", "lisa_cluster"]].copy()
            fname = f"lisa_{partido_elec.lower().replace(' ', '_')}.csv"
            lisa_out.to_csv(OUT_DIR / fname, index=False, encoding="utf-8-sig")

        except Exception as e:
            print(f"    Error: {e}")

    if resultados_moran:
        df_moran = pd.DataFrame(resultados_moran)
        df_moran.to_csv(OUT_DIR / "moran_global.csv", index=False, encoding="utf-8-sig")
        print(f"\n  [OK] Guardado en {OUT_DIR / 'moran_global.csv'}")
        return df_moran
    return None


# ---------------------------------------------------------------------------
# 5. SCATTER PLOTS
# ---------------------------------------------------------------------------

def generar_scatters(df):
    print("\n" + "=" * 60)
    print("5. SCATTER PLOTS")
    print("=" * 60)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("  [SKIP] Instalá: pip install matplotlib seaborn")
        return

    partidos = sorted(df["partido_electoral"].unique())
    n_plots = len(partidos)

    fig, axes = plt.subplots(1, n_plots, figsize=(6 * n_plots, 5), squeeze=False)
    axes = axes[0]

    for i, partido_elec in enumerate(partidos):
        ax = axes[i]
        sub = df[df["partido_electoral"] == partido_elec].dropna(
            subset=["pct_metros", "pct_votos_promedio"]
        )

        if len(sub) < 5:
            ax.set_title(f"{partido_elec}\n(N={len(sub)}, insuficiente)")
            continue

        # Color por partido_madre dentro del bloque electoral
        partidos_madre = sorted(sub["partido_madre"].unique())
        colores = {"UCR": "#E31A1C", "PRO": "#FFD700", "PJ": "#1F78B4",
                    "PS": "#E7298A", "Liberalismo": "#7570B3", "Izquierda": "#D95F02"}

        for pm in partidos_madre:
            mask = sub["partido_madre"] == pm
            ax.scatter(
                sub.loc[mask, "pct_metros"],
                sub.loc[mask, "pct_votos_promedio"],
                label=pm,
                color=colores.get(pm, "#999999"),
                alpha=0.6,
                edgecolors="white",
                s=50,
            )

        # Línea de tendencia (Spearman no es lineal, pero sirve como referencia visual)
        rho, p = stats.spearmanr(sub["pct_metros"], sub["pct_votos_promedio"])
        z = np.polyfit(sub["pct_metros"], sub["pct_votos_promedio"], 1)
        poly = np.poly1d(z)
        x_line = np.linspace(sub["pct_metros"].min(), sub["pct_metros"].max(), 100)
        ax.plot(x_line, poly(x_line), "--", color="gray", alpha=0.5)

        ax.set_xlabel("% metros lineales (calles con figuras del partido)")
        ax.set_ylabel("% votos promedio 2011-2023")
        ax.set_title(f"{partido_elec}\nrho={rho:.3f}, p={p:.4f}, N={len(sub)}")
        ax.legend(fontsize=8)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "scatter_correlacion.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  [OK] Guardado en {OUT_DIR / 'scatter_correlacion.png'}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    print("Cargando tabla de análisis...")
    df = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")

    print(f"  Filas: {len(df)}")
    print(f"  Circuitos: {df['circuito_geo_id'].nunique()}")
    print(f"  Partidos (calles): {sorted(df['partido_madre'].unique())}")
    print(f"  Partidos (electoral): {sorted(df['partido_electoral'].unique())}")

    # Detectar columnas de votos disponibles
    cols_votos = ["pct_votos_promedio"] + sorted(
        [c for c in df.columns if c.startswith("pct_votos_") and c != "pct_votos_promedio"]
    )
    print(f"  Columnas de votos: {cols_votos}")

    # 1. Descriptivo
    analisis_descriptivo(df)

    # 2. Spearman bivariado — por cada tipo de elección
    print("\n" + "=" * 60)
    print("2. CORRELACIÓN DE SPEARMAN (bivariada)")
    print("=" * 60)

    all_spearman = []
    for col in cols_votos:
        label = col.replace("pct_votos_", "")
        res = correlacion_spearman(df, col_y=col, label=label)
        if len(res) > 0:
            all_spearman.append(res)

    if all_spearman:
        df_spearman = pd.concat(all_spearman, ignore_index=True)
        df_spearman.to_csv(OUT_DIR / "spearman_bivariado.csv", index=False, encoding="utf-8-sig")
        print(f"\n  [OK] Guardado en {OUT_DIR / 'spearman_bivariado.csv'}")

    # 3. Correlación parcial — por cada tipo de elección
    print("\n" + "=" * 60)
    print("3. CORRELACIÓN PARCIAL (controlando por NBI y educación)")
    print("=" * 60)

    all_parcial = []
    for col in cols_votos:
        label = col.replace("pct_votos_", "")
        res = correlacion_parcial(df, col_y=col, label=label)
        if res is not None and len(res) > 0:
            all_parcial.append(res)

    if all_parcial:
        df_parcial = pd.concat(all_parcial, ignore_index=True)
        df_parcial.to_csv(OUT_DIR / "spearman_parcial.csv", index=False, encoding="utf-8-sig")
        print(f"\n  [OK] Guardado en {OUT_DIR / 'spearman_parcial.csv'}")

    # 4. Moran's I + LISA (solo sobre pct_metros, no cambia con votos)
    analisis_espacial(df)

    # 5. Scatters (solo promedio general)
    generar_scatters(df)

    print("\n" + "=" * 60)
    print("CAPA 4 COMPLETA")
    print(f"Resultados en: {OUT_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()