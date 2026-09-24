"""
Cálculo de indicadores (KPIs) y tablas agregadas reutilizadas por los
notebooks, el dashboard y el informe.

Definiciones clave:
    votos              -> proxy de INTERACCIÓN (usuarios que evaluaron)
    popularidad        -> proxy de ATENCIÓN reciente (índice de actividad)
    calif_ponderada    -> proxy de SATISFACCIÓN, corregida por n de votos
    índice de tracción -> % de votos del género / % de asignaciones del género
                          (las participaciones se calculan sobre la tabla larga
                          título-género, por lo que suman 100% por tipo; un título
                          con 3 géneros aporta a los 3. >1 = el género genera
                          más interacción que su peso en la oferta)
"""
import numpy as np
import pandas as pd

from src import config as cfg


def cargar_procesados():
    cat = pd.read_csv(cfg.CATALOGO)
    gen = pd.read_csv(cfg.CATALOGO_GENEROS)
    pai = pd.read_csv(cfg.CATALOGO_PAISES)
    return cat, gen, pai


def kpis(cat):
    """Indicadores clave del catálogo filtrado."""
    evaluados = cat[cat["votos"] > 0]
    total = len(cat)
    votos_ord = cat["votos"].sort_values(ascending=False)
    top10 = votos_ord.head(max(1, int(round(total * 0.10)))).sum()
    return {
        "titulos": total,
        "peliculas": int((cat["tipo"] == "Película").sum()),
        "series": int((cat["tipo"] == "Serie").sum()),
        "votos_totales": int(cat["votos"].sum()),
        "votos_mediana": float(cat["votos"].median()) if total else 0.0,
        "calif_media": float(evaluados["calif_ponderada"].mean()) if len(evaluados) else np.nan,
        "pct_calif_alta": float((evaluados["calificacion"] >= 7).mean() * 100) if len(evaluados) else np.nan,
        "pct_baja_visibilidad": float((cat["votos"] < 10).mean() * 100) if total else np.nan,
        "pct_top10_votos": float(top10 / votos_ord.sum() * 100) if votos_ord.sum() else np.nan,
        "roi_mediano": float(cat["roi"].median() * 100) if cat["roi"].notna().any() else np.nan,
        "idiomas": int(cat["idioma_cod"].nunique()),
    }


def tabla_generos(cat, gen, min_titulos=30):
    """Oferta, interacción y calidad por tipo y género."""
    base = gen.merge(
        cat[["id", "tipo", "votos", "calif_ponderada", "calificacion", "roi"]],
        on=["id", "tipo"])
    t = base.groupby(["tipo", "genero"]).agg(
        titulos=("id", "size"),
        votos=("votos", "sum"),
        votos_mediana=("votos", "median"),
        calif_ponderada=("calif_ponderada", "mean"),
        pct_calif_alta=("calificacion", lambda s: (s >= 7).mean() * 100),
        roi_mediano=("roi", "median"),
        n_roi=("roi", "count"),
    ).reset_index()
    t["pct_titulos"] = t["titulos"] / t.groupby("tipo")["titulos"].transform("sum") * 100
    t["pct_votos"] = t["votos"] / t.groupby("tipo")["votos"].transform("sum") * 100
    t["indice_traccion"] = t["pct_votos"] / t["pct_titulos"]
    return t[t["titulos"] >= min_titulos].reset_index(drop=True)


def curva_concentracion(cat):
    """Curva de Lorenz: % acumulado de votos vs % acumulado de títulos."""
    filas = []
    for tipo, g in cat.groupby("tipo"):
        v = np.sort(g["votos"].to_numpy())[::-1]
        if v.sum() == 0:
            continue
        acum = np.cumsum(v) / v.sum() * 100
        x = np.arange(1, len(v) + 1) / len(v) * 100
        idx = np.linspace(0, len(v) - 1, 201).astype(int)
        filas.append(pd.DataFrame({"tipo": tipo, "pct_titulos": x[idx], "pct_votos": acum[idx]}))
    return pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()


def tabla_idiomas(cat, min_titulos=200):
    ev = cat[cat["votos"] > 0]
    t = ev.groupby(["tipo", "idioma"]).agg(
        titulos=("id", "size"), votos=("votos", "sum"),
        calif_ponderada=("calif_ponderada", "mean"),
        pct_calif_alta=("calificacion", lambda s: (s >= 7).mean() * 100),
    ).reset_index()
    return t[t["titulos"] >= min_titulos].reset_index(drop=True)


def tabla_anual(cat):
    ev = cat[cat["votos"] > 0]
    t = ev.groupby(["tipo", "anio"]).agg(
        calif_ponderada=("calif_ponderada", "mean"),
        pct_calif_alta=("calificacion", lambda s: (s >= 7).mean() * 100),
        votos_mediana=("votos", "median"),
        popularidad_mediana=("popularidad", "median"),
    ).reset_index()
    roi = cat.groupby(["tipo", "anio"])["roi"].median().mul(100).rename("roi_mediano")
    return t.merge(roi.reset_index(), on=["tipo", "anio"], how="left")


def tabla_visibilidad(cat):
    t = cat.groupby(["tipo", "visibilidad"]).size().rename("titulos").reset_index()
    t["pct"] = t["titulos"] / t.groupby("tipo")["titulos"].transform("sum") * 100
    t["visibilidad"] = pd.Categorical(t["visibilidad"], cfg.ORDEN_VISIBILIDAD, ordered=True)
    return t.sort_values(["tipo", "visibilidad"])


def correlaciones(cat, min_votos=10):
    """Spearman entre métricas, solo títulos con min_votos o más (nota estable)."""
    ev = cat[cat["votos"] >= min_votos]
    out = {}
    for tipo, g in ev.groupby("tipo"):
        out[tipo] = g[["popularidad", "votos", "calificacion", "calif_ponderada"]].corr(method="spearman")
    return out
