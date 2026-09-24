"""Genera el informe ejecutivo para gerencia (HTML + PDF).

Uso, desde la raíz del proyecto:
    python -m docs.fuentes_generacion.informe_ejecutivo.generar_informe
    (o: python docs/fuentes_generacion/informe_ejecutivo/generar_informe.py)

Todas las cifras y gráficos se calculan con src.metricas sobre data/processed,
igual que el dashboard y la presentación. El PDF se imprime con Microsoft Edge
o Google Chrome en modo headless.
"""
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from src import config as cfg      # noqa: E402
from src import metricas as met    # noqa: E402

AQUI = Path(__file__).resolve().parent
HTML = AQUI / "informe_ejecutivo.html"
PDF = RAIZ / "docs" / "Informe_Ejecutivo_StreamView.pdf"
URL_DASHBOARD = "https://apotheosisss-streamview-ep1-visualizacionda-dashboardapp-f3aacs.streamlit.app/"

# Paleta del proyecto: un color, un significado
PELI, SERIE = cfg.COLOR_PELICULA, cfg.COLOR_SERIE
POS, ALERTA = cfg.COLOR_POSITIVO, cfg.COLOR_ACENTO
GRIS, GRIS_OSC, TINTA = "#C9CDD3", cfg.COLOR_GRIS_OSCURO, cfg.COLOR_TEXTO
REJILLA = "#E6E8EC"


# --------------------------------------------------------------------- formato
def num(x, dec=0):
    """Formato chileno: punto de miles, coma decimal."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, dec=0):
    return f"{num(x, dec)}%"


# --------------------------------------------------------------------- SVG
def _barra(x, y, w, h, color):
    """Barra horizontal anclada a la base, con extremo de datos redondeado (4 px)."""
    if w <= 0:
        return ""
    r = min(4, w, h / 2)
    return (f'<path d="M{x:.1f},{y:.1f} h{w - r:.1f} a{r},{r} 0 0 1 {r},{r} v{h - 2 * r:.1f} '
            f'a{r},{r} 0 0 1 -{r},{r} h-{w - r:.1f} z" fill="{color}"/>')


def barras_h(filas, vmax, ref=None, ancho=660, col_etq=190, col_extra=0, alto_fila=24,
             titulo_extra="", fmt=lambda v: pct(v)):
    """Barras horizontales ordenadas. filas = [(etiqueta, valor, color, negrita, extra)]."""
    area = ancho - col_etq - col_extra - 60
    top = 26 if (ref or titulo_extra) else 6
    alto = top + len(filas) * alto_fila + 10
    s = [f'<svg viewBox="0 0 {ancho} {alto}" role="img" xmlns="http://www.w3.org/2000/svg">']
    esc = lambda v: col_etq + v / vmax * area
    if ref:
        xr = esc(ref[0])
        s.append(f'<line x1="{xr:.1f}" y1="{top - 4}" x2="{xr:.1f}" y2="{alto - 6}" stroke="{GRIS_OSC}" '
                 f'stroke-width="1.2" stroke-dasharray="4 3"/>')
        s.append(f'<text x="{xr:.1f}" y="{top - 10}" text-anchor="middle" class="nota">{escape(ref[1])}</text>')
    if titulo_extra:
        s.append(f'<text x="{ancho}" y="{top - 10}" text-anchor="end" class="nota">{escape(titulo_extra)}</text>')
    for i, (etq, v, color, negrita, extra) in enumerate(filas):
        y = top + i * alto_fila
        peso = ' font-weight="700"' if negrita else ""
        s.append(f'<text x="{col_etq - 10}" y="{y + alto_fila / 2 + 4:.1f}" text-anchor="end" class="etq"{peso}>'
                 f'{escape(etq)}</text>')
        w = v / vmax * area
        s.append(_barra(col_etq, y + 4, w, alto_fila - 8, color))
        s.append(f'<text x="{col_etq + w + 6:.1f}" y="{y + alto_fila / 2 + 4:.1f}" class="val"{peso}>{fmt(v)}</text>')
        if extra:
            s.append(f'<text x="{ancho}" y="{y + alto_fila / 2 + 4:.1f}" text-anchor="end" class="etq"{peso}>'
                     f'{escape(extra)}</text>')
    s.append("</svg>")
    return "".join(s)


def apilada_100(filas, ancho=660, col_etq=110, alto_fila=46):
    """Barras 100% apiladas. filas = [(etiqueta, [(valor, color, texto, texto_oscuro)])]."""
    area = ancho - col_etq
    alto = len(filas) * alto_fila + 6
    s = [f'<svg viewBox="0 0 {ancho} {alto}" role="img" xmlns="http://www.w3.org/2000/svg">']
    for i, (etq, segs) in enumerate(filas):
        y = i * alto_fila + 4
        h = alto_fila - 14
        s.append(f'<text x="{col_etq - 10}" y="{y + h / 2 + 5:.1f}" text-anchor="end" class="etq" '
                 f'font-weight="700">{escape(etq)}</text>')
        x = col_etq
        total = sum(v for v, *_ in segs)
        for j, (v, color, txt, oscuro) in enumerate(segs):
            w = v / total * area - (2 if j < len(segs) - 1 else 0)   # 2 px de separación
            s.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="3" fill="{color}"/>')
            tinta = TINTA if oscuro else "#FFFFFF"
            s.append(f'<text x="{x + 10:.1f}" y="{y + h / 2 + 5:.1f}" class="seg" fill="{tinta}">'
                     f'{escape(txt)}</text>')
            x += w + 2
    s.append("</svg>")
    return "".join(s)


def lineas(series, x0, x1, ymin, ymax, ticks_y, ancho=320, alto=210, fmt_y=lambda v: pct(v),
           cero=False, marcas=None):
    """Gráfico de líneas con un solo eje. series = [(nombre, {anio: valor}, color)]."""
    iz, de, ar, ab = 40, 78, 12, 26
    ax = lambda a: iz + (a - x0) / (x1 - x0) * (ancho - iz - de)
    ay = lambda v: ar + (ymax - v) / (ymax - ymin) * (alto - ar - ab)
    s = [f'<svg viewBox="0 0 {ancho} {alto}" role="img" xmlns="http://www.w3.org/2000/svg">']
    for t in ticks_y:
        color, grosor = (GRIS_OSC, 1) if (cero and t == 0) else (REJILLA, 1)
        s.append(f'<line x1="{iz}" y1="{ay(t):.1f}" x2="{ancho - de + 6}" y2="{ay(t):.1f}" '
                 f'stroke="{color}" stroke-width="{grosor}"/>')
        s.append(f'<text x="{iz - 6}" y="{ay(t) + 4:.1f}" text-anchor="end" class="eje">{fmt_y(t)}</text>')
    for a in (x0, (x0 + x1) // 2, x1):
        s.append(f'<text x="{ax(a):.1f}" y="{alto - 8}" text-anchor="middle" class="eje">{a}</text>')
    for nombre, datos, color in series:
        pts = " ".join(f"{ax(a):.1f},{ay(v):.1f}" for a, v in sorted(datos.items()))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" '
                 f'stroke-linejoin="round" stroke-linecap="round"/>')
        for a in (min(datos), max(datos)):
            s.append(f'<circle cx="{ax(a):.1f}" cy="{ay(datos[a]):.1f}" r="4" fill="{color}" '
                     f'stroke="#FFFFFF" stroke-width="2"/>')
        s.append(f'<text x="{ax(min(datos)) + 6:.1f}" y="{ay(datos[min(datos)]) - 9:.1f}" class="val" '
                 f'text-anchor="start">{fmt_y(datos[min(datos)])}</text>')
        ult = max(datos)
        s.append(f'<text x="{ax(ult) + 8:.1f}" y="{ay(datos[ult]) + 4:.1f}" class="val" font-weight="700">'
                 f'{fmt_y(datos[ult])} {escape(nombre)}</text>')
    for a, v, texto in (marcas or []):
        s.append(f'<circle cx="{ax(a):.1f}" cy="{ay(v):.1f}" r="5" fill="{ALERTA}" stroke="#FFFFFF" stroke-width="2"/>')
        s.append(f'<text x="{ax(a):.1f}" y="{ay(v) + 20:.1f}" text-anchor="middle" class="val" '
                 f'font-weight="700" fill="{ALERTA}">{escape(texto)}</text>')
    s.append("</svg>")
    return "".join(s)


# --------------------------------------------------------------------- datos
def calcular():
    cat, gen, _ = met.cargar_procesados()
    d = {"k": met.kpis(cat)}
    d["kp"] = met.kpis(cat[cat["tipo"] == "Película"])
    d["ks"] = met.kpis(cat[cat["tipo"] == "Serie"])
    tg = met.tabla_generos(cat, gen)
    tg = tg[tg["genero"] != "Sin clasificar"]
    d["gen_s"] = tg[tg["tipo"] == "Serie"].sort_values("indice_traccion", ascending=False)
    d["gen_p"] = tg[tg["tipo"] == "Película"].sort_values("pct_calif_alta", ascending=False)
    ti = met.tabla_idiomas(cat)
    tot = cat.groupby("tipo")["votos"].sum()
    ti["pct_votos"] = ti.apply(lambda r: r["votos"] / tot[r["tipo"]] * 100, axis=1)
    d["idi_p"] = ti[ti["tipo"] == "Película"].sort_values("pct_calif_alta", ascending=False)
    d["idi_s"] = ti[ti["tipo"] == "Serie"].set_index("idioma")
    ta = met.tabla_anual(cat)
    ta = ta[ta["anio"] <= 2024]
    d["anual"] = {t: g.set_index("anio") for t, g in ta.groupby("tipo")}
    corr = met.correlaciones(cat)
    d["rho_p"] = corr["Película"].loc["popularidad", "calificacion"]
    d["rho_s"] = corr["Serie"].loc["popularidad", "calificacion"]
    return d


# --------------------------------------------------------------------- figuras
def fig_concentracion(d):
    top_p, top_s = d["kp"]["pct_top10_votos"], d["ks"]["pct_top10_votos"]
    return apilada_100([
        ("Películas", [(top_p, PELI, f"10% más votado: {pct(top_p)} de los votos", False),
                       (100 - top_p, GRIS, f"90% restante: {pct(100 - top_p)}", True)]),
        ("Series", [(top_s, SERIE, f"10% más votado: {pct(top_s)} de los votos", True),
                    (100 - top_s, GRIS, f"{pct(100 - top_s)}", True)]),
    ])


def fig_visibilidad(d):
    bp, bs = d["kp"]["pct_baja_visibilidad"], d["ks"]["pct_baja_visibilidad"]
    return apilada_100([
        ("Películas", [(bp, ALERTA, f"{pct(bp)}", False),
                       (100 - bp, GRIS, f"{pct(100 - bp)} con 10 votos o más", True)]),
        ("Series", [(bs, ALERTA, f"{pct(bs)} con menos de 10 votos", False),
                    (100 - bs, GRIS, f"{pct(100 - bs)}", True)]),
    ])


def fig_traccion(d):
    g = d["gen_s"]
    motores = g["genero"].head(4).tolist()
    bajos = ["Reality", "Talk show", "Noticias"]
    filas = []
    for _, r in g.iterrows():
        color = POS if r["genero"] in motores else ALERTA if r["genero"] in bajos else GRIS
        filas.append((r["genero"], r["indice_traccion"], color, r["genero"] in motores + bajos, ""))
    return barras_h(filas, vmax=2.7, ref=(1, "x1 = rinde lo que pesa"), alto_fila=22,
                    fmt=lambda v: "x" + num(v, 1))


def fig_joyas(d):
    g = d["gen_p"]
    joyas = ["Documental", "Música", "Historia y bélico"]
    filas = []
    for _, r in g.iterrows():
        es = r["genero"] in joyas
        filas.append((r["genero"], r["pct_calif_alta"], POS if es else GRIS, es, pct(r["pct_votos"], 1)))
    return barras_h(filas, vmax=60, ref=(d["kp"]["pct_calif_alta"], f"Promedio: {pct(d['kp']['pct_calif_alta'])}"),
                    col_extra=70, alto_fila=22, titulo_extra="% de los votos")


def fig_idiomas(d):
    g = d["idi_p"]
    filas = []
    for _, r in g.iterrows():
        color = POS if r["idioma"] == "Japonés" else PELI if r["idioma"] == "Inglés" else GRIS
        filas.append((r["idioma"], r["pct_calif_alta"], color, r["idioma"] in ("Japonés", "Inglés"),
                      pct(r["pct_votos"], 1)))
    return barras_h(filas, vmax=60, ref=(d["kp"]["pct_calif_alta"], f"Promedio: {pct(d['kp']['pct_calif_alta'])}"),
                    col_extra=70, alto_fila=26, titulo_extra="% de los votos")


def fig_calidad(d):
    a = d["anual"]
    return lineas([("series", a["Serie"]["pct_calif_alta"].to_dict(), SERIE),
                   ("películas", a["Película"]["pct_calif_alta"].to_dict(), PELI)],
                  2010, 2024, 0, 80, [0, 20, 40, 60, 80])


def fig_roi(d):
    roi = d["anual"]["Película"]["roi_mediano"].to_dict()
    return lineas([("", roi, PELI)], 2010, 2024, -40, 140, [-40, 0, 40, 80, 120], cero=True,
                  marcas=[(2020, roi[2020], f"2020: {pct(roi[2020])}")])


# --------------------------------------------------------------------- HTML
CSS = f"""
@page {{ size: A4; margin: 18mm 18mm 20mm 18mm;
  @bottom-left {{ content: "StreamView Analytics | Informe ejecutivo"; font: 8.5pt 'Segoe UI', Arial, sans-serif; color: {GRIS_OSC}; }}
  @bottom-right {{ content: "Página " counter(page) " de " counter(pages); font: 8.5pt 'Segoe UI', Arial, sans-serif; color: {GRIS_OSC}; }} }}
@page portada {{ @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
* {{ box-sizing: border-box; }}
body {{ font-family: 'Segoe UI', Arial, sans-serif; color: {TINTA}; font-size: 10.5pt; line-height: 1.5; margin: 0;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
section {{ break-before: page; }}
section.portada {{ page: portada; break-before: auto; }}
h1 {{ font-size: 25pt; line-height: 1.15; margin: 0 0 8px; letter-spacing: -0.3px; }}
h2 {{ font-size: 17pt; line-height: 1.25; margin: 0 0 4px; letter-spacing: -0.2px; }}
h3 {{ font-size: 11.5pt; margin: 14px 0 5px; }}
p {{ margin: 0 0 9px; }}
.antetitulo {{ font-size: 9pt; font-weight: 700; letter-spacing: 1.2px; text-transform: uppercase; color: {POS}; margin-bottom: 6px; }}
.bajada {{ font-size: 11.5pt; color: {GRIS_OSC}; margin-bottom: 16px; }}
.fuente {{ font-size: 8.5pt; color: {GRIS_OSC}; margin-top: 4px; }}
.figura {{ margin: 12px 0 6px; }}
.figura .tit {{ font-weight: 700; font-size: 10.5pt; margin-bottom: 2px; }}
.figura .sub {{ font-size: 9pt; color: {GRIS_OSC}; margin-bottom: 6px; }}
svg {{ width: 100%; height: auto; display: block; font-family: 'Segoe UI', Arial, sans-serif; }}
svg .etq {{ font-size: 11px; fill: {TINTA}; }}
svg .val {{ font-size: 11px; fill: {TINTA}; paint-order: stroke; stroke: #FFFFFF; stroke-width: 3px; stroke-linejoin: round; }}
svg .seg {{ font-size: 11.5px; font-weight: 700; }}
svg .nota {{ font-size: 10px; fill: {GRIS_OSC}; }}
svg .eje {{ font-size: 10px; fill: {GRIS_OSC}; }}
.caja {{ border-radius: 8px; padding: 12px 16px; margin: 12px 0; }}
.caja.negocio {{ background: #E7F2F3; border-left: 4px solid {POS}; }}
.caja.alerta {{ background: #FBE9EC; border-left: 4px solid {ALERTA}; }}
.caja.neutra {{ background: #F3F4F6; }}
.caja b.rot {{ display: block; font-size: 9pt; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 4px; }}
.caja.negocio b.rot {{ color: {POS}; }} .caja.alerta b.rot {{ color: {ALERTA}; }}
.caja p:last-child, .caja ul:last-child {{ margin-bottom: 0; }}
ul {{ margin: 0 0 9px; padding-left: 18px; }} li {{ margin-bottom: 3px; }}
.cifras {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0; }}
.cifra {{ background: #F3F4F6; border-radius: 8px; padding: 12px 14px; }}
.cifra .n {{ font-size: 26pt; font-weight: 700; line-height: 1.05; }}
.cifra .d {{ font-size: 9.5pt; color: {TINTA}; margin-top: 4px; }}
.dos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 6px 0 10px; }}
th {{ text-align: left; background: {TINTA}; color: #FFFFFF; padding: 5px 8px; font-weight: 600; }}
td {{ padding: 4px 8px; border-bottom: 1px solid {REJILLA}; vertical-align: top; }}
.decision {{ border: 1px solid {REJILLA}; border-radius: 8px; padding: 8px 14px 4px; margin: 8px 0; break-inside: avoid; }}
.decision .cab {{ display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }}
.decision .num {{ background: {TINTA}; color: #FFFFFF; width: 26px; height: 26px; border-radius: 13px; text-align: center;
  line-height: 26px; font-weight: 700; flex: none; }}
.decision .nom {{ font-size: 12pt; font-weight: 700; }}
.decision .resp {{ margin-left: auto; font-size: 9pt; color: {GRIS_OSC}; font-weight: 600; }}
.decision table {{ margin: 0 0 4px; }} .decision td {{ padding: 3px 8px; }}
.decision table td:first-child {{ width: 24%; font-weight: 600; color: {GRIS_OSC}; }}
.portada-banda {{ background: {TINTA}; color: #FFFFFF; margin: -18mm -18mm 0; padding: 22mm 18mm 14mm; }}
.portada-banda .antetitulo {{ color: {SERIE}; }}
.portada-banda h1 {{ color: #FFFFFF; font-size: 28pt; }}
.portada-banda .bajada {{ color: #D6D9DE; margin: 0; }}
.meta {{ font-size: 9pt; color: {GRIS_OSC}; margin: 12px 0 16px; line-height: 1.6; }}
.leyenda {{ font-size: 9pt; color: {GRIS_OSC}; margin: 2px 0 6px; }}
.leyenda i {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin: 0 4px -1px 10px; }}
.leyenda i:first-child {{ margin-left: 0; }}
a {{ color: {POS}; }}
ol {{ margin: 0 0 9px; padding-left: 20px; }} ol li {{ margin-bottom: 5px; }}
.captura {{ height: 88mm; overflow: hidden; border: 1px solid {REJILLA}; border-radius: 6px; margin: 10px 0 4px; }}
.captura img {{ width: 100%; display: block; }}
"""


def figura(titulo, sub, svg, fuente="Fuente: catálogo StreamView 2010-2025 (31.991 títulos). Elaboración propia.",
           leyenda=""):
    return (f'<div class="figura"><div class="tit">{titulo}</div><div class="sub">{sub}</div>{leyenda}{svg}'
            f'<div class="fuente">{fuente}</div></div>')


def ley(*items):
    return '<div class="leyenda">' + "".join(f'<i style="background:{c}"></i>{t}' for c, t in items) + "</div>"


def construir(d):
    k, kp, ks = d["k"], d["kp"], d["ks"]
    gs = d["gen_s"].set_index("genero")
    gp = d["gen_p"].set_index("genero")
    ip = d["idi_p"].set_index("idioma")
    isr = d["idi_s"]
    ap, as_ = d["anual"]["Película"], d["anual"]["Serie"]
    x = lambda v: "x" + num(v, 1)
    bajos = ["Reality", "Talk show", "Noticias"]

    def tabla(cab, filas, anchos=None):
        anchos = anchos or [""] * len(cab)
        th = "".join(f'<th style="width:{a}">{c}</th>' if a else f"<th>{c}</th>" for c, a in zip(cab, anchos))
        tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in f) + "</tr>" for f in filas)
        return f"<table><tr>{th}</tr>{tr}</table>"

    def encabezado(n, ante, titulo, bajada):
        num_txt = f"{n}. " if n else ""
        return (f'<div class="antetitulo">{num_txt}{ante}</div><h2>{titulo}</h2>'
                f'<p class="bajada">{bajada}</p>')

    h = []
    # ================================================================ portada y resumen
    h.append(f"""
<section class="portada">
  <div class="portada-banda">
    <div class="antetitulo">Informe ejecutivo para el directorio y la gerencia general</div>
    <h1>StreamView no necesita más títulos: necesita que los títulos correctos sean descubiertos</h1>
    <p class="bajada">Qué contenido genera interacción, cuál valora el público y qué parte del catálogo
    nadie está alcanzando a ver.</p>
  </div>
  <div class="meta">ADY1104 Visualización de Datos | Evaluación Parcial N°1 (encargo) | Duoc UC, sede Puerto Montt<br>
  Equipo consultor: Claudio Aro, Guillermo Cerda y Manuel Díaz | Docente: Claudio Andrés Gonzalez Penaloza<br>
  Septiembre de 2026</div>

  <h2>La respuesta en un minuto</h2>
  <p>Analizamos {num(k['titulos'])} películas y series estrenadas entre 2010 y 2025. El catálogo es amplio y de
  buena calidad, pero <b>la atención del público se concentra en muy pocos títulos</b> y buena parte del contenido
  mejor evaluado pasa inadvertido. El problema no es de cantidad ni de calidad: es de descubrimiento.</p>

  <div class="cifras">
    <div class="cifra"><div class="n">{pct(ks['pct_top10_votos'])}</div>
      <div class="d">de la interacción en series se la lleva solo el 10% de los títulos (en películas, el {pct(kp['pct_top10_votos'])}).</div></div>
    <div class="cifra"><div class="n" style="color:{ALERTA}">{pct(ks['pct_baja_visibilidad'])}</div>
      <div class="d">de las series tiene menos de 10 votos: para el público, prácticamente no existen.</div></div>
    <div class="cifra"><div class="n" style="color:{POS}">{pct(gp.loc['Documental','pct_calif_alta'])}</div>
      <div class="d">de los documentales está bien evaluado, el doble que el promedio de películas ({pct(kp['pct_calif_alta'])}), y casi no recibe votos.</div></div>
  </div>

  <div class="caja negocio"><b class="rot">Lo que pedimos decidir</b>
  <ul>
    <li><b>Exponer las "joyas ocultas".</b> Crear en la interfaz filas de títulos bien evaluados y poco vistos, y un
    ranking que combine popularidad y calidad. <i>Responsable: Producto / Experiencia de usuario.</i></li>
    <li><b>Reorientar la adquisición de contenido.</b> Priorizar ciencia ficción, acción, misterio, crimen y anime;
    revisar la inversión en reality y talk show. <i>Responsable: Contenidos.</i></li>
    <li><b>Medir el comportamiento real.</b> Integrar reproducciones, abandono y suscripciones para confirmar estas
    señales y seguir las metas. <i>Responsable: Analítica / TI.</i></li>
  </ul></div>
  <p class="fuente">Cómo leer este documento: la página 1 basta para decidir. Las secciones 1 a 5 explican el problema
  y la evidencia; las secciones 6 a 9, cómo se construyó la solución; la sección 10 detalla cada decisión con su
  responsable, meta y plazo.</p>
</section>""")

    # ================================================================ 1 a 3
    h.append(f"""
<section>
  {encabezado(1, "Problema de negocio", "Un gran catálogo no retiene si el usuario no lo descubre",
              "Por qué hicimos este análisis.")}
  <p>StreamView Analytics es una plataforma internacional de streaming que vive de suscripciones: gana cuando la
  persona encuentra algo que ver y se queda. Hasta hoy no existía una vista que conectara tres cosas: lo que
  ofrecemos, lo que genera interacción y lo que el público valora. Sin esa vista, las decisiones de compra de
  contenido y de recomendación se toman mirando solo lo más popular, y se corre el riesgo de pagar por un catálogo
  que el público no alcanza a ver.</p>

  <div class="antetitulo" style="margin-top:14px">2. Objetivos del proyecto</div>
  <p><b>Objetivo general:</b> entregar a StreamView una solución de visualización que muestre qué contenido genera
  interacción, cuál satisface al público y cuál no se está descubriendo, para apoyar decisiones de retención.</p>
  {tabla(["Objetivo específico", "Dónde se responde"], [
      ["Medir cuán concentrada está la interacción en el catálogo.", "Sección 5.1"],
      ["Identificar qué géneros rinden más o menos que su peso en la oferta.", "Sección 5.2"],
      ["Encontrar contenido de alta calidad y baja interacción (joyas ocultas).", "Sección 5.3"],
      ["Comparar calidad e interacción por idioma y su evolución en el tiempo.", "Secciones 5.4 y 5.5"],
      ["Entregar un dashboard para que cada gerencia explore el detalle por su cuenta.", "Sección 8"],
      ["Proponer decisiones concretas, con responsable, meta y plazo.", "Sección 10"]], ["72%", ""])}

  <div class="antetitulo" style="margin-top:14px">3. Audiencia objetivo y propósito comunicacional</div>
  {tabla(["Audiencia", "Qué necesita", "Producto que recibe"], [
      ["<b>Directorio y gerencia general</b> (principal)", "Decidir con poco tiempo y sin detalle técnico.", "Este informe y la presentación: conclusión primero."],
      ["<b>Gerencias de contenidos y de producto</b>", "Explorar el detalle por género, idioma y título.", "Dashboard interactivo."],
      ["<b>Equipo de analítica</b>", "Revisar y reproducir el trabajo.", "Informe técnico y archivos del proyecto."]],
      ["30%", "32%", ""])}
  <p><b>Propósito comunicacional:</b> doble. <b>Persuadir</b> a la gerencia para aprobar tres decisiones y
  <b>habilitar</b> a cada área para responder sus propias preguntas con el dashboard.</p>

  <h3>Cómo leer este informe</h3>
  {tabla(["Término", "Qué significa"], [
      ["<b>Interacción</b>", "Cantidad de votos que recibe un título. Más votos indican que más personas lo vieron y se animaron a calificarlo."],
      ["<b>Bien evaluado</b>", "Título con nota 7 o más, en una escala de 1 a 10."],
      ["<b>Tracción</b>", "Cuánto rinde un género frente a su peso en el catálogo. \"x2\" significa que atrae el doble de interacción de la que le correspondería por su tamaño; \"x0,5\", la mitad."],
      ["<b>Joya oculta</b>", "Género o título con alta calidad y poca interacción: contenido valioso que el público no está encontrando."]],
      ["22%", ""])}
  <p>Cada gráfico tiene un título que dice la conclusión, y los colores tienen un solo significado en todo el informe:</p>
  {ley((POS, 'oportunidad'), (ALERTA, 'alerta'), (GRIS, 'contexto'), (PELI, 'películas'), (SERIE, 'series'))}
</section>""")

    # ================================================================ 4 fuentes
    h.append(f"""
<section>
  {encabezado(4, "Fuentes de datos", "Dos catálogos integrados en una sola base comparable",
              "Qué datos usamos, qué variables importan y cómo los preparamos.")}
  <p>StreamView entregó dos archivos: el catálogo de <b>películas</b> y el de <b>series</b>, con 16.000 registros
  cada uno, estrenados entre 2010 y 2025 (mil títulos por año y tipo). Los integramos en un solo catálogo de
  <b>{num(k['titulos'])} títulos</b>, tras eliminar 9 registros duplicados.</p>

  <h3>Variables utilizadas</h3>
  {tabla(["Variable", "Qué describe", "Para qué la usamos"], [
      ["Tipo, título, año de estreno", "Identificación del contenido.", "Separar películas y series; ver tendencias por año."],
      ["Género", "Hasta varios géneros por título.", "Tracción y joyas ocultas (secciones 5.2 y 5.3)."],
      ["Idioma original y país", "Origen del contenido.", "Comparar calidad por idioma (sección 5.4)."],
      ["Votos (vote_count)", "Cuántas personas calificaron el título.", "Medida de interacción y visibilidad."],
      ["Nota (vote_average)", "Promedio de las calificaciones, de 1 a 10.", "Medida de calidad percibida."],
      ["Popularidad", "Índice de interés reciente del sitio de origen.", "Comparar popularidad con calidad."],
      ["Presupuesto y recaudación", "Solo películas; montos en dólares.", "Retorno en taquilla (sección 5.5)."]],
      ["26%", "36%", ""])}

  <h3>Cómo preparamos los datos</h3>
  <ul>
    <li><b>Géneros unificados:</b> cada archivo nombraba los géneros de forma distinta; los llevamos a 21 géneros en español.</li>
    <li><b>Notas sin votos:</b> un título con nota 0 y ningún voto se trata como "sin evaluar", no como una mala nota.</li>
    <li><b>Nota corregida por cantidad de votos:</b> para que un título con 2 votos y nota 10 no supere a uno con
    20.000 votos y nota 8,5, usamos una calificación ponderada, similar a la de IMDb.</li>
    <li><b>Columnas descartadas:</b> las que repetían información o venían vacías (por ejemplo, una segunda columna de nota idéntica a la primera).</li>
    <li><b>Datos financieros:</b> el retorno solo se calcula para las {num(3362)} películas con presupuesto y recaudación informados.</li>
  </ul>

  <div class="caja alerta"><b class="rot">Lo que hay que tener presente</b>
  <p>Las notas y los votos provienen de <b>TMDB</b>, una comunidad pública de cine y series en internet (los
  identificadores de los archivos coinciden con los de ese sitio), no de los suscriptores de StreamView. Por eso los
  usamos como una <b>señal aproximada</b> del interés del público. Los archivos no incluyen reproducciones,
  suscripciones ni dispositivos: confirmarlo con datos propios es la tercera decisión que proponemos.</p></div>
</section>""")

    # ================================================================ 5.1 concentración
    h.append(f"""
<section>
  {encabezado("5", "Análisis exploratorio | 5.1 Concentración", "Muy pocos títulos se llevan casi toda la atención",
              "Si todo el catálogo recibiera la misma atención, el 10% de los títulos se llevaría el 10% de los votos. La realidad está muy lejos de eso.")}
  {figura("El 10% de los títulos concentra entre 7 y 9 de cada 10 votos",
          "Reparto de los votos entre el 10% de títulos más votados y el resto, por tipo de contenido.",
          fig_concentracion(d))}
  {figura("6 de cada 10 series tienen menos de 10 votos",
          "Porcentaje de títulos con menos de 10 votos (baja visibilidad), por tipo de contenido.",
          fig_visibilidad(d))}
  <div class="caja negocio"><b class="rot">Qué significa para el negocio</b>
  <p>Pagamos por miles de títulos que el público no está encontrando. En series el problema es mayor:
  {num(ks['titulos'] * ks['pct_baja_visibilidad'] / 100)} series tienen menos de 10 votos. Mientras la recomendación
  se base solo en lo más popular, esa concentración se reforzará sola: lo visible se vuelve más visible y el
  resto del catálogo sigue escondido.</p></div>
</section>""")

    # ================================================================ 5.2 tracción
    h.append(f"""
<section>
  {encabezado("", "5.2 Oferta vs. interacción", "Invertimos en géneros que el público casi no busca",
              "La tracción compara cuánta interacción atrae cada género con cuánto pesa en el catálogo. Sobre la línea x1, el género rinde más de lo que pesa; bajo ella, menos.")}
  {figura("En series, ciencia ficción rinde 2,5 veces su peso; reality y talk show, casi nada",
          "Tracción de cada género de series: % de los votos dividido por % del catálogo que ocupa.",
          fig_traccion(d),
          leyenda=ley((POS, 'motores de interacción'), (ALERTA, 'baja tracción'), (GRIS, 'resto de los géneros')))}
  <div class="dos">
    <div class="caja negocio"><b class="rot">Oportunidad</b>
    <p>Ciencia ficción y fantasía ({x(gs.loc['Ciencia ficción y fantasía','indice_traccion'])}), acción y aventura
    ({x(gs.loc['Acción y aventura','indice_traccion'])}), misterio ({x(gs.loc['Misterio','indice_traccion'])}) y
    crimen ({x(gs.loc['Crimen','indice_traccion'])}) atraen mucha más interacción de la que les correspondería. En
    películas el patrón es similar: ciencia ficción ({x(gp.loc['Ciencia ficción y fantasía','indice_traccion'])}) y
    acción ({x(gp.loc['Acción y aventura','indice_traccion'])}) lideran.</p></div>
    <div class="caja alerta"><b class="rot">Alerta</b>
    <p>Reality, talk show y noticias ocupan el {pct(gs.loc[bajos,'pct_titulos'].sum())} del catálogo de series y
    reciben apenas el {pct(gs.loc[bajos,'pct_votos'].sum(), 1)} de los votos. Estos formatos pueden verse sin que
    nadie los califique, por lo que conviene confirmarlo con reproducciones antes de reducir la inversión.</p></div>
  </div>
  <p class="fuente">Nota: un título con varios géneros cuenta en cada uno de ellos, por lo que el peso de cada género se
  mide sobre el total de asignaciones título-género.</p>
</section>""")

    # ================================================================ 5.3 joyas
    h.append(f"""
<section>
  {encabezado("", "5.3 Joyas ocultas", "Tenemos contenido muy bien valorado que nadie está viendo",
              "Los géneros con mayor proporción de películas bien evaluadas no son los que reciben más votos.")}
  {figura("Documental, música e historia: calidad alta, interacción mínima",
          "Películas: % de títulos bien evaluados (nota 7 o más) por género. A la derecha, % de todos los votos de películas que recibe el género.",
          fig_joyas(d), leyenda=ley((POS, 'joyas ocultas'), (GRIS, 'resto de los géneros')),
          fuente="Fuente: catálogo StreamView 2010-2025 (31.991 títulos). Animación y familiar también tienen alta calidad, "
                 "pero reciben interacción acorde a su peso en el catálogo, por lo que no se consideran ocultas.")}
  <div class="caja negocio"><b class="rot">Qué significa para el negocio</b>
  <p>El {pct(gp.loc['Documental','pct_calif_alta'])} de los documentales está bien evaluado, el doble que el promedio de
  películas, pero el género recibe apenas el {pct(gp.loc['Documental','pct_votos'], 1)} de los votos. Música e historia
  repiten el patrón. Es contenido que ya pagamos y que, bien expuesto, puede mejorar la experiencia sin costo de
  adquisición adicional.</p></div>
  <div class="caja neutra"><b class="rot">Lo más popular no es lo mejor evaluado</b>
  <p>La relación entre popularidad y nota es débil: en una escala de 0 (ninguna relación) a 1 (relación perfecta),
  llega apenas a {num(d['rho_p'], 2)} en películas y {num(d['rho_s'], 2)} en series. Un sistema que recomienda solo
  por popularidad esconde la calidad de forma sistemática.</p></div>
</section>""")

    # ================================================================ 5.4 idiomas
    h.append(f"""
<section>
  {encabezado("", "5.4 Idiomas", "El contenido japonés es el mejor evaluado; el inglés, el más visto",
              "El inglés concentra casi toda la interacción, pero no es donde está la mejor calidad percibida.")}
  {figura("La mitad de las películas japonesas está bien evaluada, frente a 1 de cada 5 en inglés",
          "Películas: % de títulos bien evaluados por idioma original (idiomas con 200 títulos evaluados o más). A la derecha, % de los votos de películas.",
          fig_idiomas(d), leyenda=ley((POS, 'mayor calidad'), (PELI, 'mayor interacción'), (GRIS, 'resto de los idiomas')))}
  <div class="caja negocio"><b class="rot">Qué significa para el negocio</b>
  <p>El {pct(ip.loc['Japonés','pct_calif_alta'])} de las películas japonesas está bien evaluado, frente al
  {pct(ip.loc['Inglés','pct_calif_alta'])} en inglés, que concentra el {pct(ip.loc['Inglés','pct_votos'])} de los
  votos. El coreano ({pct(ip.loc['Coreano','pct_calif_alta'])}) y el español ({pct(ip.loc['Español','pct_calif_alta'])})
  también superan al inglés. En series, el {pct(isr.loc['Japonés','pct_calif_alta'])} del contenido japonés está bien
  evaluado. Gran parte de ese contenido es animación: <b>el anime es una oportunidad de diferenciación</b>.</p></div>
  <p class="fuente">Precaución: en series, el orden de los idiomas cambia según el mínimo de votos que se exija; la
  conclusión sólida es la del japonés en películas y la del anime.</p>
</section>""")

    # ================================================================ 5.5 tiempo
    h.append(f"""
<section>
  {encabezado("", "5.5 Evolución 2010-2024", "La calidad no es el problema; la rentabilidad sí preocupa",
              "Cómo han cambiado la calidad del catálogo y el retorno de las películas según su año de estreno.")}
  <div class="dos">
    {figura("La proporción de títulos bien evaluados tiende a subir",
            "% de títulos bien evaluados por año de estreno.", fig_calidad(d), fuente="Fuente: catálogo StreamView. Se excluye 2025 por tener pocos votos.")}
    {figura("El retorno de las películas no se recupera",
            "Retorno mediano en taquilla de las películas (recaudación menos presupuesto, sobre el presupuesto).", fig_roi(d),
            fuente="Fuente: 3.362 películas con presupuesto y recaudación informados.")}
  </div>
  <div class="dos">
    <div class="caja negocio"><b class="rot">Calidad</b>
    <p>Entre 2010 y 2024, las películas bien evaluadas pasan de {pct(ap.loc[2010,'pct_calif_alta'])} a
    {pct(ap.loc[2024,'pct_calif_alta'])} y las series, de {pct(as_.loc[2010,'pct_calif_alta'])} a
    {pct(as_.loc[2024,'pct_calif_alta'])}, con algunos retrocesos. Parte del alza puede deberse a que los títulos
    recientes tienen menos votos. Aun así, el catálogo no está empeorando.</p></div>
    <div class="caja alerta"><b class="rot">Rentabilidad</b>
    <p>El retorno mediano de las películas cayó a {pct(ap.loc[2020,'roi_mediano'])} en 2020, con la pandemia, y en
    2024 llega a {pct(ap.loc[2024,'roi_mediano'])}, bajo el 100% habitual de la década anterior. Mide taquilla, no el
    valor en la plataforma, pero refuerza la idea de sacar más provecho al catálogo que ya existe.</p></div>
  </div>
  <p class="fuente">Por país de origen, Estados Unidos participa en {num(10955)} títulos; Japón, China y Corea del Sur
  pesan mucho más en series que en películas. El detalle está en la página "Idiomas y origen" del dashboard.</p>
</section>""")

    # ================================================================ 6 justificación
    h.append(f"""
<section>
  {encabezado(6, "Justificación de las representaciones gráficas", "Cada gráfico se eligió por la pregunta que responde",
              "Para una audiencia no técnica elegimos las formas que el ojo compara con más precisión y descartamos las que exigen formación estadística.")}
  {tabla(["Pregunta", "Gráfico elegido", "Por qué", "Alternativa descartada"], [
      ["¿Qué parte de los votos se lleva el 10% más votado?", "Barra 100% apilada (5.1)", "Muestra una parte y su resto de un vistazo.", "Curva de Lorenz: correcta, pero técnica; queda en el dashboard y el informe técnico."],
      ["¿Cuántos títulos casi no se ven?", "Barra 100% apilada (5.1)", "Una sola proporción destacada en rojo.", "Torta: los ángulos se comparan con poca precisión."],
      ["¿Qué géneros rinden más que su peso?", "Barras horizontales ordenadas con línea x1 (5.2)", "La longitud desde cero se compara con precisión; los nombres largos se leen sin girar.", "Escala logarítmica y matriz de burbujas: exigen formación estadística."],
      ["¿Dónde está la calidad escondida?", "Barras ordenadas + columna de % de votos (5.3)", "Calidad y visibilidad en la misma fila, sin cruzar ejes.", "Matriz de burbujas por cuadrantes: se mantiene en el dashboard para explorar."],
      ["¿Qué idioma tiene mejor calidad?", "Barras ordenadas (5.4)", "Ranking directo con el promedio como referencia.", "Mapa: el idioma no es una variable geográfica."],
      ["¿Cómo evolucionan calidad y retorno?", "Dos gráficos de línea (5.5)", "La pendiente muestra la tendencia en el tiempo.", "Un gráfico de dos ejes: mezcla escalas y confunde."]],
      ["25%", "21%", "27%", ""])}

  <h3>Principios de percepción visual y atributos aplicados</h3>
  {tabla(["Principio", "Cómo se aplicó"], [
      ["<b>Atención preatentiva</b>", "El color se usa solo donde hay un mensaje; el resto va en gris. El ojo llega primero al dato importante."],
      ["<b>Posición y longitud</b>", "Son los atributos que se comparan con más precisión (Cleveland y McGill), por eso casi todo son barras que parten de cero, ordenadas de mayor a menor."],
      ["<b>Color con un solo significado</b>", "Azul petróleo = oportunidad, rojo = alerta, gris = contexto; azul pizarra = películas y ámbar = series en todos los productos."],
      ["<b>Accesibilidad</b>", "Se evitó el par verde y rojo, el más difícil para personas con daltonismo; la paleta se verificó con un simulador de daltonismo. Ningún dato se identifica solo por color: todo lleva etiqueta."],
      ["<b>Contraste y tamaño</b>", "Textos en tinta oscura sobre fondo claro; las tres cifras clave de la página 1 van en tamaño grande para leerse primero."],
      ["<b>Gestalt</b>", "Proximidad: cada valor junto a su barra, sin leyendas lejanas. Similitud: mismo color, mismo significado. Cerramiento: las cajas agrupan la lectura de negocio de cada gráfico."],
      ["<b>Jerarquía visual</b>", "Cada hallazgo sigue el mismo orden: sección, título-mensaje, bajada, gráfico, fuente y lectura de negocio."],
      ["<b>Baja carga cognitiva</b>", "Un mensaje por gráfico, sin 3D, sin rejillas innecesarias y con formato numérico chileno (coma decimal)."]],
      ["26%", ""])}
</section>""")

    # ================================================================ 7 narrativa
    h.append(f"""
<section>
  {encabezado(7, "Narrativa visual (Data Storytelling)", "Una idea central contada en tres actos",
              "Todos los productos cuentan la misma historia, adaptada a cada audiencia.")}
  <div class="caja neutra"><b class="rot">Idea central</b>
  <p style="font-size:12.5pt"><b>"StreamView no necesita más títulos: necesita que los títulos correctos sean descubiertos."</b></p></div>
  {tabla(["Acto", "Qué cuenta", "Dónde aparece"], [
      ["<b>1. Contexto</b>", "El negocio depende de que el usuario encuentre qué ver; hoy no hay una vista que conecte oferta, interacción y calidad.", "Secciones 1 a 4; presentación, diapositivas 1 a 5."],
      ["<b>2. Conflicto</b>", "La atención se concentra, la oferta no está alineada y la calidad está escondida.", "Sección 5; presentación, diapositivas 6 a 10."],
      ["<b>3. Resolución</b>", "Hacer visible el valor que ya existe y medirlo con datos propios.", "Sección 10; presentación, diapositivas 12 a 16; dashboard."]],
      ["18%", "46%", ""])}

  <h3>Decisiones de narrativa</h3>
  <ul>
    <li><b>Pirámide invertida:</b> la conclusión y las decisiones van en la página 1, porque la gerencia decide con poco tiempo.
    Descartamos el relato cronológico del análisis, que deja la conclusión al final.</li>
    <li><b>Títulos-mensaje:</b> cada gráfico dice su conclusión en el título; el gráfico la demuestra.</li>
    <li><b>Lenguaje de negocio:</b> "tracción" y "joya oculta" en lugar de términos estadísticos, definidos en la sección 3.</li>
    <li><b>Del dato a la acción:</b> cada hallazgo termina en una caja "Qué significa para el negocio" y conecta con una decisión.</li>
  </ul>

  <h3>Recursos orales, escritos y visuales</h3>
  {tabla(["Recurso", "Producto", "Función en la historia"], [
      ["Escrito", "Este informe ejecutivo", "Documento de decisión y respaldo para el directorio."],
      ["Oral y visual", "Presentación ejecutiva (16 diapositivas, 10 minutos)", "Cuenta la historia en tres actos con los mismos gráficos y colores."],
      ["Interactivo", "Dashboard en Streamlit", "Permite a cada gerencia comprobar y profundizar los hallazgos."]],
      ["18%", "38%", ""])}
</section>""")

    # ================================================================ 8 dashboard
    img = (RAIZ / "images" / "dashboard_02.png").as_uri()
    h.append(f"""
<section>
  {encabezado(8, "Diseño e implementación del dashboard interactivo", "Un dashboard para que cada gerencia explore por su cuenta",
              "Este informe resume las conclusiones; el dashboard permite revisar el detalle sin depender del equipo técnico.")}
  <p><b>Tecnología:</b> Python, Streamlit y Plotly, publicado en Streamlit Community Cloud. Usa los mismos datos y el
  mismo código de cálculo que este informe, por lo que las cifras coinciden. <b>Acceso:</b>
  <a href="{URL_DASHBOARD}">{URL_DASHBOARD}</a></p>
  <div class="captura"><img src="{img}" alt="Página Géneros del dashboard"></div>
  <p class="fuente">Página "Géneros: oferta vs interacción": indicadores clave arriba, filtros a la izquierda y matriz
  interactiva de géneros.</p>
  <div class="dos">
    <div>
      <h3>Componentes</h3>
      <ul>
        <li><b>6 indicadores clave (KPI):</b> títulos, votos, calificación ponderada, % bien evaluados, % de baja
        visibilidad y % de votos del 10% más votado. Cada uno se compara con el catálogo completo.</li>
        <li><b>5 filtros globales:</b> tipo, años, género, idioma y votos mínimos, con botón para restablecerlos.</li>
        <li><b>6 páginas:</b> resumen, géneros, idiomas y origen, tendencias, explorador de títulos y metodología.</li>
        <li><b>Interacción:</b> selección de géneros con clic o lazo, búsqueda de títulos, interruptor "Solo joyas
        ocultas", detalle al pasar el cursor y descarga de la selección en CSV.</li>
      </ul>
    </div>
    <div>
      <h3>Si usted quiere...</h3>
      {tabla(["Objetivo", "Vaya a"], [
          ["Ver el estado general", "<b>1. Resumen ejecutivo</b>"],
          ["Saber qué géneros rinden más", "<b>2. Géneros</b>: al elegir un género aparecen sus mejores títulos."],
          ["Obtener la lista de joyas ocultas", "<b>5. Explorador</b>: active \"Solo joyas ocultas\" y descargue la lista."],
          ["Filtrar por tipo, año o idioma", "Barra lateral; los filtros aplican a todas las páginas."]], ["42%", ""])}
    </div>
  </div>
</section>""")

    # ================================================================ 9 evaluación crítica
    h.append(f"""
<section>
  {encabezado(9, "Evaluación crítica de la solución", "Fortalezas, limitaciones y cómo mejorar",
              "Una revisión honesta de lo que la solución resuelve y de lo que todavía no.")}
  {tabla(["Fortalezas", "Limitaciones", "Oportunidades de mejora"], [
      ["<b>Una sola fuente de verdad:</b> informe, presentación y dashboard salen del mismo código y los mismos datos.",
       "<b>Votos externos:</b> la interacción se mide con votos de TMDB, no con reproducciones de StreamView.",
       "Integrar datos propios de reproducción, abandono, suscripción y dispositivo."],
      ["<b>Cifras verificadas:</b> 76 cifras del proyecto se comprueban automáticamente contra los datos.",
       "<b>Muestra equilibrada:</b> mil títulos por año y tipo; no permite analizar el crecimiento del volumen de estrenos.",
       "Validar el dashboard con usuarios de cada gerencia (prueba de uso) y ajustar según sus preguntas."],
      ["<b>Diseño accesible y coherente:</b> paleta verificada para daltonismo y un significado por color en todos los productos.",
       "<b>Años recientes:</b> los títulos de 2024 y 2025 acumulan pocos votos; 2025 se excluye de las tendencias.",
       "Unificar el formato decimal en las tablas del dashboard (hoy muestran punto) y traducir los países que siguen en inglés."],
      ["<b>Reproducible:</b> cualquier persona puede regenerar datos, gráficos e informe desde el repositorio.",
       "<b>Rentabilidad parcial:</b> solo 3.362 películas informan presupuesto y recaudación, y el dato mide taquilla.",
       "Actualizar los datos de forma automática y agregar acceso con usuario para uso interno."]],
      ["33%", "34%", ""])}
  <div class="caja neutra"><b class="rot">Principales decisiones de diseño y su razón</b>
  <ul>
    <li><b>Dos productos en vez de uno:</b> un documento para decidir y un dashboard para explorar, porque la gerencia
    y las áreas operativas necesitan cosas distintas. Un único dashboard para todos sobrecargaría a quien decide.</li>
    <li><b>Gráficos distintos según la audiencia:</b> en este informe, barras simples; en el dashboard, la matriz de
    burbujas y la curva de Lorenz, más completas, para quienes exploran.</li>
    <li><b>Transparencia sobre el origen de los datos:</b> declarar que los votos vienen de TMDB cambió las metas: ahora
    se medirán con reproducciones propias.</li>
  </ul></div>
</section>""")

    # ================================================================ 10 conclusiones y recomendaciones
    def decision(n, nombre, resp, que, porque, meta, plazo):
        return f"""<div class="decision"><div class="cab"><span class="num">{n}</span><span class="nom">{nombre}</span>
        <span class="resp">{resp}</span></div><table>
        <tr><td>Qué hacer</td><td>{que}</td></tr><tr><td>Por qué</td><td>{porque}</td></tr>
        <tr><td>Cómo sabremos si funciona</td><td>{meta}</td></tr><tr><td>Plazo</td><td>{plazo}</td></tr></table></div>"""

    h.append(f"""
<section>
  {encabezado(10, "Conclusiones y recomendaciones", "Tres decisiones para que el catálogo trabaje a favor de la retención",
              "Lo que aprendimos y lo que proponemos hacer.")}
  <h3>Conclusiones</h3>
  <ol>
    <li><b>La interacción está concentrada:</b> el 10% de los títulos reúne el {pct(kp['pct_top10_votos'])} de los votos en
    películas y el {pct(ks['pct_top10_votos'])} en series; el {pct(ks['pct_baja_visibilidad'])} de las series casi no se ve.</li>
    <li><b>La oferta no está alineada con la demanda:</b> ciencia ficción, acción, misterio y crimen rinden bastante más
    que su peso; reality, talk show y noticias, mucho menos.</li>
    <li><b>La calidad está escondida:</b> documentales, música, historia y el contenido japonés están entre lo mejor
    evaluado y reciben poca atención; popularidad y calidad casi no se relacionan.</li>
    <li><b>El catálogo no está empeorando,</b> pero la rentabilidad de las películas aún no se recupera: conviene sacar
    más provecho a lo que ya existe antes de comprar más.</li>
  </ol>
  {decision(1, "Exponer las joyas ocultas", "Producto / Experiencia de usuario",
    "Crear filas de recomendación con títulos bien evaluados y poco vistos, y un ranking que combine popularidad y calidad. Probarlo primero con un grupo de usuarios y compararlo con la interfaz actual.",
    f"El 10% de los títulos concentra hasta el {pct(ks['pct_top10_votos'])} de la interacción y hay géneros de alta calidad casi invisibles (secciones 5.1 y 5.3).",
    f"Aumentar el % del catálogo con al menos una reproducción en 90 días. Referencia actual aproximada: el {pct(ks['pct_baja_visibilidad'])} de las series tiene menos de 10 votos.",
    "Piloto en 3 meses; decisión de extenderlo al mes 4.")}
  {decision(2, "Reorientar la adquisición de contenido", "Contenidos",
    "Priorizar ciencia ficción, acción, misterio, crimen y anime en las próximas compras y renovaciones. Revisar la inversión en reality y talk show, confirmando antes con datos de reproducción.",
    "Estos géneros atraen hasta 2,5 veces la interacción que les correspondería por su peso; el contenido japonés es el mejor evaluado (secciones 5.2 y 5.4).",
    "Que las nuevas adquisiciones rindan al menos lo que pesan en el catálogo (tracción de x1,0 o más), medido con reproducciones.",
    "Desde el próximo ciclo de compras.")}
  {decision(3, "Medir el comportamiento real", "Analítica / TI",
    "Incorporar al dashboard datos propios de reproducción, abandono, suscripción y dispositivo, para reemplazar los votos externos como medida principal.",
    "Hoy dependemos de votos de una comunidad externa (TMDB), que solo aproximan lo que ocurre en la plataforma (sección 4).",
    "Dashboard de retención operativo y metas de las decisiones 1 y 2 medidas con datos propios.",
    "6 meses.")}
  <p class="fuente">Documentos complementarios: presentación ejecutiva (docs/Presentación_Ejecutiva_StreamView.pdf),
  informe técnico con la metodología completa (docs/Informe_Tecnico_StreamView.pdf), verificación de cifras
  (docs/VALIDACION.md) y repositorio del proyecto: github.com/apotheosisss/StreamView_EP1_VisualizacionDatos.</p>
</section>""")

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Informe ejecutivo StreamView</title>
<style>{CSS}</style></head><body>{''.join(h)}</body></html>"""


def navegador():
    candidatos = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                  r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
    for c in candidatos:
        if Path(c).exists():
            return c
    for n in ("msedge", "google-chrome", "chromium", "chrome"):
        if shutil.which(n):
            return shutil.which(n)
    raise SystemExit("No se encontró Edge ni Chrome para imprimir el PDF.")


def main():
    HTML.write_text(construir(calcular()), encoding="utf-8")
    subprocess.run([navegador(), "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True)
    print(f"HTML: {HTML}\nPDF:  {PDF}")


if __name__ == "__main__":
    main()
