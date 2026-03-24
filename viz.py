"""
visualizacion_capa5.py
======================
Capa 5 — Visualización geográfica

1. Mapa de calles trazadas por partido (coloreadas sobre circuitos)
2. Mapa coroplético: predominancia política por circuito
3. Mapa coroplético: % votos promedio por circuito (Centroderecha y PJ)
4. Mapa de clusters LISA

Genera:
  - Folium HTML interactivos
  - Matplotlib PNGs estáticos

Requiere: pip install folium geopandas matplotlib pandas shapely openpyxl
"""

import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from pathlib import Path
from shapely import wkt

try:
    import folium
    from folium.features import GeoJsonTooltip
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("[WARN] folium no instalado. Solo se generarán PNGs.")

OUT_DIR = Path("output_capa5")
OUT_DIR.mkdir(exist_ok=True)

# Paths — ajustar si difieren
CALLEJERO_MATCHED   = r"data/callejero_matched.csv"
CALLEJERO_GEO_PATH  = r"data/callejero_caba.xlsx"
CIRCUITOS_PATH      = r"data/circuitos_electorales.csv"
TABLA_ANALISIS      = r"data/tabla_analisis.csv"
LISA_DIR            = Path("output_capa4")

CRS = "EPSG:4326"

# Colores por partido
COLORES = {
    "UCR":         "#E31A1C",
    "PJ":          "#1F78B4",
    "PS":          "#E7298A",
    "Liberalismo": "#7570B3",
    "Prócer":      "#999999",
    "Dictadura":   "#444444",
    # Electorales
    "Centroderecha": "#E31A1C",
}

COLORES_LISA = {
    "High-High": "#d7191c",
    "Low-Low":   "#2c7bb6",
    "High-Low":  "#fdae61",
    "Low-High":  "#abd9e9",
    "ns":        "#eeeeee",
}


def parse_wkt_safe(g):
    try:
        return wkt.loads(g) if isinstance(g, str) and g.strip() else None
    except Exception:
        return None


def cargar_calles():
    """Carga calles matcheadas con geometría del Excel."""
    print("[1] Cargando calles matcheadas...")
    df = pd.read_csv(CALLEJERO_MATCHED, encoding="utf-8-sig")
    df = df[df["partido_madre"].notna()].copy()

    df_geo = pd.read_excel(CALLEJERO_GEO_PATH, usecols=["id", "geometry"])
    df = df.drop(columns=["geometry"], errors="ignore")
    df = df.merge(df_geo, on="id", how="left")
    df["geometry"] = df["geometry"].apply(parse_wkt_safe)

    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=CRS)
    gdf = gdf[gdf.geometry.notna()]
    print(f"    Calles con geometría: {len(gdf)}")
    return gdf


def cargar_circuitos():
    """Carga circuitos electorales."""
    print("[2] Cargando circuitos...")
    df = pd.read_csv(CIRCUITOS_PATH, encoding="utf-8-sig", dtype=str)
    df["geometry"] = df["WKT"].apply(parse_wkt_safe)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs=CRS)
    gdf = gdf[["CIRCUITO_N", "COMUNA", "geometry"]].rename(
        columns={"CIRCUITO_N": "circuito_geo_id", "COMUNA": "comuna"}
    )
    gdf = gdf[gdf.geometry.notna()]
    print(f"    Circuitos: {len(gdf)}")
    return gdf


# ---------------------------------------------------------------------------
# MAPA 1: Calles trazadas por partido
# ---------------------------------------------------------------------------

def mapa_calles_folium(gdf_calles, gdf_circuitos):
    if not HAS_FOLIUM:
        return
    print("[3a] Generando mapa Folium de calles...")

    center = [-34.615, -58.435]
    m = folium.Map(location=center, zoom_start=12, tiles="cartodbpositron")

    # Circuitos como fondo
    folium.GeoJson(
        gdf_circuitos.__geo_interface__,
        style_function=lambda f: {
            "fillColor": "#f0f0f0",
            "color": "#888888",
            "weight": 0.5,
            "fillOpacity": 0.2,
        },
        tooltip=GeoJsonTooltip(fields=["circuito_geo_id"], aliases=["Circuito:"]),
    ).add_to(m)

    # Calles por partido (cada partido en un FeatureGroup)
    for partido in sorted(gdf_calles["partido_madre"].unique()):
        sub = gdf_calles[gdf_calles["partido_madre"] == partido]
        color = COLORES.get(partido, "#666666")

        fg = folium.FeatureGroup(name=partido, show=(partido not in ["Prócer", "Dictadura"]))

        for _, row in sub.iterrows():
            if row.geometry is None:
                continue
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda f, c=color: {
                    "color": c, "weight": 2.5, "opacity": 0.8,
                },
                tooltip=f"{row.get('nomoficial', '')} — {row.get('figura_nombre', '')} ({partido})",
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    path = OUT_DIR / "mapa_calles_partido.html"
    m.save(str(path))
    print(f"    [OK] {path}")


def mapa_calles_matplotlib(gdf_calles, gdf_circuitos):
    print("[3b] Generando mapa Matplotlib de calles...")

    fig, ax = plt.subplots(1, 1, figsize=(12, 14))

    gdf_circuitos.plot(ax=ax, facecolor="#f5f5f0", edgecolor="#cccccc", linewidth=0.3)

    for partido in ["Prócer", "PS", "Liberalismo", "PJ", "UCR"]:
        sub = gdf_calles[gdf_calles["partido_madre"] == partido]
        if len(sub) == 0:
            continue
        color = COLORES.get(partido, "#666666")
        alpha = 0.3 if partido == "Prócer" else 0.8
        lw = 0.8 if partido == "Prócer" else 1.5
        sub.plot(ax=ax, color=color, linewidth=lw, alpha=alpha)

    # Leyenda
    patches = [
        mpatches.Patch(color=COLORES["UCR"], label="UCR"),
        mpatches.Patch(color=COLORES["PJ"], label="PJ"),
        mpatches.Patch(color=COLORES["PS"], label="PS"),
        mpatches.Patch(color=COLORES["Liberalismo"], label="Liberalismo"),
        mpatches.Patch(color=COLORES["Prócer"], label="Prócer", alpha=0.3),
    ]
    ax.legend(handles=patches, loc="lower left", fontsize=10, framealpha=0.9)
    ax.set_title("Calles con figuras políticas en CABA", fontsize=16, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()

    path = OUT_DIR / "mapa_calles_partido.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"    [OK] {path}")


# ---------------------------------------------------------------------------
# MAPA 2: Predominancia por circuito
# ---------------------------------------------------------------------------

def mapa_predominancia(gdf_circuitos, df_tabla):
    print("[4] Generando mapa de predominancia por circuito...")

    # Partido con más pct_metros por circuito
    predominante = (
        df_tabla
        .sort_values("pct_metros", ascending=False)
        .drop_duplicates("circuito_geo_id", keep="first")
        [["circuito_geo_id", "partido_madre", "pct_metros"]]
    )

    gdf = gdf_circuitos.merge(predominante, on="circuito_geo_id", how="left")
    gdf["color"] = gdf["partido_madre"].map(COLORES).fillna("#eeeeee")

    # Matplotlib
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    gdf.plot(ax=ax, color=gdf["color"], edgecolor="#888888", linewidth=0.3)

    patches = [mpatches.Patch(color=COLORES[p], label=p) for p in ["UCR", "PJ", "PS", "Liberalismo"]]
    patches.append(mpatches.Patch(color="#eeeeee", label="Sin calles políticas"))
    ax.legend(handles=patches, loc="lower left", fontsize=10, framealpha=0.9)
    ax.set_title("Partido predominante en calles (por circuito)", fontsize=16, fontweight="bold")
    ax.set_axis_off()
    plt.tight_layout()

    path = OUT_DIR / "mapa_predominancia.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"    [OK] {path}")

    # Folium
    if HAS_FOLIUM:
        center = [-34.615, -58.435]
        m = folium.Map(location=center, zoom_start=12, tiles="cartodbpositron")
        for _, row in gdf.iterrows():
            if row.geometry is None:
                continue
            partido = row.get("partido_madre", "")
            folium.GeoJson(
                row.geometry.__geo_interface__,
                style_function=lambda f, c=row["color"]: {
                    "fillColor": c, "color": "#666", "weight": 0.5, "fillOpacity": 0.6,
                },
                tooltip=f"Circ. {row['circuito_geo_id']} — {partido} ({row.get('pct_metros', 0):.0f}%)",
            ).add_to(m)
        path = OUT_DIR / "mapa_predominancia.html"
        m.save(str(path))
        print(f"    [OK] {path}")


# ---------------------------------------------------------------------------
# MAPA 3: Coroplético de % votos
# ---------------------------------------------------------------------------

def mapa_votos_coropletico(gdf_circuitos, df_tabla):
    print("[5] Generando mapas coropléticos de % votos...")

    for partido_elec, cmap_name in [("Centroderecha", "Reds"), ("PJ", "Blues")]:
        sub = df_tabla[df_tabla["partido_electoral"] == partido_elec].copy()
        if len(sub) == 0:
            continue

        gdf = gdf_circuitos.merge(
            sub[["circuito_geo_id", "pct_votos_promedio", "pct_metros"]],
            on="circuito_geo_id", how="left"
        )

        # Matplotlib
        fig, axes = plt.subplots(1, 2, figsize=(20, 14))

        # Panel 1: % votos
        vmin, vmax = gdf["pct_votos_promedio"].quantile(0.05), gdf["pct_votos_promedio"].quantile(0.95)
        norm = Normalize(vmin=vmin, vmax=vmax)
        cmap = plt.cm.get_cmap(cmap_name)

        gdf.plot(
            ax=axes[0], column="pct_votos_promedio", cmap=cmap_name,
            edgecolor="#888", linewidth=0.3, missing_kwds={"color": "#f0f0f0"},
            vmin=vmin, vmax=vmax,
        )
        sm = ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        fig.colorbar(sm, ax=axes[0], shrink=0.5, label="% votos promedio")
        axes[0].set_title(f"{partido_elec} — % votos promedio", fontsize=14, fontweight="bold")
        axes[0].set_axis_off()

        # Panel 2: % metros de calles
        gdf.plot(
            ax=axes[1], column="pct_metros", cmap=cmap_name,
            edgecolor="#888", linewidth=0.3, missing_kwds={"color": "#f0f0f0"},
            vmin=0, vmax=100,
        )
        norm2 = Normalize(vmin=0, vmax=100)
        sm2 = ScalarMappable(norm=norm2, cmap=cmap)
        sm2.set_array([])
        fig.colorbar(sm2, ax=axes[1], shrink=0.5, label="% metros calles")
        axes[1].set_title(f"{partido_elec} — % metros calles políticas", fontsize=14, fontweight="bold")
        axes[1].set_axis_off()

        plt.tight_layout()
        path = OUT_DIR / f"mapa_votos_vs_calles_{partido_elec.lower()}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"    [OK] {path}")


# ---------------------------------------------------------------------------
# MAPA 4: Clusters LISA
# ---------------------------------------------------------------------------

def mapa_lisa(gdf_circuitos):
    print("[6] Generando mapas LISA...")

    for partido in ["centroderecha", "pj", "ps"]:
        lisa_path = LISA_DIR / f"lisa_{partido}.csv"
        if not lisa_path.exists():
            print(f"    {lisa_path} no encontrado, skip.")
            continue

        df_lisa = pd.read_csv(lisa_path, encoding="utf-8-sig")
        df_lisa["circuito_geo_id"] = df_lisa["circuito_geo_id"].astype(str)

        gdf = gdf_circuitos.merge(df_lisa, on="circuito_geo_id", how="left")
        gdf["lisa_cluster"] = gdf["lisa_cluster"].fillna("ns")
        gdf["color"] = gdf["lisa_cluster"].map(COLORES_LISA).fillna("#eeeeee")

        # Matplotlib
        fig, ax = plt.subplots(1, 1, figsize=(12, 14))
        gdf.plot(ax=ax, color=gdf["color"], edgecolor="#888", linewidth=0.3)

        patches = [mpatches.Patch(color=v, label=k) for k, v in COLORES_LISA.items() if k != "ns"]
        patches.append(mpatches.Patch(color="#eeeeee", label="No significativo"))
        ax.legend(handles=patches, loc="lower left", fontsize=10, framealpha=0.9)
        ax.set_title(f"Clusters LISA — {partido.upper()}", fontsize=16, fontweight="bold")
        ax.set_axis_off()
        plt.tight_layout()

        path = OUT_DIR / f"mapa_lisa_{partido}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"    [OK] {path}")

        # Folium
        if HAS_FOLIUM:
            center = [-34.615, -58.435]
            m = folium.Map(location=center, zoom_start=12, tiles="cartodbpositron")
            for _, row in gdf.iterrows():
                if row.geometry is None:
                    continue
                folium.GeoJson(
                    row.geometry.__geo_interface__,
                    style_function=lambda f, c=row["color"]: {
                        "fillColor": c, "color": "#666", "weight": 0.5, "fillOpacity": 0.65,
                    },
                    tooltip=f"Circ. {row['circuito_geo_id']} — {row.get('lisa_cluster', 'ns')} (I={row.get('lisa_I', 0):.3f})",
                ).add_to(m)
            path = OUT_DIR / f"mapa_lisa_{partido}.html"
            m.save(str(path))
            print(f"    [OK] {path}")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    gdf_calles = cargar_calles()
    gdf_circuitos = cargar_circuitos()

    df_tabla = pd.read_csv(TABLA_ANALISIS, encoding="utf-8-sig")
    df_tabla["circuito_geo_id"] = df_tabla["circuito_geo_id"].astype(str)
    gdf_circuitos["circuito_geo_id"] = gdf_circuitos["circuito_geo_id"].astype(str)

    # Mapa 1: calles por partido
    mapa_calles_folium(gdf_calles, gdf_circuitos)
    mapa_calles_matplotlib(gdf_calles, gdf_circuitos)

    # Mapa 2: predominancia
    mapa_predominancia(gdf_circuitos, df_tabla)

    # Mapa 3: coropléticos votos vs calles
    mapa_votos_coropletico(gdf_circuitos, df_tabla)

    # Mapa 4: LISA
    mapa_lisa(gdf_circuitos)

    print(f"\n[OK] Capa 5 completa. Output en: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()