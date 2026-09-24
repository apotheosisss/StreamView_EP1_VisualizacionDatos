"""
Figuras estáticas (matplotlib) para el informe y la presentación.

Principios aplicados en todas las figuras:
    - Título = mensaje (el hallazgo), subtítulo = qué se mide.
    - Gris para el contexto, color solo en lo que se quiere destacar.
    - Sin bordes superiores/derechos ni cuadrículas innecesarias
      (menos tinta no informativa = menor carga cognitiva).
    - Etiquetas directas sobre los datos en lugar de leyendas cuando es posible.
    - Formato numérico chileno (coma decimal).

Uso:
    python -m src.graficos
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from adjustText import adjust_text

from src import config as cfg
from src import metricas as met

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": 10.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": cfg.COLOR_GRIS_OSCURO,
    "axes.labelcolor": cfg.COLOR_TEXTO,
    "xtick.color": cfg.COLOR_GRIS_OSCURO,
    "ytick.color": cfg.COLOR_GRIS_OSCURO,
    "axes.titleweight": "bold",
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
    "axes.formatter.use_locale": False,
    "axes.unicode_minus": False,
})


def num(x, dec=0):
    """Formato chileno: miles con punto y decimales con coma."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _titulo(fig, titulo, subtitulo):
    h = fig.get_figheight()
    fig.text(0.01, 1 + 0.40 / h, titulo, fontsize=14, fontweight="bold",
             color=cfg.COLOR_TEXTO, ha="left", va="bottom")
    fig.text(0.01, 1 + 0.12 / h, subtitulo, fontsize=10.5, color=cfg.COLOR_GRIS_OSCURO,
             ha="left", va="bottom")


def _fuente(fig, texto="Fuente: catálogo StreamView 2010-2025 (31.991 títulos integrados). Elaboración propia."):
    fig.text(0.01, -0.12 / fig.get_figheight(), texto, fontsize=8.5, color=cfg.COLOR_GRIS_OSCURO, ha="left", va="top")


def _guardar(fig, nombre):
    cfg.IMAGES.mkdir(parents=True, exist_ok=True)
    ruta = cfg.IMAGES / nombre
    fig.savefig(ruta, facecolor="white")
    plt.close(fig)
    return ruta


# ------------------------------------------------------------------ F1
def fig_oferta_vs_interaccion(tg):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.2), sharex=False)
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = tg[(tg.tipo == tipo) & (tg.genero != "Sin clasificar")].copy()
        d = d.sort_values("indice_traccion")
        y = np.arange(len(d))
        for yi, (_, r) in zip(y, d.iterrows()):
            gana = r.pct_votos > r.pct_titulos
            color = cfg.COLOR_POSITIVO if r.indice_traccion >= 1.5 else (
                cfg.COLOR_ACENTO if r.indice_traccion <= 0.4 else cfg.COLOR_GRIS)
            ax.plot([r.pct_titulos, r.pct_votos], [yi, yi], color=color, lw=2.6, zorder=1)
            ax.scatter(r.pct_titulos, yi, s=46, color="white", edgecolor=cfg.COLOR_GRIS_OSCURO, lw=1.4, zorder=2)
            ax.scatter(r.pct_votos, yi, s=46, color=color if color != cfg.COLOR_GRIS else cfg.COLOR_GRIS_OSCURO, zorder=3)
            ax.text(max(r.pct_titulos, r.pct_votos) + 0.6, yi, f"x{num(r.indice_traccion, 1)}",
                    va="center", fontsize=9, color=color if color != cfg.COLOR_GRIS else cfg.COLOR_GRIS_OSCURO,
                    fontweight="bold" if color != cfg.COLOR_GRIS else "normal")
        ax.set_yticks(y)
        ax.set_yticklabels(d.genero)
        ax.xaxis.set_major_locator(mtick.MultipleLocator(5))
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"{num(v)}%"))
        ax.set_xlim(0, max(d.pct_titulos.max(), d.pct_votos.max()) * 1.18)
        ax.set_title("Películas" if tipo == "Película" else "Series", loc="left", fontsize=12,
                     color=cfg.COLORES_TIPO[tipo])
        ax.grid(axis="x", color="#EEEEEE", lw=0.8)
        ax.set_axisbelow(True)
        ax.set_xlabel("% del total de asignaciones del tipo")
    axes[0].scatter([], [], s=46, color="white", edgecolor=cfg.COLOR_GRIS_OSCURO, label="% de asignaciones de género (oferta)")
    axes[0].scatter([], [], s=46, color=cfg.COLOR_GRIS_OSCURO, label="% de votos asignados (interacción)")
    axes[0].legend(loc="lower right", frameon=False, fontsize=9)
    _titulo(fig, "Ciencia ficción y acción generan hasta 2,5 veces más interacción que su peso en el catálogo",
            "Participación de cada género en la oferta (asignaciones título-género) y en la interacción (votos). "
            "xN = índice de tracción = % votos / % asignaciones.")
    _fuente(fig)
    fig.tight_layout(w_pad=4)
    return _guardar(fig, "fig01_oferta_vs_interaccion.png")


# ------------------------------------------------------------------ F2
def fig_matriz_calidad(tg):
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 6))
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = tg[(tg.tipo == tipo) & (tg.genero != "Sin clasificar")].copy()
        xm, ym = d.indice_traccion.median(), d.calif_ponderada.median()
        joya = (d.indice_traccion < xm) & (d.calif_ponderada >= ym)
        estrella = (d.indice_traccion >= xm) & (d.calif_ponderada >= ym)
        colores = np.where(joya, cfg.COLOR_POSITIVO, np.where(estrella, cfg.COLORES_TIPO[tipo], cfg.COLOR_GRIS))
        ax.scatter(d.indice_traccion, d.calif_ponderada, s=d.titulos / d.titulos.max() * 900 + 40,
                   c=colores, alpha=0.85, edgecolor="white", lw=1)
        textos = [ax.text(r.indice_traccion, r.calif_ponderada, r.genero, fontsize=8.5,
                          color=cfg.COLOR_TEXTO) for _, r in d.iterrows()]
        ax.set_xscale("log")
        ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 3])
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"x{num(v, 1)}"))
        ax.xaxis.set_minor_formatter(mtick.NullFormatter())
        y0, y1 = ax.get_ylim()
        ax.set_ylim(y0, y1 + (y1 - y0) * 0.14)
        adjust_text(textos, ax=ax, expand=(1.15, 1.4),
                    arrowprops=dict(arrowstyle="-", color=cfg.COLOR_GRIS, lw=0.6))
        ax.axvline(xm, color=cfg.COLOR_GRIS, ls="--", lw=1)
        ax.axhline(ym, color=cfg.COLOR_GRIS, ls="--", lw=1)
        ax.set_xlabel("Índice de tracción (escala log): % votos / % asignaciones")
        ax.set_ylabel("Calificación ponderada promedio (0-10)")
        ax.set_title("Películas" if tipo == "Película" else "Series", loc="left", fontsize=12,
                     color=cfg.COLORES_TIPO[tipo])
        ax.text(0.02, 0.98, "JOYAS OCULTAS\nalta calidad, baja interacción", transform=ax.transAxes,
                fontsize=8.5, color=cfg.COLOR_POSITIVO, va="top", fontweight="bold")
        ax.text(0.98, 0.98, "MOTORES\nalta calidad, alta interacción", transform=ax.transAxes,
                fontsize=8.5, color=cfg.COLORES_TIPO[tipo], va="top", ha="right", fontweight="bold")
    _titulo(fig, "Documental, música e historia: bien evaluados, pero poco descubiertos",
            "Cada burbuja es un género; tamaño = cantidad de títulos. Líneas punteadas = mediana de los géneros. "
            "En películas, drama y romance también caen en el cuadrante de joyas, cerca del umbral.")
    _fuente(fig)
    fig.tight_layout(w_pad=4)
    return _guardar(fig, "fig02_matriz_calidad_interaccion.png")


def fig_matriz_presentacion(tg, tipo="Película"):
    """Versión de la matriz para diapositiva: un solo panel y texto >= 14 pt."""
    d = tg[(tg.tipo == tipo) & (tg.genero != "Sin clasificar")].copy()
    xm, ym = d.indice_traccion.median(), d.calif_ponderada.median()
    joya = (d.indice_traccion < xm) & (d.calif_ponderada >= ym)
    motor = (d.indice_traccion >= xm) & (d.calif_ponderada >= ym)
    colores = np.where(joya, cfg.COLOR_POSITIVO, np.where(motor, cfg.COLORES_TIPO[tipo], cfg.COLOR_GRIS))
    with plt.rc_context({"font.size": 15}):
        fig, ax = plt.subplots(figsize=(7.4, 4.4))
        ax.scatter(d.indice_traccion, d.calif_ponderada, s=d.titulos / d.titulos.max() * 1400 + 80,
                   c=colores, alpha=0.9, edgecolor="white", lw=1.2)
        # Solo se rotulan los géneros que sostienen el mensaje (menos ruido visual)
        rotular = joya | motor | d.genero.isin(["Terror"])
        # Rótulos con posición fija (legibilidad al proyectar, sin superposición)
        pos = {"Documental": (10, 2, "left"), "Música": (-10, 6, "right"), "Animación": (12, 12, "left"),
               "Historia y bélico": (12, 7, "left"), "Familiar": (12, -2, "left"), "Drama": (-34, 12, "right"),
               "Romance": (-18, -4, "right"), "Ciencia ficción y fantasía": (6, -36, "center"),
               "Terror": (14, -4, "left")}
        for (_, r), j, k in zip(d.iterrows(), joya, rotular):
            if not k:
                continue
            dx, dy, ha = pos.get(r.genero, (10, 0, "left"))
            etiqueta = "Ciencia ficción\ny fantasía" if r.genero.startswith("Ciencia") else r.genero
            ax.annotate(etiqueta, (r.indice_traccion, r.calif_ponderada), xytext=(dx, dy), textcoords="offset points",
                        ha=ha, va="center", fontsize=15.5, color=cfg.COLOR_POSITIVO if j else cfg.COLOR_TEXTO,
                        fontweight="bold" if j else "normal")
        ax.set_xscale("log")
        ax.set_xlim(0.12, 3)
        ax.set_xticks([0.2, 0.5, 1, 2, 3])
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"x{num(v, 2 if v < 0.1 else 1)}"))
        ax.xaxis.set_minor_formatter(mtick.NullFormatter())
        y0, y1 = ax.get_ylim(); ax.set_ylim(y0, y1 + (y1 - y0) * 0.25)
        ax.axvline(xm, color=cfg.COLOR_GRIS, ls="--", lw=1.2)
        ax.axhline(ym, color=cfg.COLOR_GRIS, ls="--", lw=1.2)
        ax.set_xlabel("Interacción: índice de tracción (escala log)", fontsize=15)
        ax.set_ylabel("Calidad: calificación ponderada", fontsize=15)
        ax.text(0.02, 0.97, "JOYAS OCULTAS", transform=ax.transAxes, fontsize=16, color=cfg.COLOR_POSITIVO,
                va="top", fontweight="bold")
        ax.text(0.98, 0.97, "MOTORES", transform=ax.transAxes, fontsize=16, color=cfg.COLORES_TIPO[tipo],
                va="top", ha="right", fontweight="bold")
        ax.tick_params(labelsize=14.5)
        return _guardar(fig, "fig02b_matriz_peliculas_presentacion.png")


# ------------------------------------------------------------------ F3
def fig_concentracion(cat):
    lz = met.curva_concentracion(cat)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    ax.plot([0, 100], [0, 100], color=cfg.COLOR_GRIS, ls="--", lw=1)
    ax.text(62, 55, "Distribución igualitaria", color=cfg.COLOR_GRIS_OSCURO, fontsize=9, rotation=33)
    for tipo, g in lz.groupby("tipo"):
        c = cfg.COLORES_TIPO[tipo]
        ax.plot(g.pct_titulos, g.pct_votos, color=c, lw=2.6)
        v10 = np.interp(10, g.pct_titulos, g.pct_votos)
        ax.scatter([10], [v10], color=c, zorder=3, s=40)
        etiqueta = "Series" if tipo == "Serie" else "Películas"
        ty = 70 if tipo == "Serie" else 48
        ax.annotate(f"{etiqueta}: el 10% de los títulos\nconcentra el {num(v10)}% de los votos",
                    (10, v10), xytext=(22, ty), fontsize=9.5, color=c, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=c, lw=1))
    ax.axvline(10, color=cfg.COLOR_ACENTO, lw=1, alpha=0.5)
    ax.set_xlim(0, 100); ax.set_ylim(0, 102)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("% acumulado de títulos (de mayor a menor cantidad de votos)")
    ax.set_ylabel("% acumulado de votos")
    _titulo(fig, "La interacción se concentra en muy pocos títulos",
            "Curva de concentración (Lorenz) de los votos recibidos por título.")
    _fuente(fig)
    return _guardar(fig, "fig03_concentracion_interaccion.png")


# ------------------------------------------------------------------ F4
def fig_visibilidad(cat):
    tv = met.tabla_visibilidad(cat)
    paleta = ["#C8102E", "#E88A8A", "#D9DCE0", "#8FA3B5", "#2E4A62"]
    fig, ax = plt.subplots(figsize=(10.5, 3.4))
    for i, tipo in enumerate(["Serie", "Película"]):
        izq = 0
        d = tv[tv.tipo == tipo]
        for (_, r), col in zip(d.iterrows(), paleta):
            ax.barh(i, r.pct, left=izq, color=col, edgecolor="white", height=0.62)
            if r.pct >= 4:
                ax.text(izq + r.pct / 2, i, f"{num(r.pct)}%", ha="center", va="center", fontsize=9.5,
                        color="white" if col in ("#C8102E", "#2E4A62", "#8FA3B5") else cfg.COLOR_TEXTO,
                        fontweight="bold")
            izq += r.pct
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Series", "Películas"], fontsize=11)
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in paleta]
    ax.legend(handles, cfg.ORDEN_VISIBILIDAD, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.2),
              frameon=False, fontsize=9, title="Votos recibidos por título", title_fontsize=9)
    _titulo(fig, "6 de cada 10 series son prácticamente invisibles (menos de 10 votos)",
            "Distribución de títulos según tramo de visibilidad.")
    fig.text(0.01, -1.3 / fig.get_figheight(), "Fuente: catálogo StreamView 2010-2025. Elaboración propia.", fontsize=8.5,
             color=cfg.COLOR_GRIS_OSCURO)
    return _guardar(fig, "fig04_visibilidad_tramos.png")


# ------------------------------------------------------------------ F5
def fig_idiomas(cat):
    ti = met.tabla_idiomas(cat)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = ti[ti.tipo == tipo].sort_values("pct_calif_alta")
        top = d.pct_calif_alta.idxmax()
        colores = [cfg.COLOR_POSITIVO if i == top else (cfg.COLORES_TIPO[tipo] if r.idioma == "Inglés" else cfg.COLOR_GRIS)
                   for i, r in d.iterrows()]
        ax.barh(d.idioma, d.pct_calif_alta, color=colores, height=0.65)
        for yi, (_, r) in enumerate(d.iterrows()):
            ax.text(r.pct_calif_alta + 0.8, yi, f"{num(r.pct_calif_alta)}%  (n={num(r.titulos)})",
                    va="center", fontsize=9, color=cfg.COLOR_TEXTO)
        ax.set_xlim(0, d.pct_calif_alta.max() * 1.35)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax.set_xlabel("% de títulos con calificación 7 o más")
        ax.set_title("Películas" if tipo == "Película" else "Series", loc="left", fontsize=12,
                     color=cfg.COLORES_TIPO[tipo])
        ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    _titulo(fig, "El contenido japonés es el mejor evaluado; el inglés domina en volumen, no en calidad",
            "Porcentaje de títulos bien evaluados (calificación >= 7) por idioma original. Idiomas con 200+ títulos evaluados.")
    _fuente(fig)
    fig.tight_layout(w_pad=4)
    return _guardar(fig, "fig05_idiomas_calidad.png")


# ------------------------------------------------------------------ F6
def fig_tendencia(cat):
    ta = met.tabla_anual(cat)
    fig, ax = plt.subplots(figsize=(10, 5))
    for tipo, g in ta.groupby("tipo"):
        c = cfg.COLORES_TIPO[tipo]
        ax.plot(g.anio, g.pct_calif_alta, color=c, lw=2.6, marker="o", ms=4)
        ax.text(2010, g.pct_calif_alta.iloc[0] + 4, "Series" if tipo == "Serie" else "Películas",
                color=c, fontweight="bold", fontsize=11)
        p = g[g.anio == 2010].pct_calif_alta.iloc[0]; q = g[g.anio == 2024].pct_calif_alta.iloc[0]
        ax.annotate(f"{num(p)}% -> {num(q)}%", (2024, q), xytext=(2019.6, q + (7 if tipo == "Serie" else 9)),
                    fontsize=9.5, color=c, arrowprops=dict(arrowstyle="-", color=c, lw=0.8))
    ax.axvspan(2024.5, 2025.5, color="#F2F2F2")
    ax.text(2025, 8, "2025: estrenos\nrecientes con\npocos votos", ha="center", fontsize=8, color=cfg.COLOR_GRIS_OSCURO)
    ax.set_xticks(range(2010, 2026, 1)); ax.tick_params(axis="x", labelrotation=45)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_ylim(0, 85)
    ax.set_ylabel("% de títulos con calificación 7 o más")
    ax.grid(axis="y", color="#EEEEEE"); ax.set_axisbelow(True)
    _titulo(fig, "La proporción de títulos bien evaluados tiende a subir desde 2010, con retrocesos",
            "Porcentaje de títulos bien evaluados por año de estreno. Los años recientes acumulan menos votos "
            "(posible sesgo de antigüedad).")
    _fuente(fig, "Fuente: catálogo StreamView 2010-2025 (muestra de 1.000 títulos por año y tipo). Elaboración propia.")
    return _guardar(fig, "fig06_tendencia_calidad.png")


# ------------------------------------------------------------------ F7
def fig_popularidad_calidad(cat):
    ev = cat[cat.votos >= 10]
    corr = met.correlaciones(cat)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, tipo in zip(axes, ["Película", "Serie"]):
        d = ev[ev.tipo == tipo]
        ax.hexbin(d.popularidad, d.calificacion, xscale="log", gridsize=38, cmap="Greys", mincnt=1, bins="log")
        rho = corr[tipo].loc["popularidad", "calificacion"]
        ax.text(0.97, 0.05, f"Correlación de Spearman = {num(rho, 2)}", transform=ax.transAxes, ha="right",
                fontsize=10.5, fontweight="bold", color=cfg.COLOR_ACENTO,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85))
        ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: num(v)))
        ax.set_xlabel("Popularidad (escala logarítmica)")
        ax.set_title("Películas" if tipo == "Película" else "Series", loc="left", fontsize=12,
                     color=cfg.COLORES_TIPO[tipo])
    axes[0].set_ylabel("Calificación promedio (0-10)")
    _titulo(fig, "Ser popular no es lo mismo que ser bien evaluado",
            "Relación entre popularidad y calificación (títulos con 10+ votos). Tono más oscuro = más títulos.")
    _fuente(fig)
    fig.tight_layout(w_pad=3)
    return _guardar(fig, "fig07_popularidad_vs_calificacion.png")


# ------------------------------------------------------------------ F8
def fig_roi(cat, tg):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 5.2), gridspec_kw={"width_ratios": [1.1, 1]})
    d = tg[(tg.tipo == "Película") & tg.roi_mediano.notna() & (tg.n_roi >= 100)].copy()
    d = d[~d.genero.isin(["Sin clasificar", "Película para TV"])].sort_values("roi_mediano")
    d["roi"] = d.roi_mediano * 100
    top = d.roi.idxmax()
    col = [cfg.COLOR_POSITIVO if i == top else cfg.COLOR_PELICULA for i in d.index]
    a1.barh(d.genero, d.roi, color=col, height=0.65)
    for yi, v in enumerate(d.roi):
        a1.text(v + 2, yi, f"{num(v)}%", va="center", fontsize=9)
    a1.set_xlabel("ROI mediano = (recaudación - presupuesto) / presupuesto")
    a1.xaxis.set_major_formatter(mtick.PercentFormatter())
    a1.set_title("Por género", loc="left", fontsize=12)
    a1.spines["left"].set_visible(False); a1.tick_params(axis="y", length=0)
    a1.set_xlim(min(0, d.roi.min()) - 10, d.roi.max() * 1.18)

    ta = met.tabla_anual(cat)
    g = ta[ta.tipo == "Película"]
    a2.plot(g.anio, g.roi_mediano, color=cfg.COLOR_PELICULA, lw=2.6, marker="o", ms=4)
    a2.axhline(0, color=cfg.COLOR_GRIS_OSCURO, lw=0.8)
    a2.axvspan(2019.5, 2021.5, color="#FBE3E6")
    v20 = g[g.anio == 2020].roi_mediano.iloc[0]
    a2.annotate(f"Pandemia: {num(v20)}%", (2020, v20), xytext=(2011.3, v20 - 5), color=cfg.COLOR_ACENTO,
                fontweight="bold", arrowprops=dict(arrowstyle="-", color=cfg.COLOR_ACENTO, lw=0.8))
    a2.yaxis.set_major_formatter(mtick.PercentFormatter())
    a2.set_xticks(range(2010, 2026, 3))
    a2.set_title("Por año de estreno", loc="left", fontsize=12)
    a2.grid(axis="y", color="#EEEEEE"); a2.set_axisbelow(True)
    _titulo(fig, "Terror y animación son los géneros más rentables; la rentabilidad aún no vuelve a niveles previos a 2020",
            "ROI mediano (taquilla) de películas con presupuesto y recaudación informados (n = 3.362; 2025: solo 24 películas).")
    _fuente(fig)
    fig.tight_layout(w_pad=4)
    return _guardar(fig, "fig08_rentabilidad_peliculas.png")


# ------------------------------------------------------------------ F9
def fig_paises(pai):
    t = pai.groupby(["pais", "tipo"]).size().unstack(fill_value=0)
    t["total"] = t.sum(axis=1)
    t = t.sort_values("total").tail(12)
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.barh(t.index, t["Película"], color=cfg.COLOR_PELICULA, height=0.65, label="Películas")
    ax.barh(t.index, t["Serie"], left=t["Película"], color=cfg.COLOR_SERIE, height=0.65, label="Series")
    for yi, v in enumerate(t.total):
        ax.text(v + 80, yi, num(v), va="center", fontsize=9)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: num(v)))
    ax.set_xlabel("Títulos en los que participa el país (coproducciones cuentan para cada país)")
    ax.legend(frameon=False, loc="lower right")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, t.total.max() * 1.12)
    _titulo(fig, "Estados Unidos domina el origen; Asia pesa más en series que en películas",
            "Top 12 países productores por cantidad de títulos.")
    _fuente(fig)
    return _guardar(fig, "fig09_paises_origen.png")


def generar_todas():
    cat, gen, pai = met.cargar_procesados()
    tg = met.tabla_generos(cat, gen)
    rutas = [
        fig_oferta_vs_interaccion(tg), fig_matriz_calidad(tg), fig_matriz_presentacion(tg), fig_concentracion(cat),
        fig_visibilidad(cat), fig_idiomas(cat), fig_tendencia(cat),
        fig_popularidad_calidad(cat), fig_roi(cat, tg), fig_paises(pai),
    ]
    for r in rutas:
        print("Figura generada:", r.name)
    return rutas


if __name__ == "__main__":
    generar_todas()
