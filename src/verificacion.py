"""
Verificación automática de las cifras citadas en el informe (paper).

Recalcula cada afirmación cuantitativa desde data/processed y compara con el
valor escrito en el informe (redondeado como allí aparece). Si una cifra no
coincide, el script lo informa y termina con código de error.

Uso:
    python -m src.verificacion
"""
import sys

import numpy as np
import pandas as pd

from src import config as cfg
from src import metricas as met


def main():
    cat, gen, pai = met.cargar_procesados()
    pel_raw = pd.read_csv(cfg.ARCHIVO_PELICULAS)
    tg = met.tabla_generos(cat, gen).set_index(["tipo", "genero"])
    kp = {t: met.kpis(cat[cat.tipo == t]) for t in ["Película", "Serie"]}
    k0 = met.kpis(cat)
    ev = cat[cat.votos > 0]
    ti = met.tabla_idiomas(cat).set_index(["tipo", "idioma"])
    ta = met.tabla_anual(cat).set_index(["tipo", "anio"])
    corr = met.correlaciones(cat)
    pc = pai.groupby(["pais", "tipo"]).size()

    def pct_tit_votos(tipo, generos):
        c = cat[cat.tipo == tipo]
        ids = gen[(gen.tipo == tipo) & gen.genero.isin(generos)].id.unique()
        m = c.id.isin(ids)
        return m.mean() * 100, c[m].votos.sum() / c.votos.sum() * 100

    ser = cat[cat.tipo == "Serie"]
    generos_unif = set(gen.genero) - {"Sin clasificar"}
    roi_n = cat[cat.roi.notna()].groupby("anio").size()
    jp_p = ev[(ev.tipo == "Película") & (ev.idioma == "Japonés")]
    jp_s = ev[(ev.tipo == "Serie") & (ev.idioma == "Japonés")]
    pe = ev[ev.tipo == "Película"]
    q75 = ev.groupby("tipo")["calif_ponderada"].transform(lambda s: s.quantile(0.75))
    med = ev.groupby("tipo")["votos"].transform("median")
    joyas = ev[(ev.calif_ponderada >= q75) & (ev.votos < med)]

    # (descripción, valor calculado, valor en el informe, decimales)
    c = [
        ("Títulos integrados", len(cat), 31991, 0),
        ("Series tras duplicados", (cat.tipo == "Serie").sum(), 15991, 0),
        ("Géneros unificados", len(generos_unif), 21, 0),
        ("Asignaciones título-género", len(gen), 65788, 0),
        ("Relaciones título-país", len(pai), 37628, 0),
        ("Títulos no latinos", (~cat.titulo_latino).sum(), 704, 0),
        ("Películas 0 votos", ((cat.tipo == "Película") & (cat.votos == 0)).sum(), 894, 0),
        ("Series 0 votos", ((cat.tipo == "Serie") & (cat.votos == 0)).sum(), 3666, 0),
        ("% películas con presupuesto", (pel_raw.budget > 0).mean() * 100, 30.3, 1),
        ("n ROI", cat.roi.notna().sum(), 3362, 0),
        ("% películas con ROI", cat.roi.notna().sum() / 16000 * 100, 21.0, 1),
        ("m series", ev[ev.tipo == "Serie"].votos.median(), 9, 0),
        ("Idiomas", k0["idiomas"], 83, 0),
        ("Top10 películas", kp["Película"]["pct_top10_votos"], 71, 0),
        ("Top10 series", kp["Serie"]["pct_top10_votos"], 86, 0),
        ("Baja visibilidad series", kp["Serie"]["pct_baja_visibilidad"], 61.6, 1),
        ("Baja visibilidad películas", kp["Película"]["pct_baja_visibilidad"], 11.4, 1),
        ("Series sin votos %", (ser.votos == 0).mean() * 100, 22.9, 1),
        ("Series 1-9 votos %", ser.votos.between(1, 9).mean() * 100, 38.6, 1),
        ("Calif. pond. películas", kp["Película"]["calif_media"], 6.38, 2),
        ("Calif. pond. series", kp["Serie"]["calif_media"], 7.12, 2),
        ("Votos películas/series", kp["Película"]["votos_totales"] / kp["Serie"]["votos_totales"], 6.7, 1),
        ("ROI mediano", kp["Película"]["roi_mediano"], 80.7, 1),
        ("Tracción CF series", tg.loc[("Serie", "Ciencia ficción y fantasía"), "indice_traccion"], 2.48, 2),
        ("% asign CF series", tg.loc[("Serie", "Ciencia ficción y fantasía"), "pct_titulos"], 6.7, 1),
        ("% votos CF series", tg.loc[("Serie", "Ciencia ficción y fantasía"), "pct_votos"], 16.5, 1),
        ("Tracción talk show", tg.loc[("Serie", "Talk show"), "indice_traccion"], 0.06, 2),
        ("Tracción reality", tg.loc[("Serie", "Reality"), "indice_traccion"], 0.09, 2),
        ("Tracción noticias", tg.loc[("Serie", "Noticias"), "indice_traccion"], 0.10, 2),
        ("Tracción documental series", tg.loc[("Serie", "Documental"), "indice_traccion"], 0.21, 2),
        ("Tracción CF películas", tg.loc[("Película", "Ciencia ficción y fantasía"), "indice_traccion"], 1.85, 2),
        ("Tracción AyA películas", tg.loc[("Película", "Acción y aventura"), "indice_traccion"], 1.63, 2),
        ("Tracción drama películas", tg.loc[("Película", "Drama"), "indice_traccion"], 0.78, 2),
        ("Tracción terror películas", tg.loc[("Película", "Terror"), "indice_traccion"], 0.74, 2),
        ("% series con CF (títulos)", pct_tit_votos("Serie", ["Ciencia ficción y fantasía"])[0], 12.2, 1),
        ("% votos series CF (títulos)", pct_tit_votos("Serie", ["Ciencia ficción y fantasía"])[1], 41, 0),
        ("% series R+T+N", pct_tit_votos("Serie", ["Reality", "Talk show", "Noticias"])[0], 14, 0),
        ("% votos R+T+N", pct_tit_votos("Serie", ["Reality", "Talk show", "Noticias"])[1], 1.6, 1),
        ("Documentales 7+", tg.loc[("Película", "Documental"), "pct_calif_alta"], 54, 0),
        ("Películas 7+", kp["Película"]["pct_calif_alta"], 26, 0),
        ("Spearman películas", corr["Película"].loc["popularidad", "calificacion"], 0.23, 2),
        ("Spearman series", corr["Serie"].loc["popularidad", "calificacion"], 0.17, 2),
        ("Japonés películas 7+", ti.loc[("Película", "Japonés"), "pct_calif_alta"], 52, 0),
        ("Japonés series 7+", ti.loc[("Serie", "Japonés"), "pct_calif_alta"], 72, 0),
        ("Coreano películas 7+", ti.loc[("Película", "Coreano"), "pct_calif_alta"], 39, 0),
        ("Español películas 7+", ti.loc[("Película", "Español"), "pct_calif_alta"], 35, 0),
        ("Inglés películas 7+", ti.loc[("Película", "Inglés"), "pct_calif_alta"], 21, 0),
        ("Coreano series 7+", ti.loc[("Serie", "Coreano"), "pct_calif_alta"], 57, 0),
        ("Inglés series 7+", ti.loc[("Serie", "Inglés"), "pct_calif_alta"], 60, 0),
        ("% películas evaluadas en inglés", (pe.idioma == "Inglés").mean() * 100, 60, 0),
        ("% votos películas en inglés", pe[pe.idioma == "Inglés"].votos.sum() / pe.votos.sum() * 100, 88, 0),
        ("% animación japonés películas", jp_p.generos.str.contains("Animación").mean() * 100, 56, 0),
        ("% animación japonés series", jp_s.generos.str.contains("Animación").mean() * 100, 77, 0),
        ("7+ películas 2010", ta.loc[("Película", 2010), "pct_calif_alta"], 20, 0),
        ("7+ películas 2024", ta.loc[("Película", 2024), "pct_calif_alta"], 28, 0),
        ("7+ películas 2019 (máx.)", ta.loc[("Película", 2019), "pct_calif_alta"], 31, 0),
        ("7+ series 2010", ta.loc[("Serie", 2010), "pct_calif_alta"], 56, 0),
        ("7+ series 2024", ta.loc[("Serie", 2024), "pct_calif_alta"], 71, 0),
        ("Mediana votos películas 2019", ta.loc[("Película", 2019), "votos_mediana"], 221, 0),
        ("Mediana votos películas 2024", ta.loc[("Película", 2024), "votos_mediana"], 61, 0),
        ("ROI terror", tg.loc[("Película", "Terror"), "roi_mediano"] * 100, 150, 0),
        ("ROI animación", tg.loc[("Película", "Animación"), "roi_mediano"] * 100, 137, 0),
        ("ROI familiar", tg.loc[("Película", "Familiar"), "roi_mediano"] * 100, 119, 0),
        ("ROI drama", tg.loc[("Película", "Drama"), "roi_mediano"] * 100, 39, 0),
        ("ROI historia", tg.loc[("Película", "Historia y bélico"), "roi_mediano"] * 100, 17, 0),
        ("ROI prom. 2011-2019", np.mean([ta.loc[("Película", a), "roi_mediano"] for a in range(2011, 2020)]), 104, 0),
        ("ROI 2020", ta.loc[("Película", 2020), "roi_mediano"], -17, 0),
        ("ROI 2024", ta.loc[("Película", 2024), "roi_mediano"], 61, 0),
        ("n ROI 2025", roi_n[2025], 24, 0),
        ("EE.UU. títulos", pc["Estados Unidos"].sum(), 10955, 0),
        ("EE.UU. % películas", pc[("Estados Unidos", "Película")] / 16000 * 100, 48.5, 1),
        ("EE.UU. % series", pc[("Estados Unidos", "Serie")] / 15991 * 100, 20.0, 1),
        ("Japón % series", pc[("Japón", "Serie")] / 15991 * 100, 11.8, 1),
        ("China % series", pc[("China", "Serie")] / 15991 * 100, 11.9, 1),
        ("Joyas ocultas (títulos)", len(joyas), 1253, 0),
        ("Mediana votos joyas series", joyas[joyas.tipo == "Serie"].votos.median(), 4, 0),
    ]

    errores = 0
    for desc, calc, informe, dec in c:
        ok = round(float(calc), dec) == round(float(informe), dec)
        errores += not ok
        print(f"{'OK ' if ok else 'ERROR'}  {desc:<34} calculado={float(calc):>12.3f}  informe={informe}")
    print(f"\n{len(c) - errores}/{len(c)} cifras verificadas.")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()
