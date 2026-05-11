"""
visualizaciones_paper.py
========================
Genera todas las figuras para el paper:
  Fig 1 — Geografía política de CABA por nombres de calle
  Fig 2 — Efecto PJ: presencia binaria + mapa de circuitos
  Fig 3 — Consistencia temporal del efecto PJ (2011-2025)
  Fig 4 — Clustering espacial LISA (Centroderecha y PJ)
  Fig 5 — Distribución de figuras por partido

Requiere: pip install geopandas matplotlib seaborn pandas shapely
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from shapely import wkt

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import TwoSlopeNorm, LinearSegmentedColormap
import matplotlib.ticker as mticker
import geopandas as gpd
import seaborn as sns

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
CIRCUITOS_PATH  = "data/circuitos_electorales.csv"
TABLA_PATH      = "data/tabla_analisis.csv"
VOTOS_PATH      = "data/votos_normalizados.csv"
MATCHED_PATH    = "data/callejero_matched.csv"
WIKIDATA_PATH   = "data/callejero_wikidata_match.csv"
LISA_DIR        = Path("output_capa4")
OUT_DIR         = Path("output_paper")
OUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# PALETA — colores consistentes con identidad partidaria argentina
# ---------------------------------------------------------------------------
PALETA = {
    "PJ":           "#1B4F9C",   # azul peronista
    "UCR":          "#C0392B",   # rojo radical
    "Centroderecha":"#C0392B",
    "PRO":          "#FFD600",
    "Liberalismo":  "#C9891E",   # dorado liberal
    "PS":           "#8E44AD",   # violeta socialista
    "Izquierda":    "#27AE60",
    "sin_data":     "#D5D8DC",
    "HH":           "#C0392B",
    "LL":           "#2980B9",
    "HL":           "#E67E22",
    "LH":           "#76D7C4",
    "ns":           "#EAECEE",
}

FONT_TITLE  = dict(fontsize=13, fontweight="bold", color="#1A1A1A")
FONT_SUB    = dict(fontsize=10, color="#555555")
FONT_LABEL  = dict(fontsize=9,  color="#333333")
FONT_TICK   = dict(labelsize=8)

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_circuits():
    df = pd.read_csv(CIRCUITOS_PATH, encoding="utf-8-sig", dtype=str)
    df["geometry"] = df["WKT"].apply(
        lambda x: wkt.loads(x) if isinstance(x, str) and x.strip() else None
    )
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")
    gdf["circuito_geo_id"] = gdf["CIRCUITO_N"].astype(str)
    return gdf[["circuito_geo_id", "geometry"]].dropna(subset=["geometry"])


def style_map_ax(ax):
    ax.set_axis_off()
    ax.set_aspect("equal")


def add_scalebar(ax, length_deg=0.05, label="~4 km", x=0.75, y=0.04):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    xpos = x0 + (x1 - x0) * x
    ypos = y0 + (y1 - y0) * y
    ax.plot([xpos, xpos + length_deg], [ypos, ypos],
            color="black", lw=2, transform=ax.transData)
    ax.text(xpos + length_deg / 2, ypos + (y1 - y0) * 0.015,
            label, ha="center", fontsize=7, color="black")


def add_north(ax, x=0.06, y=0.92):
    ax.annotate("N", xy=(x, y), xycoords="axes fraction",
                fontsize=11, ha="center", va="center", fontweight="bold")
    ax.annotate("▲", xy=(x, y - 0.06), xycoords="axes fraction",
                fontsize=14, ha="center", va="center", color="#333")


# ---------------------------------------------------------------------------
# FIGURA 1 — Geografía política: partido dominante en calles por circuito
# ---------------------------------------------------------------------------

def fig1_geografia():
    print("[Fig 1] Geografía política de CABA...")
    gdf = load_circuits()
    tabla = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")

    # Partido con más metros lineales por circuito
    dominant = (
        tabla.loc[tabla.groupby("circuito_geo_id")["metros_lineales"].idxmax()]
        [["circuito_geo_id", "partido_madre", "metros_lineales", "pct_metros"]]
    )
    dominant["circuito_geo_id"] = dominant["circuito_geo_id"].astype(str)
    gdf = gdf.merge(dominant, on="circuito_geo_id", how="left")
    gdf["partido_plot"] = gdf["partido_madre"].fillna("sin_data")

    fig, ax = plt.subplots(figsize=(8, 9), facecolor="white")
    style_map_ax(ax)

    # Dibujar circuitos sin datos primero
    sin = gdf[gdf["partido_plot"] == "sin_data"]
    if len(sin):
        sin.plot(ax=ax, color=PALETA["sin_data"], linewidth=0.3, edgecolor="white")

    orden = ["UCR", "Liberalismo", "PJ", "PS", "PRO"]
    for p in orden:
        sub = gdf[gdf["partido_plot"] == p]
        if not len(sub):
            continue
        sub.plot(ax=ax, color=PALETA[p], linewidth=0.3, edgecolor="white", alpha=0.9)

    # Leyenda
    handles = [
        mpatches.Patch(color=PALETA[p], label=p)
        for p in orden if len(gdf[gdf["partido_plot"] == p])
    ]
    handles.append(mpatches.Patch(color=PALETA["sin_data"], label="Sin calles políticas"))
    ax.legend(handles=handles, loc="lower left", fontsize=9,
              framealpha=0.9, edgecolor="#CCC", title="Partido dominante\n(por metros lineales)")

    add_north(ax)
    add_scalebar(ax)

    ax.set_title("Figura 1 — Partido dominante en nomenclatura por circuito electoral\n"
                 "Ciudad Autónoma de Buenos Aires",
                 **FONT_TITLE, pad=12)
    ax.text(0.5, -0.01,
            "Nota: cada circuito se colorea según el partido con más metros lineales de calles con figuras políticas.",
            transform=ax.transAxes, ha="center", **FONT_SUB)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig1_geografia_politica.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig1_geografia_politica.png")


# ---------------------------------------------------------------------------
# FIGURA 2 — Efecto PJ: mapa de circuitos + violín por elección
# ---------------------------------------------------------------------------

def fig2_efecto_pj():
    print("[Fig 2] Efecto PJ binario...")
    gdf = load_circuits()
    tabla = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")
    votos = pd.read_csv(VOTOS_PATH, encoding="utf-8-sig")

    circ_pj = set(tabla[tabla["partido_madre"] == "PJ"]["circuito_geo_id"].astype(str))
    gdf["es_pj"] = gdf["circuito_geo_id"].isin(circ_pj)

    # Votos PJ promedio por circuito
    voto_pj = (votos[votos["partido_electoral"] == "PJ"]
               .groupby("circuito_id")["pct_votos"].mean().reset_index()
               .rename(columns={"circuito_id": "circuito_geo_id", "pct_votos": "voto_pj"}))
    voto_pj["circuito_geo_id"] = voto_pj["circuito_geo_id"].astype(str)
    gdf = gdf.merge(voto_pj, on="circuito_geo_id", how="left")

    fig = plt.figure(figsize=(14, 7), facecolor="white")
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1.5], wspace=0.06)

    # ── Panel izquierdo: mapa ──────────────────────────────────────────────
    ax_map = fig.add_subplot(gs[0])
    style_map_ax(ax_map)

    # Fondo: todos los circuitos con % voto PJ (cloroplético)
    gdf_valid = gdf[gdf["voto_pj"].notna()].copy()
    gdf_na    = gdf[gdf["voto_pj"].isna()]
    if len(gdf_na):
        gdf_na.plot(ax=ax_map, color="#EAECEE", linewidth=0.2, edgecolor="white")

    norm = TwoSlopeNorm(vmin=gdf_valid["voto_pj"].min(),
                        vcenter=gdf_valid["voto_pj"].mean(),
                        vmax=gdf_valid["voto_pj"].max())
    cmap_pj = LinearSegmentedColormap.from_list("pj", ["#D6EAF8", "#5DADE2", "#1B4F9C"])
    gdf_valid.plot(ax=ax_map, column="voto_pj", cmap=cmap_pj, norm=norm,
                   linewidth=0.2, edgecolor="white")

    # Borde grueso sobre los 23 circuitos PJ
    gdf[gdf["es_pj"]].plot(ax=ax_map, facecolor="none",
                            edgecolor="#E8B000", linewidth=1.6)

    sm = plt.cm.ScalarMappable(cmap=cmap_pj, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax_map, orientation="horizontal",
                        fraction=0.046, pad=0.02, shrink=0.8)
    cbar.set_label("% voto PJ (promedio 2011-2025)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    pj_patch = mpatches.Patch(facecolor="none", edgecolor="#E8B000",
                               linewidth=2, label="Circuitos con calles PJ (N=23)")
    ax_map.legend(handles=[pj_patch], loc="lower left", fontsize=8,
                  framealpha=0.9, edgecolor="#CCC")
    add_north(ax_map)
    ax_map.set_title("% voto PJ promedio y circuitos\ncon calles peronistas",
                     **FONT_TITLE, pad=8)

    # ── Panel derecho: violin por categoría ──────────────────────────────
    ax_vio = fig.add_subplot(gs[1])

    vp = (votos[votos["partido_electoral"] == "PJ"]
          .rename(columns={"circuito_id": "cid"})
          .copy())
    vp["cid"] = vp["cid"].astype(str)
    vp["Grupo"] = vp["cid"].apply(
        lambda x: "Con calles PJ\n(N=23 circuitos)" if x in circ_pj
        else "Sin calles PJ\n(N=144 circuitos)"
    )

    order = ["Con calles PJ\n(N=23 circuitos)", "Sin calles PJ\n(N=144 circuitos)"]
    pal = {"Con calles PJ\n(N=23 circuitos)": PALETA["PJ"],
           "Sin calles PJ\n(N=144 circuitos)": "#AEB6BF"}

    sns.violinplot(data=vp, x="Grupo", y="pct_votos", order=order,
                   palette=pal, inner="box", linewidth=1.2,
                   cut=0, ax=ax_vio)

    # Medias anotadas
    medias = vp.groupby("Grupo")["pct_votos"].mean()
    for i, g in enumerate(order):
        m = medias[g]
        ax_vio.text(i, m + 1.5, f"{m:.1f}%", ha="center",
                    fontsize=10, fontweight="bold", color="black")

    # Anotación delta
    m_con = medias[order[0]]
    m_sin = medias[order[1]]
    ax_vio.annotate("",
        xy=(1, m_sin), xytext=(0, m_con),
        arrowprops=dict(arrowstyle="<->", color="#E8B000", lw=2))
    ax_vio.text(0.5, (m_con + m_sin) / 2, f"+{m_con - m_sin:.1f}pp",
                ha="center", va="center", fontsize=11, fontweight="bold",
                color="#E8B000",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#E8B000"))

    # p-value
    con_v = vp[vp["Grupo"] == order[0]]["pct_votos"].dropna()
    sin_v = vp[vp["Grupo"] == order[1]]["pct_votos"].dropna()
    _, p = stats.mannwhitneyu(con_v, sin_v, alternative="two-sided")
    ax_vio.set_title(f"Distribución del % voto PJ\npor presencia de calles peronistas\n"
                     f"(Mann-Whitney p = {p:.4f})",
                     **FONT_TITLE, pad=8)
    ax_vio.set_xlabel("", fontsize=10)
    ax_vio.set_ylabel("% votos al PJ (todas las elecciones 2011-2025)", **FONT_LABEL)
    ax_vio.tick_params(**FONT_TICK)
    sns.despine(ax=ax_vio)
    ax_vio.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax_vio.set_axisbelow(True)

    fig.suptitle("Figura 2 — Los circuitos con calles peronistas votan consistentemente\n"
                 "más al PJ en toda la serie electoral",
                 fontsize=13, fontweight="bold", color="#1A1A1A", y=1.01)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig2_efecto_pj.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig2_efecto_pj.png")


# ---------------------------------------------------------------------------
# FIGURA 3 — Consistencia temporal: delta PJ por elección
# ---------------------------------------------------------------------------

def fig3_temporal():
    print("[Fig 3] Consistencia temporal...")
    tabla = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")
    votos = pd.read_csv(VOTOS_PATH, encoding="utf-8-sig")
    circ_pj = set(tabla[tabla["partido_madre"] == "PJ"]["circuito_geo_id"].astype(str))

    rows = []
    for (anio, tipo), grp in votos[votos["partido_electoral"] == "PJ"].groupby(
            ["anio", "tipo_eleccion"]):
        g = grp.copy(); g["cid"] = g["circuito_id"].astype(str)
        con = g[g["cid"].isin(circ_pj)]["pct_votos"].dropna()
        sin = g[~g["cid"].isin(circ_pj)]["pct_votos"].dropna()
        if len(con) < 3 or len(sin) < 3:
            continue
        _, p = stats.mannwhitneyu(con, sin, alternative="two-sided")
        rows.append({"anio": anio, "tipo": tipo,
                     "con": con.mean(), "sin": sin.mean(),
                     "con_se": con.std() / np.sqrt(len(con)),
                     "sin_se": sin.std() / np.sqrt(len(sin)),
                     "delta": con.mean() - sin.mean(), "p": p})

    df_r = pd.DataFrame(rows).sort_values(["anio", "tipo"])
    labels = [f"{int(r.anio)}\n{r.tipo[:4]}." for _, r in df_r.iterrows()]
    x = np.arange(len(df_r))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), facecolor="white",
                                    gridspec_kw={"height_ratios": [2.5, 1],
                                                  "hspace": 0.08})

    # ── Panel superior: líneas con bandas de error ────────────────────────
    ax1.fill_between(x,
                     df_r["con"] - 1.96 * df_r["con_se"],
                     df_r["con"] + 1.96 * df_r["con_se"],
                     alpha=0.15, color=PALETA["PJ"])
    ax1.fill_between(x,
                     df_r["sin"] - 1.96 * df_r["sin_se"],
                     df_r["sin"] + 1.96 * df_r["sin_se"],
                     alpha=0.12, color="#7F8C8D")

    l1, = ax1.plot(x, df_r["con"], "o-", color=PALETA["PJ"],
                   lw=2.2, ms=7, label="Circuitos CON calles PJ (N=23)")
    l2, = ax1.plot(x, df_r["sin"], "s--", color="#7F8C8D",
                   lw=1.8, ms=6, label="Circuitos SIN calles PJ (N=144)")

    # Shading entre líneas
    ax1.fill_between(x, df_r["con"], df_r["sin"],
                     alpha=0.08, color=PALETA["PJ"])

    ax1.set_xticks(x)
    ax1.set_xticklabels([])
    ax1.set_ylabel("% votos al PJ", **FONT_LABEL)
    ax1.tick_params(**FONT_TICK)
    ax1.legend(fontsize=9, loc="upper right", framealpha=0.9)
    ax1.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax1.set_axisbelow(True)
    sns.despine(ax=ax1, bottom=True)
    ax1.set_title("Figura 3 — Consistencia temporal del efecto: circuitos con calles PJ\n"
                  "votan más al PJ en las 10 elecciones (2011-2025)",
                  **FONT_TITLE, pad=10)

    # ── Panel inferior: barras de delta ──────────────────────────────────
    bar_cols = [PALETA["PJ"] if p < 0.05 else "#BDC3C7"
                for p in df_r["p"]]
    bars = ax2.bar(x, df_r["delta"], color=bar_cols, width=0.6,
                   edgecolor="white", linewidth=0.5)

    for i, (bar, row) in enumerate(zip(bars, df_r.itertuples())):
        sig = "***" if row.p < 0.001 else "**" if row.p < 0.01 else "*" if row.p < 0.05 else ""
        ax2.text(i, row.delta + 0.15, sig, ha="center", fontsize=9,
                 color=PALETA["PJ"] if row.p < 0.05 else "#888")
        ax2.text(i, -0.5, f"+{row.delta:.1f}", ha="center", fontsize=7.5,
                 color="#333", va="top")

    ax2.axhline(0, color="#888", lw=0.8)
    ax2.axhline(df_r["delta"].mean(), color=PALETA["PJ"],
                lw=1.2, linestyle=":", alpha=0.7,
                label=f"Media = +{df_r['delta'].mean():.1f}pp")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8)
    ax2.set_ylabel("Δ pp", **FONT_LABEL)
    ax2.set_ylim(-1, df_r["delta"].max() + 1.5)
    ax2.legend(fontsize=8, loc="upper right", framealpha=0.9)
    ax2.tick_params(**FONT_TICK)
    sns.despine(ax=ax2)
    ax2.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax2.set_axisbelow(True)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig3_temporal_pj.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig3_temporal_pj.png")


# ---------------------------------------------------------------------------
# FIGURA 4 — LISA clusters: Centroderecha y PJ
# ---------------------------------------------------------------------------

def fig4_lisa():
    print("[Fig 4] LISA clusters...")
    gdf_base = load_circuits()

    partidos_plot = [
        ("centroderecha", "Centroderecha (UCR)", PALETA["Centroderecha"]),
        ("pj",            "PJ",                  PALETA["PJ"]),
    ]

    cluster_colors = {
        "High-High": PALETA["HH"],
        "Low-Low":   PALETA["LL"],
        "High-Low":  PALETA["HL"],
        "Low-High":  PALETA["LH"],
        "ns":        PALETA["ns"],
    }

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), facecolor="white")

    for ax, (partido_slug, titulo, color_p) in zip(axes, partidos_plot):
        style_map_ax(ax)
        fpath = LISA_DIR / f"lisa_{partido_slug}.csv"
        if not fpath.exists():
            ax.set_title(f"{titulo}\n(sin datos LISA)", **FONT_TITLE)
            continue

        lisa = pd.read_csv(fpath, encoding="utf-8-sig")
        lisa["circuito_geo_id"] = lisa["circuito_geo_id"].astype(str)
        gdf_m = gdf_base.merge(lisa, on="circuito_geo_id", how="left")
        gdf_m["lisa_cluster"] = gdf_m["lisa_cluster"].fillna("ns")

        for cluster, col in cluster_colors.items():
            sub = gdf_m[gdf_m["lisa_cluster"] == cluster]
            if not len(sub):
                continue
            sub.plot(ax=ax, color=col, linewidth=0.25, edgecolor="white", alpha=0.9)

        # Leyenda
        handles = []
        cluster_labels = {
            "High-High": "Alto-Alto (hot spot)",
            "Low-Low":   "Bajo-Bajo (cold spot)",
            "High-Low":  "Alto-Bajo (outlier)",
            "Low-High":  "Bajo-Alto (outlier)",
            "ns":        "No significativo",
        }
        for cl, col in cluster_colors.items():
            n = (gdf_m["lisa_cluster"] == cl).sum()
            if n > 0:
                handles.append(mpatches.Patch(color=col,
                    label=f"{cluster_labels[cl]} (N={n})"))
        ax.legend(handles=handles, loc="lower left", fontsize=7.5,
                  framealpha=0.95, edgecolor="#CCC")

        # pct_metros como círculos proporcionales sobre circuitos sig
        sig = gdf_m[gdf_m["lisa_cluster"] != "ns"].copy()
        if len(sig):
            centroids = sig.geometry.centroid
            sizes = sig["pct_metros"].fillna(0) * 0.8
            ax.scatter(centroids.x, centroids.y, s=sizes, color=color_p,
                       alpha=0.4, linewidths=0, zorder=5)

        add_north(ax)
        ax.set_title(f"LISA — clustering espacial\n% calles {titulo}",
                     **FONT_TITLE, pad=8)

    fig.suptitle("Figura 4 — Autocorrelación espacial local (LISA) de la concentración\n"
                 "de calles políticas por circuito electoral",
                 fontsize=13, fontweight="bold", color="#1A1A1A", y=1.01)
    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig4_lisa.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig4_lisa.png")


# ---------------------------------------------------------------------------
# FIGURA 5 — Distribución de figuras por partido: top figures + por era
# ---------------------------------------------------------------------------

def fig5_figuras():
    print("[Fig 5] Distribución de figuras...")
    matched = pd.read_csv(MATCHED_PATH, encoding="utf-8-sig")
    wm      = pd.read_csv(WIKIDATA_PATH, encoding="utf-8-sig")

    PARTIDOS_VALIDOS = {"UCR", "PJ", "PS", "Liberalismo", "PRO"}
    pol = matched[matched["partido_madre"].isin(PARTIDOS_VALIDOS)].copy()

    LIBERALISMO_XIX = {
        "Partido Unitario", "Partido Autonomista", "Partido Autonomista Nacional",
        "Partido Nacional Democrático", "Partido Liberal", "Partido Republicano",
    }
    wm_lib = wm[wm["partido_madre"] == "Liberalismo"].copy()
    wm_lib["era"] = wm_lib["partido_raw"].apply(
        lambda r: "Liberal XIX" if r in LIBERALISMO_XIX else "Liberal XX"
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="white")

    # ── Panel izq: top 15 figuras por metros lineales ────────────────────
    ax = axes[0]
    top_figs = (pol.groupby(["figura_nombre", "partido_madre"])["long"]
                .sum().reset_index()
                .sort_values("long", ascending=False).head(15))
    top_figs["long_km"] = top_figs["long"] / 1000

    bar_cols = [PALETA.get(p, "#AAA") for p in top_figs["partido_madre"]]
    bars = ax.barh(top_figs["figura_nombre"][::-1],
                   top_figs["long_km"][::-1],
                   color=bar_cols[::-1], edgecolor="white", height=0.7)

    ax.set_xlabel("Kilómetros lineales de calle", **FONT_LABEL)
    ax.set_title("Top 15 figuras políticas\npor kilómetros de calle en CABA",
                 **FONT_TITLE, pad=10)
    ax.tick_params(**FONT_TICK)

    # Mini-leyenda de partidos
    seen = []
    handles = []
    for p, c in PALETA.items():
        if p in PARTIDOS_VALIDOS and p not in seen:
            handles.append(mpatches.Patch(color=c, label=p))
            seen.append(p)
    ax.legend(handles=handles, fontsize=8, loc="lower right",
              framealpha=0.9, edgecolor="#CCC")
    ax.xaxis.grid(True, alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    sns.despine(ax=ax)

    # ── Panel der: distribución metros por partido ────────────────────────
    ax2 = axes[1]
    resumen = (pol.groupby("partido_madre")["long"]
               .sum().reset_index()
               .rename(columns={"long": "metros"}))
    resumen["km"] = resumen["metros"] / 1000
    resumen = resumen.sort_values("km", ascending=False)
    cols2 = [PALETA.get(p, "#AAA") for p in resumen["partido_madre"]]

    bars2 = ax2.bar(resumen["partido_madre"], resumen["km"],
                    color=cols2, edgecolor="white", width=0.6)
    for bar, (_, row) in zip(bars2, resumen.iterrows()):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.3,
                 f"{row['km']:.0f} km", ha="center", fontsize=9,
                 fontweight="bold", color="#333")

    # Añadir desglose Liberalismo XIX/XX
    era_summary = wm_lib.groupby("era")["long"].sum() / 1000
    y_offset = resumen.loc[resumen["partido_madre"] == "Liberalismo", "km"].values
    if len(y_offset):
        base = y_offset[0]
        xpos = list(resumen["partido_madre"]).index("Liberalismo")
        ax2.text(xpos, base * 0.35,
                 f"XIX: {era_summary.get('Liberal XIX', 0):.0f}km\n"
                 f"XX:  {era_summary.get('Liberal XX', 0):.0f}km",
                 ha="center", fontsize=7.5, color="white", fontweight="bold",
                 va="center")

    ax2.set_ylabel("Kilómetros lineales totales", **FONT_LABEL)
    ax2.set_title("Total kilómetros de calle por partido\n(calles con figuras políticas)",
                  **FONT_TITLE, pad=10)
    ax2.tick_params(**FONT_TICK)
    ax2.yaxis.grid(True, alpha=0.3, linestyle="--")
    ax2.set_axisbelow(True)
    sns.despine(ax=ax2)

    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig5_figuras_partido.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig5_figuras_partido.png")


# ---------------------------------------------------------------------------
# FIGURA 6 — Comparación síntesis: variables y significancia
# ---------------------------------------------------------------------------

def fig6_sintesis():
    print("[Fig 6] Síntesis de resultados...")
    tabla = pd.read_csv(TABLA_PATH, encoding="utf-8-sig")
    votos = pd.read_csv(VOTOS_PATH, encoding="utf-8-sig")

    partidos_map = [
        ("UCR",          "Centroderecha", PALETA["UCR"]),
        ("PJ",           "PJ",            PALETA["PJ"]),
        ("Liberalismo",  "Liberalismo",   PALETA["Liberalismo"]),
        ("PS",           "PS",            PALETA["PS"]),
    ]

    # Calcular stats para cada partido: rho pct_metros, rho m/km2, mann-whitney presencia
    vp = (votos.groupby(["circuito_id", "partido_electoral"])["pct_votos"]
          .mean().reset_index().rename(
              columns={"circuito_id": "circuito_geo_id", "pct_votos": "pct_votos_promedio"}))
    vp["circuito_geo_id"] = vp["circuito_geo_id"].astype(str)

    fig, axes = plt.subplots(1, 3, figsize=(14, 5), facecolor="white")
    titulos = ["pct_metros\n(% calles del partido)", "metros_por_km²\n(densidad absoluta)",
               "Presencia binaria\n(Mann-Whitney Δ)"]
    xlabels = ["ρ Spearman", "ρ Spearman", "Diferencia (pp)"]

    resultados = {t: [] for t in ["pct_metros", "metros_km2", "binario"]}
    nombres = []

    for pm, pe, col in partidos_map:
        sub = tabla[tabla["partido_madre"] == pm].dropna(
            subset=["pct_metros", "metros_por_km2", "pct_votos_promedio"])
        # pct_metros
        rho1, p1 = stats.spearmanr(sub["pct_metros"], sub["pct_votos_promedio"]) if len(sub) > 5 else (0, 1)
        # metros/km2
        rho2, p2 = stats.spearmanr(sub["metros_por_km2"], sub["pct_votos_promedio"]) if len(sub) > 5 else (0, 1)
        # presencia binaria
        circ_con = set(tabla[tabla["partido_madre"] == pm]["circuito_geo_id"].astype(str))
        todos = vp[vp["partido_electoral"] == pe]
        v_con = todos[todos["circuito_geo_id"].isin(circ_con)]["pct_votos_promedio"].dropna()
        v_sin = todos[~todos["circuito_geo_id"].isin(circ_con)]["pct_votos_promedio"].dropna()
        if len(v_con) > 3 and len(v_sin) > 3:
            _, p3 = stats.mannwhitneyu(v_con, v_sin, alternative="two-sided")
            delta = v_con.mean() - v_sin.mean()
        else:
            p3, delta = 1, 0

        resultados["pct_metros"].append((rho1, p1, col, pm))
        resultados["metros_km2"].append((rho2, p2, col, pm))
        resultados["binario"].append((delta, p3, col, pm))
        nombres.append(pm)

    for ax, (key, titulo, xlabel) in zip(
            axes, [("pct_metros", titulos[0], xlabels[0]),
                   ("metros_km2", titulos[1], xlabels[1]),
                   ("binario",    titulos[2], xlabels[2])]):

        data = resultados[key]
        vals  = [d[0] for d in data]
        pvals = [d[1] for d in data]
        cols  = [d[2] for d in data]
        parts = [d[3] for d in data]

        y = np.arange(len(data))
        bars = ax.barh(y, vals, color=cols, edgecolor="white",
                       height=0.6, alpha=0.85)

        for i, (v, p, part) in enumerate(zip(vals, pvals, parts)):
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
            xtext = v + (max(abs(x) for x in vals) * 0.05 if v >= 0
                         else -max(abs(x) for x in vals) * 0.05)
            ax.text(xtext, i, sig, va="center", fontsize=9,
                    color="#C0392B" if p < 0.05 else "#888",
                    fontweight="bold" if p < 0.05 else "normal")

        ax.set_yticks(y)
        ax.set_yticklabels(parts, fontsize=9)
        ax.axvline(0, color="#888", lw=0.8)
        ax.set_xlabel(xlabel, **FONT_LABEL)
        ax.set_title(titulo, **FONT_TITLE, pad=8)
        ax.tick_params(**FONT_TICK)
        ax.xaxis.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

    fig.suptitle("Figura 6 — Síntesis: qué variables predicen el voto (y cuáles no)",
                 fontsize=13, fontweight="bold", color="#1A1A1A", y=1.02)
    fig.text(0.5, -0.03,
             "* p<0.05  ** p<0.01  *** p<0.001  ns = no significativo",
             ha="center", fontsize=9, color="#555")

    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig6_sintesis.png", dpi=180, bbox_inches="tight",
                facecolor="white")
    plt.close()
    print("  -> fig6_sintesis.png")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generando figuras para el paper...\n")
    fig1_geografia()
    fig2_efecto_pj()
    fig3_temporal()
    fig4_lisa()
    fig5_figuras()
    fig6_sintesis()
    print(f"\nTodas las figuras guardadas en: {OUT_DIR.resolve()}")
