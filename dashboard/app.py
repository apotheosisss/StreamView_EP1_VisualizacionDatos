"""
Dashboard interactivo - StreamView Analytics
Evaluación Parcial N°1 - ADY1104 Visualización de Datos (Duoc UC)
Equipo: Claudio Aro, Guillermo Cerda, Manuel Díaz

Ejecutar desde la raíz del proyecto:
    streamlit run dashboard/app.py

Estructura:
    Barra lateral  -> navegación entre páginas + filtros globales
    Páginas        -> 1 Resumen ejecutivo | 2 Géneros | 3 Idiomas y origen
                      4 Tendencias | 5 Explorador de títulos | 6 Metodología
"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src import config as cfg          # noqa: E402
from src import metricas as met        # noqa: E402

st.set_page_config(page_title="StreamView Analytics | Dashboard", layout="wide",
                   initial_sidebar_state="expanded")

# ----------------------------------------------------------------- estilo
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
div[data-testid="stMetric"] {background: #F3F4F6; border-radius: 10px; padding: 12px 14px;}
div[data-testid="stMetricLabel"] p {font-size: 0.85rem; color: #5B6270;}
div[data-testid="stMetricValue"] {font-size: 1.7rem;}
.mensaje {background:#FFF4E5; border-left: 0; border-radius: 8px; padding: 10px 14px;
          font-size: 0.98rem; margin: 4px 0 14px 0;}
.pie {color:#5B6270; font-size:0.8rem;}
</style>
""", unsafe_allow_html=True)

PLANTILLA = dict(
    template="simple_white",
    font=dict(family="Arial, sans-serif", size=13, color=cfg.COLOR_TEXTO),
    separators=",.",
    margin=dict(l=10, r=20, t=60, b=10),
    hoverlabel=dict(bgcolor="white", font_size=13),
)


def num(x, dec=0):
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def estilo(fig, titulo, subtitulo=None, alto=420):
    texto = f"<b>{titulo}</b>"
    if subtitulo:
        texto += f"<br><span style='font-size:12px;color:#5B6270'>{subtitulo}</span>"
    fig.update_layout(**PLANTILLA, title=dict(text=texto, x=0, xanchor="left"), height=alto)
    return fig


def mensaje(texto):
    st.markdown(f"<div class='mensaje'>{texto}</div>", unsafe_allow_html=True)


# ----------------------------------------------------------------- datos
@st.cache_data(show_spinner="Cargando catálogo...")
def cargar():
    if not cfg.CATALOGO.exists():
        from src import preparacion
        preparacion.ejecutar()
    return met.cargar_procesados()


cat_total, gen_total, pai_total = cargar()

# ----------------------------------------------------------------- barra lateral
st.sidebar.markdown("## StreamView Analytics")
st.sidebar.caption("Catálogo 2010-2025 | Dashboard de contenido y engagement")

PAGINAS = ["1. Resumen ejecutivo", "2. Géneros: oferta vs interacción", "3. Idiomas y origen",
           "4. Tendencias", "5. Explorador de títulos", "6. Metodología y glosario"]
pagina = st.sidebar.radio("Navegación", PAGINAS, key="pagina")

st.sidebar.markdown("---")
st.sidebar.markdown("### Filtros")

if st.sidebar.button("Restablecer filtros", use_container_width=True):
    for k in ["f_tipo", "f_anios", "f_generos", "f_idiomas", "f_votos"]:
        st.session_state.pop(k, None)
    st.rerun()

tipos = st.sidebar.multiselect("Tipo de contenido", ["Película", "Serie"],
                               default=["Película", "Serie"], key="f_tipo", placeholder="Elige un tipo")
anios = st.sidebar.slider("Año de estreno", 2010, 2025, (2010, 2025), key="f_anios")
lista_generos = sorted(gen_total["genero"].unique())
generos = st.sidebar.multiselect("Géneros", lista_generos, key="f_generos", placeholder="Todos los géneros")
top_idiomas = cat_total["idioma"].value_counts().head(15).index.tolist()
idiomas = st.sidebar.multiselect("Idioma original", top_idiomas, key="f_idiomas", placeholder="Todos los idiomas")
votos_min = st.sidebar.select_slider("Votos mínimos por título", [0, 1, 10, 50, 100, 500, 1000],
                                     value=0, key="f_votos")

# aplicar filtros
f = cat_total[cat_total["tipo"].isin(tipos) & cat_total["anio"].between(*anios)
              & (cat_total["votos"] >= votos_min)]
if generos:
    ids = gen_total[gen_total["genero"].isin(generos)][["id", "tipo"]].drop_duplicates()
    f = f.merge(ids, on=["id", "tipo"])
if idiomas:
    f = f[f["idioma"].isin(idiomas)]
g = gen_total.merge(f[["id", "tipo"]], on=["id", "tipo"])
p = pai_total.merge(f[["id", "tipo"]], on=["id", "tipo"])

st.sidebar.markdown("---")
st.sidebar.caption(f"Títulos en la selección: **{num(len(f))}** de {num(len(cat_total))}")
st.sidebar.download_button("Descargar selección (CSV)", f.to_csv(index=False).encode("utf-8"),
                           "seleccion_streamview.csv", "text/csv", use_container_width=True)
st.sidebar.caption("Equipo: Claudio Aro, Guillermo Cerda, Manuel Díaz | ADY1104 Duoc UC")

if f.empty:
    st.warning("La combinación de filtros no devuelve títulos. Ajusta los filtros de la barra lateral.")
    st.stop()

K = met.kpis(f)
K0 = met.kpis(cat_total)


def _delta(valor, base, dec=2, sufijo=""):
    dif = valor - base
    if pd.isna(dif) or abs(dif) < 10 ** (-dec) / 2:
        return None
    return f"{num(dif, dec)}{sufijo} vs catálogo"


def fila_kpis():
    c = st.columns(6)
    c[0].metric("Títulos", num(K["titulos"]),
                help="Cantidad de películas y series en la selección.")
    c[1].metric("Votos", num(K["votos_totales"]),
                help="Suma de votos de usuarios. Proxy de interacción (engagement).")
    c[2].metric("Calif. ponderada", num(K["calif_media"], 2),
                delta=_delta(K["calif_media"], K0["calif_media"]),
                help="Promedio bayesiano (0-10) que corrige notas con pocos votos.")
    c[3].metric("% calif. 7+", f"{num(K['pct_calif_alta'], 1)}%",
                delta=_delta(K["pct_calif_alta"], K0["pct_calif_alta"], 1, " pp"),
                help="Porcentaje de títulos evaluados con calificación 7 o superior.")
    c[4].metric("% baja visibilidad", f"{num(K['pct_baja_visibilidad'], 1)}%",
                delta=_delta(K["pct_baja_visibilidad"], K0["pct_baja_visibilidad"], 1, " pp"),
                delta_color="inverse",
                help="Títulos con menos de 10 votos: el usuario casi no los descubre.")
    c[5].metric("Votos top 10%", f"{num(K['pct_top10_votos'], 1)}%",
                help="Concentración: % de votos que se lleva el 10% de títulos más votados.")


def grafico_traccion(tg, tipo, alto=520):
    d = tg[(tg["tipo"] == tipo) & (tg["genero"] != "Sin clasificar")].sort_values("indice_traccion")
    colores = [cfg.COLOR_POSITIVO if v >= 1.5 else cfg.COLOR_ACENTO if v <= 0.4 else cfg.COLOR_GRIS
               for v in d.indice_traccion]
    fig = go.Figure(go.Bar(
        x=d.indice_traccion, y=d.genero, orientation="h", marker_color=colores,
        text=[f"x{num(v, 1)}" for v in d.indice_traccion], textposition="outside", cliponaxis=False,
        customdata=d[["pct_titulos", "pct_votos", "titulos"]],
        hovertemplate="<b>%{y}</b><br>Índice de tracción: x%{x:.2f}<br>% asignaciones: %{customdata[0]:.1f}%"
                      "<br>% votos: %{customdata[1]:.1f}%<br>Títulos: %{customdata[2]:,}<extra></extra>"))
    fig.add_vline(x=1, line_dash="dash", line_color=cfg.COLOR_GRIS_OSCURO)
    nombre = "Películas" if tipo == "Película" else "Series"
    estilo(fig, f"{nombre}: interacción vs peso en el catálogo",
           "Tracción = % votos / % asignaciones de género. Petróleo: motor; rojo: baja.", alto)
    fig.update_xaxes(title="Índice de tracción", range=[0, max(2.2, d.indice_traccion.max() * 1.2)])
    fig.update_layout(margin=dict(l=10, r=40, t=70, b=10))
    return fig


# ======================================================================== 1
if pagina == PAGINAS[0]:
    st.title("Resumen ejecutivo")
    st.caption("¿Qué contenido genera interacción, cuál satisface y cuál el usuario no alcanza a descubrir?")
    fila_kpis()
    mensaje(f"<b>Mensaje clave:</b> el 10% de los títulos concentra el <b>{num(K['pct_top10_votos'])}%</b> "
            f"de la interacción y el <b>{num(K['pct_baja_visibilidad'])}%</b> del catálogo seleccionado "
            f"tiene menos de 10 votos. StreamView no necesita más títulos: necesita que los títulos "
            f"correctos sean descubiertos.")

    tg = met.tabla_generos(f, g, min_titulos=30)
    tipos_presentes = [t for t in ["Película", "Serie"] if t in tg["tipo"].unique()]
    cols = st.columns(len(tipos_presentes)) if tipos_presentes else []
    for col_, tipo in zip(cols, tipos_presentes):
        with col_:
            st.plotly_chart(grafico_traccion(tg, tipo), use_container_width=True)

    c1, c2 = st.columns([1, 1.25])
    with c1:
        lz = met.curva_concentracion(f)
        fig = px.line(lz, x="pct_titulos", y="pct_votos", color="tipo", color_discrete_map=cfg.COLORES_TIPO,
                      labels={"pct_titulos": "% acumulado de títulos", "pct_votos": "% acumulado de votos",
                              "tipo": "Tipo"})
        fig.update_traces(hovertemplate="%{x:.0f}% de títulos concentra %{y:.1f}% de votos<extra></extra>")
        fig.add_scatter(x=[0, 100], y=[0, 100], mode="lines", line=dict(dash="dash", color=cfg.COLOR_GRIS),
                        name="Igualdad", hoverinfo="skip")
        fig.add_vline(x=10, line_color=cfg.COLOR_ACENTO, line_width=1)
        estilo(fig, "Concentración de la interacción", "Curva de Lorenz de votos por título", 400)
        fig.update_layout(legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        tv = met.tabla_visibilidad(f)
        fig = px.bar(tv, x="pct", y="tipo", color="visibilidad", orientation="h",
                     category_orders={"visibilidad": cfg.ORDEN_VISIBILIDAD},
                     color_discrete_sequence=["#C8102E", "#E88A8A", "#D9DCE0", "#8FA3B5", "#2E4A62"],
                     text=tv["pct"].map(lambda v: f"{num(v)}%" if v >= 4 else ""),
                     labels={"pct": "% de títulos", "tipo": "", "visibilidad": "Votos por título"},
                     custom_data=["titulos"])
        fig.update_traces(hovertemplate="%{fullData.name}: %{x:.1f}% (%{customdata[0]:,} títulos)<extra></extra>")
        estilo(fig, "Visibilidad del catálogo", "Distribución de títulos por tramo de votos recibidos", 400)
        fig.update_layout(legend=dict(orientation="h", y=-0.25), barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

# ======================================================================== 2
elif pagina == PAGINAS[1]:
    st.title("Géneros: oferta vs interacción")
    fila_kpis()
    tg = met.tabla_generos(f, g, min_titulos=30)
    tg = tg[tg["genero"] != "Sin clasificar"]
    mensaje("<b>Cómo leer:</b> arriba a la derecha están los <b>motores</b> (bien evaluados y con alta "
            "interacción); arriba a la izquierda las <b>joyas ocultas</b> (bien evaluadas pero poco "
            "descubiertas). <b>Selecciona burbujas</b> (clic o lazo) para ver sus títulos más destacados.")
    tipo_sel = st.radio("Tipo", [t for t in ["Película", "Serie"] if t in tg["tipo"].unique()],
                        horizontal=True, key="tipo_matriz")
    d = tg[tg["tipo"] == tipo_sel]
    if d.empty:
        st.info("No hay géneros suficientes con los filtros actuales.")
    else:
        xm, ym = d["indice_traccion"].median(), d["calif_ponderada"].median()
        d = d.assign(cuadrante=[
            "Motor" if (x >= xm and y >= ym) else "Joya oculta" if (x < xm and y >= ym)
            else "Volumen sin calidad" if x >= xm else "Baja prioridad"
            for x, y in zip(d["indice_traccion"], d["calif_ponderada"])])
        colores_q = {"Motor": cfg.COLORES_TIPO[tipo_sel], "Joya oculta": cfg.COLOR_POSITIVO,
                     "Volumen sin calidad": cfg.COLOR_GRIS_OSCURO, "Baja prioridad": cfg.COLOR_GRIS}
        fig = px.scatter(d, x="indice_traccion", y="calif_ponderada", size="titulos", color="cuadrante",
                         color_discrete_map=colores_q, text="genero", log_x=True, size_max=55,
                         custom_data=["genero", "titulos", "votos", "pct_calif_alta"],
                         labels={"indice_traccion": "Índice de tracción (log)",
                                 "calif_ponderada": "Calificación ponderada promedio", "cuadrante": ""})
        fig.update_traces(textposition="top center", textfont_size=11,
                          hovertemplate="<b>%{customdata[0]}</b><br>Tracción: x%{x:.2f}<br>"
                                        "Calificación ponderada: %{y:.2f}<br>Títulos: %{customdata[1]:,}<br>"
                                        "Votos: %{customdata[2]:,}<br>% bien evaluados: %{customdata[3]:.1f}%"
                                        "<extra></extra>")
        fig.add_vline(x=xm, line_dash="dash", line_color=cfg.COLOR_GRIS)
        fig.add_hline(y=ym, line_dash="dash", line_color=cfg.COLOR_GRIS)
        estilo(fig, f"Matriz calidad vs interacción por género ({'películas' if tipo_sel == 'Película' else 'series'})",
               "Tamaño = cantidad de títulos. Líneas = mediana de los géneros.", 560)
        ticks = [0.05, 0.1, 0.2, 0.5, 1, 2, 3]
        fig.update_xaxes(tickvals=ticks, ticktext=[f"x{num(t, 2 if t < 0.1 else 1)}" for t in ticks])
        fig.update_layout(legend=dict(orientation="h", y=-0.2), dragmode="lasso")
        evento = st.plotly_chart(fig, use_container_width=True, on_select="rerun",
                                 selection_mode=("points", "lasso", "box"), key="matriz")

        seleccion = []
        try:
            seleccion = [pt["customdata"][0] for pt in evento.selection.points]
        except Exception:
            seleccion = []
        if not seleccion:
            seleccion = st.multiselect("O elige géneros para ver el detalle:", d["genero"].tolist(),
                                       default=d.sort_values("indice_traccion").head(1)["genero"].tolist())
        if seleccion:
            ids = g[(g["genero"].isin(seleccion)) & (g["tipo"] == tipo_sel)][["id", "tipo"]]
            det = f.merge(ids.drop_duplicates(), on=["id", "tipo"])
            det = det[det["votos"] > 0].sort_values("calif_ponderada", ascending=False)
            st.markdown(f"**Títulos mejor evaluados en: {', '.join(seleccion)}** "
                        f"({num(len(det))} títulos evaluados)")
            st.dataframe(
                det[["titulo", "anio", "idioma", "generos", "votos", "calif_ponderada", "popularidad"]].head(25),
                hide_index=True, use_container_width=True,
                column_config={
                    "titulo": "Título", "anio": st.column_config.NumberColumn("Año", format="%d"),
                    "idioma": "Idioma", "generos": "Géneros",
                    "votos": st.column_config.NumberColumn("Votos", format="%d"),
                    "calif_ponderada": st.column_config.ProgressColumn(
                        "Calif. ponderada", min_value=0, max_value=10, format="%.2f"),
                    "popularidad": st.column_config.NumberColumn("Popularidad", format="%.1f"),
                })

    st.markdown("#### Tabla resumen por género")
    st.dataframe(
        tg[["tipo", "genero", "titulos", "pct_titulos", "pct_votos", "indice_traccion", "calif_ponderada",
            "pct_calif_alta", "roi_mediano"]].sort_values(["tipo", "indice_traccion"], ascending=[True, False]),
        hide_index=True, use_container_width=True,
        column_config={
            "tipo": "Tipo", "genero": "Género", "titulos": "Títulos",
            "pct_titulos": st.column_config.NumberColumn("% asignaciones", format="%.1f%%"),
            "pct_votos": st.column_config.NumberColumn("% votos", format="%.1f%%"),
            "indice_traccion": st.column_config.NumberColumn("Tracción", format="x%.2f"),
            "calif_ponderada": st.column_config.NumberColumn("Calif. ponderada", format="%.2f"),
            "pct_calif_alta": st.column_config.NumberColumn("% bien evaluados", format="%.1f%%"),
            "roi_mediano": st.column_config.NumberColumn("ROI mediano (películas)", format="%.2f"),
        })

# ======================================================================== 3
elif pagina == PAGINAS[2]:
    st.title("Idiomas y origen del contenido")
    fila_kpis()
    mensaje("<b>Hallazgo (catálogo completo):</b> entre los idiomas con 200+ títulos evaluados, el japonés tiene la "
            "mayor proporción de títulos bien evaluados en películas y en series, mientras el inglés concentra el "
            "volumen. En series el orden es sensible al mínimo de votos: usa el filtro de votos mínimos para comprobarlo.")
    c1, c2 = st.columns(2)
    with c1:
        ti = met.tabla_idiomas(f, min_titulos=150)
        if not ti.empty:
            orden = (ti.groupby("idioma")["pct_calif_alta"].mean().sort_values().index.tolist())
            fig = px.scatter(ti, x="pct_calif_alta", y="idioma", color="tipo",
                             color_discrete_map=cfg.COLORES_TIPO, custom_data=["titulos", "calif_ponderada"],
                             category_orders={"idioma": orden[::-1]},
                             labels={"pct_calif_alta": "% de títulos con calificación 7+", "idioma": "",
                                     "tipo": "Tipo"})
            fig.update_traces(hovertemplate="<b>%{y}</b><br>%{x:.1f}% bien evaluados<br>"
                                            "Títulos evaluados: %{customdata[0]:,}<br>"
                                            "Calif. ponderada: %{customdata[1]:.2f}<extra></extra>")
            estilo(fig, "Calidad percibida por idioma",
                   "Idiomas con 150+ títulos evaluados. Pasa el cursor para ver el detalle.", 560)
            fig.update_traces(marker=dict(size=13, line=dict(width=1, color="white")))
            fig.update_layout(legend=dict(orientation="h", y=-0.15))
            fig.update_yaxes(showgrid=True, gridcolor="#EEEEEE")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay idiomas con al menos 150 títulos evaluados en la selección.")
    with c2:
        mp = p.groupby(["pais_en", "pais"]).size().rename("titulos").reset_index()
        fig = px.choropleth(mp, locations="pais_en", locationmode="country names", color="titulos",
                            hover_name="pais", color_continuous_scale=["#F3F4F6", "#8FA3B5", "#2E4A62"],
                            labels={"titulos": "Títulos"})
        fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>Títulos: %{z:,}<extra></extra>")
        fig.update_coloraxes(colorbar=dict(tickformat=",d"))
        estilo(fig, "Países productores", "Títulos en los que participa cada país (zoom y arrastre habilitados)", 560)
        fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
        st.plotly_chart(fig, use_container_width=True)

    top = p.groupby(["pais", "tipo"]).size().rename("titulos").reset_index()
    orden = top.groupby("pais").titulos.sum().sort_values(ascending=False).head(15).index.tolist()
    top = top[top.pais.isin(orden)]
    fig = px.bar(top, x="pais", y="titulos", color="tipo", color_discrete_map=cfg.COLORES_TIPO,
                 category_orders={"pais": orden}, labels={"pais": "", "titulos": "Títulos", "tipo": "Tipo"})
    fig.update_traces(hovertemplate="%{x}: %{y:,} títulos<extra></extra>")
    estilo(fig, "Top 15 países por cantidad de títulos", None, 380)
    fig.update_yaxes(tickformat=",d")
    st.plotly_chart(fig, use_container_width=True)

# ======================================================================== 4
elif pagina == PAGINAS[3]:
    st.title("Tendencias 2010-2025")
    fila_kpis()
    ta = met.tabla_anual(f)
    metrica = st.segmented_control(
        "Indicador", ["% bien evaluados", "Calificación ponderada", "Votos medianos", "ROI mediano (películas)"],
        default="% bien evaluados", key="ind_tend") or "% bien evaluados"
    col = {"% bien evaluados": "pct_calif_alta", "Calificación ponderada": "calif_ponderada",
           "Votos medianos": "votos_mediana", "ROI mediano (películas)": "roi_mediano"}[metrica]
    d = ta.dropna(subset=[col])
    fig = px.line(d, x="anio", y=col, color="tipo", markers=True, color_discrete_map=cfg.COLORES_TIPO,
                  labels={"anio": "Año de estreno", col: metrica, "tipo": "Tipo"})
    fig.update_traces(hovertemplate="%{x}: %{y:.1f}<extra></extra>")
    if col == "roi_mediano" and not d.empty:
        fig.add_vrect(x0=2019.5, x1=2021.5, fillcolor="#FBE3E6", line_width=0,
                      annotation_text="Pandemia", annotation_position="top left")
        lo, hi = int(d[col].min() // 20 * 20), int(d[col].max() // 20 * 20 + 20)
        vals = list(range(lo, hi + 1, 20))
        fig.update_yaxes(tickvals=vals, ticktext=[f"{v}%" for v in vals])
    fig.add_vrect(x0=2024.5, x1=2025.5, fillcolor="#F2F2F2", line_width=0,
                  annotation_text="2025: pocos votos", annotation_position="bottom right")
    estilo(fig, f"Evolución anual: {metrica}", "Muestra balanceada de 1.000 títulos por año y tipo", 480)
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)
    # Mensaje calculado sobre la selección actual (no se escriben cifras fijas)
    partes = []
    for t_, nombre_ in [("Película", "películas"), ("Serie", "series")]:
        s_ = ta[ta["tipo"] == t_].set_index("anio")["pct_calif_alta"]
        if 2010 in s_.index and 2024 in s_.index:
            pico = s_.loc[:2024].idxmax()
            partes.append(f"{nombre_}: {num(s_[2010])}% en 2010 y {num(s_[2024])}% en 2024, con máximo de "
                          f"{num(s_[pico])}% en {pico}")
    if partes:
        mensaje("<b>Lectura:</b> la proporción de títulos bien evaluados tiende a subir, con retrocesos ("
                + "; ".join(partes) + "). Los títulos recientes acumulan menos votos, por lo que parte del alza "
                "puede ser sesgo de antigüedad. El ROI de películas se desplomó en 2020 y aún no recupera su "
                "nivel previo (2025 tiene muy pocas películas con datos financieros).")

    ev = f[f["votos"] >= 10]
    if len(ev) > 0:
        muestra = ev.sample(min(4000, len(ev)), random_state=42)
        fig = px.scatter(muestra, x="popularidad", y="calificacion", color="tipo", log_x=True, opacity=0.45,
                         color_discrete_map=cfg.COLORES_TIPO, hover_name="titulo",
                         labels={"popularidad": "Popularidad (log)", "calificacion": "Calificación", "tipo": "Tipo"})
        fig.update_traces(marker_size=5, hovertemplate="<b>%{hovertext}</b><br>Popularidad: %{x:.1f}"
                                                       "<br>Calificación: %{y:.1f}<extra></extra>")
        rho = ev.groupby("tipo").apply(lambda x: x["popularidad"].corr(x["calificacion"], method="spearman"))
        sub = " | ".join(f"{t}: rho = {num(v, 2)}" for t, v in rho.items())
        estilo(fig, "Popularidad vs calificación (títulos con 10+ votos)", f"Correlación de Spearman. {sub}", 460)
        st.plotly_chart(fig, use_container_width=True)

# ======================================================================== 5
elif pagina == PAGINAS[4]:
    st.title("Explorador de títulos")
    fila_kpis()
    c1, c2, c3 = st.columns([2, 1, 1])
    busqueda = c1.text_input("Buscar por título, director o reparto", "")
    orden = c2.selectbox("Ordenar por", ["Calificación ponderada", "Votos", "Popularidad", "Año", "ROI"])
    solo_joyas = c3.toggle("Solo joyas ocultas", help="Calificación ponderada en el 25% superior y "
                                                      "votos bajo la mediana de su tipo.")
    d = f.copy()
    if busqueda:
        q = busqueda.lower()
        d = d[d["titulo"].str.lower().str.contains(q, regex=False, na=False)
              | d["director"].fillna("").str.lower().str.contains(q, regex=False)
              | d["reparto"].fillna("").str.lower().str.contains(q, regex=False)]
    if solo_joyas:
        ev = d[d["votos"] > 0]
        q75 = ev.groupby("tipo")["calif_ponderada"].transform(lambda s: s.quantile(0.75))
        med = ev.groupby("tipo")["votos"].transform("median")
        d = ev[(ev["calif_ponderada"] >= q75) & (ev["votos"] < med)]
    col = {"Calificación ponderada": "calif_ponderada", "Votos": "votos", "Popularidad": "popularidad",
           "Año": "anio", "ROI": "roi"}[orden]
    d = d.sort_values(col, ascending=False, na_position="last")
    st.caption(f"{num(len(d))} títulos encontrados (se muestran hasta 500)")
    st.dataframe(
        d[["titulo", "tipo", "anio", "genero_principal", "idioma", "pais_principal", "votos", "calificacion",
           "calif_ponderada", "popularidad", "roi"]].head(500),
        hide_index=True, use_container_width=True, height=560,
        column_config={
            "titulo": "Título", "tipo": "Tipo", "anio": st.column_config.NumberColumn("Año", format="%d"),
            "genero_principal": "Género principal", "idioma": "Idioma", "pais_principal": "País",
            "votos": st.column_config.NumberColumn("Votos", format="%d"),
            "calificacion": st.column_config.NumberColumn("Calificación", format="%.1f"),
            "calif_ponderada": st.column_config.ProgressColumn("Calif. ponderada", min_value=0, max_value=10,
                                                               format="%.2f"),
            "popularidad": st.column_config.NumberColumn("Popularidad", format="%.1f"),
            "roi": st.column_config.NumberColumn("ROI", format="%.2f"),
        })

# ======================================================================== 6
else:
    st.title("Metodología y glosario")
    st.markdown("""
**Fuentes integradas:** catálogo de películas (16.000 registros) y catálogo de series (16.000 registros),
2010-2025. Se unificaron columnas, se eliminaron 9 duplicados de id y se armonizaron las taxonomías de
género de ambas fuentes en 21 géneros en español (más "Sin clasificar"; 16 géneros por tipo).

| Indicador | Definición | Qué representa para el negocio |
|---|---|---|
| Votos | Cantidad de usuarios que calificaron el título | Interacción (engagement) |
| Popularidad | Índice de actividad reciente del título | Atención / tendencia |
| Calificación ponderada | (v/(v+m))*R + (m/(v+m))*C, con m = mediana de votos y C = media del tipo | Satisfacción corregida por pocos votos |
| Índice de tracción | % de votos del género / % de asignaciones título-género del género | Si el género rinde más o menos que su peso en el catálogo |
| % baja visibilidad | Títulos con menos de 10 votos | Contenido que el usuario no descubre |
| ROI | (recaudación - presupuesto) / presupuesto | Rentabilidad (solo películas con datos) |

**Limitaciones:** las fuentes son catálogos públicos con metadatos de TMDB: votos, calificación y popularidad
provienen de la comunidad TMDB y no de usuarios de StreamView. Describen el catálogo, no el comportamiento individual de usuarios
(reproducciones, suscripciones, dispositivos). Votos y popularidad se usan como aproximaciones del
engagement. La muestra tiene 1.000 títulos por año y tipo, por lo que no permite analizar el crecimiento
del volumen del catálogo. Las columnas duración y fecha de incorporación no son informativas y se excluyeron.
""")
    st.markdown("<p class='pie'>Proyecto EP1 ADY1104 - Duoc UC 2026.</p>", unsafe_allow_html=True)
