"""
Figuras del informe en formato paper (IEEE, dos columnas).

Diferencias con src/graficos.py:
    - Tamaños pensados para el ancho de columna (3,5 in) o de página (7,1 in).
    - Sin título incrustado: el título-mensaje va en la leyenda (caption) del paper.
    - Salida vectorial (PDF) para que el texto se lea nítido al imprimir.
Mismos datos, métricas, paleta y reglas de diseño que el resto de la solución.

Uso:
    python -m src.graficos_paper
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from adjustText import adjust_text

from src import config as cfg
from src import metricas as met
from src.graficos import num

COL, PAG = 3.45, 7.1          # pulgadas: ancho de columna y de página IEEE
SALIDA = cfg.IMAGES / "paper"

plt.rcParams.update({
    "font.family": "Liberation Sans", "font.size": 7.5,
    "axes.titlesize": 8.5, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": cfg.COLOR_GRIS_OSCURO, "axes.labelcolor": cfg.COLOR_TEXTO,
    "xtick.color": cfg.COLOR_GRIS_OSCURO, "ytick.color": cfg.COLOR_GRIS_OSCURO,
    "axes.titleweight": "bold", "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.02, "pdf.fonttype": 42, "axes.unicode_minus": False,
})
NOMBRE = {"Película": "Películas", "Serie": "Series"}


def _guardar(fig, nombre):
    SALIDA.mkdir(parents=True, exist_ok=True)
    fig.savefig(SALIDA / f"{nombre}.pdf", facecolor="white")
    fig.savefig(SALIDA / f"{nombre}.png", facecolor="white", dpi=220)
    plt.close(fig)
    return SALIDA / f"{nombre}.pdf"


def _titulo_panel(ax, tipo):
    ax.set_title(NOMBRE[tipo], loc="left", color=cfg.COLORES_TIPO[tipo])


# ------------------------------------------------------------ 1 oferta vs interacción
def p_oferta_interaccion(tg):
    fig, axes = plt.subplots(1, 2, figsize=(PAG, 3.1))
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = tg[(tg.tipo == tipo) & (tg.genero != "Sin clasificar")].sort_values("indice_traccion")
        for yi, (_, r) in enumerate(d.iterrows()):
            c = cfg.COLOR_POSITIVO if r.indice_traccion >= 1.5 else (
                cfg.COLOR_ACENTO if r.indice_traccion <= 0.4 else cfg.COLOR_GRIS)
            cp = c if c != cfg.COLOR_GRIS else cfg.COLOR_GRIS_OSCURO
            ax.plot([r.pct_titulos, r.pct_votos], [yi, yi], color=c, lw=1.8, zorder=1)
            ax.scatter(r.pct_titulos, yi, s=16, color="white", edgecolor=cfg.COLOR_GRIS_OSCURO, lw=0.9, zorder=2)
            ax.scatter(r.pct_votos, yi, s=16, color=cp, zorder=3)
            ax.text(max(r.pct_titulos, r.pct_votos) + 0.5, yi, f"x{num(r.indice_traccion, 2 if r.indice_traccion < 0.1 else 1)}",
                    va="center", fontsize=6.5, color=cp, fontweight="bold" if c != cfg.COLOR_GRIS else "normal")
        ax.set_yticks(range(len(d)))
        ax.set_yticklabels(d.genero)
        ax.xaxis.set_major_locator(mtick.MultipleLocator(5))
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{num(v)}%"))
        ax.set_xlim(0, max(d.pct_titulos.max(), d.pct_votos.max()) * 1.2)
        ax.grid(axis="x", color="#EEEEEE", lw=0.6); ax.set_axisbelow(True)
        ax.set_xlabel("% del total del tipo")
        ax.tick_params(axis="y", length=0)
        _titulo_panel(ax, tipo)
    axes[0].scatter([], [], s=16, color="white", edgecolor=cfg.COLOR_GRIS_OSCURO, label="% de asignaciones de género (oferta)")
    axes[0].scatter([], [], s=16, color=cfg.COLOR_GRIS_OSCURO, label="% de votos (interacción)")
    fig.tight_layout(w_pad=2.5, rect=(0, 0.06, 1, 1))
    fig.legend(*axes[0].get_legend_handles_labels(), loc="lower center", ncol=2, frameon=False)
    return _guardar(fig, "p01_oferta_interaccion")


# ------------------------------------------------------------ 2 matriz calidad-interacción
def p_matriz(tg):
    fig, axes = plt.subplots(1, 2, figsize=(PAG, 3.5))
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = tg[(tg.tipo == tipo) & (tg.genero != "Sin clasificar")].copy()
        xm, ym = d.indice_traccion.median(), d.calif_ponderada.median()
        joya = (d.indice_traccion < xm) & (d.calif_ponderada >= ym)
        motor = (d.indice_traccion >= xm) & (d.calif_ponderada >= ym)
        col = np.where(joya, cfg.COLOR_POSITIVO, np.where(motor, cfg.COLORES_TIPO[tipo], cfg.COLOR_GRIS))
        ax.scatter(d.indice_traccion, d.calif_ponderada, s=d.titulos / d.titulos.max() * 380 + 14,
                   c=col, alpha=0.85, edgecolor="white", lw=0.6)
        txt = [ax.text(r.indice_traccion, r.calif_ponderada, r.genero, fontsize=6.2, color=cfg.COLOR_TEXTO)
               for _, r in d.iterrows()]
        ax.set_xscale("log")
        ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"x{num(v, 1)}"))
        ax.xaxis.set_minor_formatter(mtick.NullFormatter())
        y0, y1 = ax.get_ylim(); ax.set_ylim(y0, y1 + (y1 - y0) * 0.16)
        ax.axvline(xm, color=cfg.COLOR_GRIS, ls="--", lw=0.7); ax.axhline(ym, color=cfg.COLOR_GRIS, ls="--", lw=0.7)
        adjust_text(txt, ax=ax, expand=(1.25, 1.7), force_text=(0.4, 0.8), arrowprops=dict(arrowstyle="-", color=cfg.COLOR_GRIS, lw=0.4))
        ax.set_xlabel("Índice de tracción (escala log)")
        ax.set_ylabel("Calificación ponderada media")
        ax.text(0.02, 0.98, "JOYAS OCULTAS", transform=ax.transAxes, fontsize=6.8, color=cfg.COLOR_POSITIVO,
                va="top", fontweight="bold")
        ax.text(0.98, 0.98, "MOTORES", transform=ax.transAxes, fontsize=6.8, color=cfg.COLORES_TIPO[tipo],
                va="top", ha="right", fontweight="bold")
        _titulo_panel(ax, tipo)
    fig.tight_layout(w_pad=2.5)
    return _guardar(fig, "p02_matriz")


# ------------------------------------------------------------ 3 concentración
def p_concentracion(cat):
    lz = met.curva_concentracion(cat)
    fig, ax = plt.subplots(figsize=(COL, 2.35))
    ax.plot([0, 100], [0, 100], color=cfg.COLOR_GRIS, ls="--", lw=0.8)
    ax.text(60, 52, "Igualdad", color=cfg.COLOR_GRIS_OSCURO, fontsize=6.5, rotation=31)
    for tipo, g in lz.groupby("tipo"):
        c = cfg.COLORES_TIPO[tipo]
        ax.plot(g.pct_titulos, g.pct_votos, color=c, lw=1.8)
        v10 = np.interp(10, g.pct_titulos, g.pct_votos)
        ax.scatter([10], [v10], color=c, s=14, zorder=3)
        ty = 66 if tipo == "Serie" else 44
        ax.annotate(f"{NOMBRE[tipo]}: top 10% = {num(v10)}% de los votos", (10, v10), xytext=(20, ty),
                    fontsize=6.8, color=c, fontweight="bold", arrowprops=dict(arrowstyle="-", color=c, lw=0.6))
    ax.axvline(10, color=cfg.COLOR_ACENTO, lw=0.7, alpha=0.5)
    ax.set_xlim(0, 100); ax.set_ylim(0, 102)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter()); ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("% acumulado de títulos (de más a menos votados)")
    ax.set_ylabel("% acumulado de votos")
    return _guardar(fig, "p03_concentracion")


# ------------------------------------------------------------ 4 visibilidad
def p_visibilidad(cat):
    tv = met.tabla_visibilidad(cat)
    pal = ["#C8102E", "#E88A8A", "#D9DCE0", "#8FA3B5", "#2E4A62"]
    fig, ax = plt.subplots(figsize=(COL, 1.35))
    for i, tipo in enumerate(["Serie", "Película"]):
        izq = 0
        for (_, r), c in zip(tv[tv.tipo == tipo].iterrows(), pal):
            ax.barh(i, r.pct, left=izq, color=c, edgecolor="white", height=0.62, lw=0.6)
            if r.pct >= 5:
                ax.text(izq + r.pct / 2, i, f"{num(r.pct)}%", ha="center", va="center", fontsize=6.5, fontweight="bold",
                        color="white" if c in ("#C8102E", "#2E4A62", "#8FA3B5") else cfg.COLOR_TEXTO)
            izq += r.pct
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Series", "Películas"])
    ax.set_xlim(0, 100); ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in pal]
    ax.legend(h, ["0", "1-9", "10-99", "100-999", "1000+"], ncol=5, loc="upper center",
              bbox_to_anchor=(0.5, -0.27), frameon=False, title="Votos recibidos por título", title_fontsize=6.8,
              handlelength=1, columnspacing=1)
    return _guardar(fig, "p04_visibilidad")


# ------------------------------------------------------------ 5 idiomas
def p_idiomas(cat):
    ti = met.tabla_idiomas(cat)
    fig, axes = plt.subplots(1, 2, figsize=(PAG, 2.25))
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = ti[ti.tipo == tipo].sort_values("pct_calif_alta")
        top = d.pct_calif_alta.idxmax()
        col = [cfg.COLOR_POSITIVO if i == top else (cfg.COLORES_TIPO[tipo] if r.idioma == "Inglés" else cfg.COLOR_GRIS)
               for i, r in d.iterrows()]
        ax.barh(d.idioma, d.pct_calif_alta, color=col, height=0.66)
        for yi, (_, r) in enumerate(d.iterrows()):
            ax.text(r.pct_calif_alta + 0.8, yi, f"{num(r.pct_calif_alta)}%  (n={num(r.titulos)})", va="center", fontsize=6.3)
        ax.set_xlim(0, d.pct_calif_alta.max() * 1.42)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_xlabel("% de títulos evaluados con calificación ≥ 7")
        ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
        _titulo_panel(ax, tipo)
    fig.tight_layout(w_pad=2.5)
    return _guardar(fig, "p05_idiomas")


# ------------------------------------------------------------ 6 tendencia
def p_tendencia(cat):
    ta = met.tabla_anual(cat)
    fig, ax = plt.subplots(figsize=(COL, 2.3))
    for tipo, g in ta.groupby("tipo"):
        c = cfg.COLORES_TIPO[tipo]
        ax.plot(g.anio, g.pct_calif_alta, color=c, lw=1.6, marker="o", ms=2.4)
        ax.text(2010, g.pct_calif_alta.iloc[0] + 4, NOMBRE[tipo], color=c, fontweight="bold", fontsize=7)
        pico = g[g.anio <= 2024].set_index("anio").pct_calif_alta.idxmax()
        vp = g.set_index("anio").pct_calif_alta[pico]
        if tipo == "Película":
            ax.annotate(f"máx. {num(vp)}% ({pico})", (pico, vp), xytext=(2014.3, vp + 9), fontsize=6.3, color=c,
                        arrowprops=dict(arrowstyle="-", color=c, lw=0.5))
    ax.axvspan(2024.5, 2025.5, color="#F2F2F2")
    ax.text(2025, 6, "2025:\npocos\nvotos", ha="center", fontsize=5.8, color=cfg.COLOR_GRIS_OSCURO)
    ax.set_xticks(range(2010, 2026, 3)); ax.set_ylim(0, 85)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylabel("% de títulos con calificación ≥ 7")
    ax.grid(axis="y", color="#EEEEEE", lw=0.6); ax.set_axisbelow(True)
    return _guardar(fig, "p06_tendencia")


# ------------------------------------------------------------ 7 popularidad vs calificación
def p_popularidad(cat):
    ev = cat[cat.votos >= 10]
    corr = met.correlaciones(cat)
    fig, axes = plt.subplots(1, 2, figsize=(COL, 1.9), sharey=True)
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = ev[ev.tipo == tipo]
        ax.hexbin(d.popularidad, d.calificacion, xscale="log", gridsize=26, cmap="Greys", mincnt=1, bins="log", linewidths=0.1)
        rho = corr[tipo].loc["popularidad", "calificacion"]
        ax.text(0.96, 0.05, f"Correlación: {num(rho, 2)}", transform=ax.transAxes, ha="right", fontsize=6.5,
                fontweight="bold", color=cfg.COLOR_ACENTO, bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1))
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: num(v)))
        ax.set_xlabel("Popularidad (log)")
        _titulo_panel(ax, tipo)
    axes[0].set_ylabel("Calificación (0-10)")
    fig.tight_layout(w_pad=0.8)
    return _guardar(fig, "p07_popularidad")


# ------------------------------------------------------------ 8 ROI
def p_roi(cat, tg):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(PAG, 2.3), gridspec_kw={"width_ratios": [1.1, 1]})
    d = tg[(tg.tipo == "Película") & tg.roi_mediano.notna() & (tg.n_roi >= 100)]
    d = d[~d.genero.isin(["Sin clasificar", "Película para TV"])].sort_values("roi_mediano").copy()
    d["roi"] = d.roi_mediano * 100
    top = d.roi.idxmax()
    a1.barh(d.genero, d.roi, color=[cfg.COLOR_POSITIVO if i == top else cfg.COLOR_PELICULA for i in d.index], height=0.66)
    for yi, (v, n) in enumerate(zip(d.roi, d.n_roi)):
        a1.text(v + 2, yi, f"{num(v)}%  (n={num(n)})", va="center", fontsize=6.2)
    a1.set_xlim(0, d.roi.max() * 1.35)
    a1.xaxis.set_major_formatter(mtick.PercentFormatter())
    a1.set_xlabel("ROI mediano")
    a1.set_title("Por género (géneros con 100+ películas con datos)", loc="left")
    a1.spines["left"].set_visible(False); a1.tick_params(axis="y", length=0)

    ta = met.tabla_anual(cat); g = ta[ta.tipo == "Película"]
    n = cat[cat.roi.notna()].groupby("anio").size()
    a2.plot(g.anio, g.roi_mediano, color=cfg.COLOR_PELICULA, lw=1.6, marker="o", ms=2.4)
    a2.axhline(0, color=cfg.COLOR_GRIS_OSCURO, lw=0.5)
    a2.axvspan(2019.5, 2021.5, color="#FBE3E6")
    v20 = g[g.anio == 2020].roi_mediano.iloc[0]
    a2.annotate(f"2020: {num(v20)}%", (2020, v20), xytext=(2012, v20 - 4), color=cfg.COLOR_ACENTO, fontweight="bold",
                fontsize=6.8, arrowprops=dict(arrowstyle="-", color=cfg.COLOR_ACENTO, lw=0.5))
    v25 = g[g.anio == 2025].roi_mediano.iloc[0]
    a2.annotate(f"2025: n = {n[2025]}", (2025, v25), xytext=(2021.3, v25 + 38), fontsize=6.3, color=cfg.COLOR_GRIS_OSCURO,
                arrowprops=dict(arrowstyle="-", color=cfg.COLOR_GRIS, lw=0.5))
    a2.yaxis.set_major_formatter(mtick.PercentFormatter())
    a2.set_xticks(range(2010, 2026, 3))
    a2.set_title("Por año de estreno", loc="left")
    a2.grid(axis="y", color="#EEEEEE", lw=0.6); a2.set_axisbelow(True)
    fig.tight_layout(w_pad=2.5)
    return _guardar(fig, "p08_roi")


# ------------------------------------------------------------ 9 países
def p_paises(pai):
    t = pai.groupby(["pais", "tipo"]).size().unstack(fill_value=0)
    t["total"] = t.sum(axis=1)
    t = t.sort_values("total").tail(10)
    fig, ax = plt.subplots(figsize=(COL, 2.2))
    ax.barh(t.index, t["Película"], color=cfg.COLOR_PELICULA, height=0.66, label="Películas")
    ax.barh(t.index, t["Serie"], left=t["Película"], color=cfg.COLOR_SERIE, height=0.66, label="Series")
    for yi, v in enumerate(t.total):
        ax.text(v + 80, yi, num(v), va="center", fontsize=6.3)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: num(v)))
    ax.set_xlabel("N.º de títulos (las coproducciones cuentan por país)")
    ax.legend(frameon=False, loc="lower right")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, t.total.max() * 1.13)
    return _guardar(fig, "p09_paises")


def generar_todas():
    cat, gen, pai = met.cargar_procesados()
    tg = met.tabla_generos(cat, gen)
    rutas = [p_oferta_interaccion(tg), p_matriz(tg), p_concentracion(cat), p_visibilidad(cat), p_idiomas(cat),
             p_tendencia(cat), p_popularidad(cat), p_roi(cat, tg), p_paises(pai)]
    for r in rutas:
        print("Figura paper:", r.name)
    return rutas


if __name__ == "__main__":
    generar_todas()
