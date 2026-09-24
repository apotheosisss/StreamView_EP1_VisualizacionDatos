"""
Limpieza e integración de las fuentes de datos.

Fuentes:
    data/raw/netflix_movies_detailed_up_to_2025.csv   (16.000 películas)
    data/raw/netflix_tv_shows_detailed_up_to_2025.csv (16.000 series)

Salidas (data/processed/):
    catalogo_integrado.csv  -> 1 fila por título (películas + series)
    catalogo_generos.csv    -> 1 fila por título-género (formato largo)
    catalogo_paises.csv     -> 1 fila por título-país  (formato largo)

Uso:
    python -m src.preparacion
"""
import unicodedata

import numpy as np
import pandas as pd

from src import config as cfg

# Caracteres válidos para textos visibles: los del teclado latinoamericano.
_PERMITIDOS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    " .,;:-_()[]{}!?¡¿'\"&/+*%$#@=<>|°ªºáéíóúÁÉÍÓÚñÑüÜ"
)

# Signos tipográficos frecuentes -> equivalente escribible con el teclado
_REEMPLAZOS = {
    "\u2014": " - ", "\u2013": " - ", "\u2012": "-", "\u2010": "-",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u00ab": '"', "\u00bb": '"',
    "\u2018": "'", "\u2019": "'", "\u00b4": "'", "\u2026": "...",
    "\u00a0": " ", "\u2022": "-", "\u00b7": "-",
}


def texto_teclado(valor):
    """Normaliza un texto a caracteres del teclado latinoamericano.

    Quita tildes que no existen en español (por ejemplo, la e con acento grave) y descarta
    escrituras no latinas. Devuelve cadena vacía si no queda texto útil.
    """
    if not isinstance(valor, str):
        return ""
    for original, reemplazo in _REEMPLAZOS.items():
        valor = valor.replace(original, reemplazo)
    salida = []
    for ch in valor:
        if ch in _PERMITIDOS:
            salida.append(ch)
            continue
        base = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in base if c in _PERMITIDOS)
        salida.append(base)
    txt = " ".join("".join(salida).split())
    # si se perdió más de la mitad del texto original, no es representable
    if len(txt.replace(" ", "")) < 0.5 * len(valor.replace(" ", "")):
        return ""
    return txt


def cargar_fuentes():
    """Lee ambos CSV y los devuelve como DataFrames sin modificar."""
    peliculas = pd.read_csv(cfg.ARCHIVO_PELICULAS)
    series = pd.read_csv(cfg.ARCHIVO_SERIES)
    return peliculas, series


def _tramo_visibilidad(votos):
    for lo, hi, etiqueta in cfg.TRAMOS_VISIBILIDAD:
        if lo < votos <= hi:
            return etiqueta
    return cfg.ORDEN_VISIBILIDAD[-1]


def integrar(peliculas, series):
    """Integra películas y series en un catálogo único y limpio."""
    pel = peliculas.copy()
    ser = series.copy()

    # 1) Columnas sin valor analítico (ver informe, sección 4.3):
    #    - rating == vote_average en el 100% de filas (redundante)
    #    - duration: vacía en películas y constante ("1 Seasons") en series
    #    - date_added: su año coincide 100% con release_year
    pel = pel.drop(columns=["rating", "duration", "date_added"])
    ser = ser.drop(columns=["rating", "duration", "date_added"])

    # 2) Columnas financieras solo existen en películas
    ser["budget"] = np.nan
    ser["revenue"] = np.nan

    cat = pd.concat([pel, ser], ignore_index=True)

    # 3) Duplicados exactos de id dentro de un mismo tipo
    antes = len(cat)
    cat = cat.drop_duplicates(subset=["type", "show_id"]).reset_index(drop=True)
    duplicados = antes - len(cat)

    # 4) Renombrar a español
    cat = cat.rename(columns={
        "show_id": "id", "type": "tipo", "title": "titulo_original",
        "director": "director", "cast": "reparto", "country": "paises",
        "release_year": "anio", "genres": "generos_origen",
        "language": "idioma_cod", "description": "descripcion",
        "popularity": "popularidad", "vote_count": "votos",
        "vote_average": "calificacion", "budget": "presupuesto",
        "revenue": "recaudacion",
    })
    cat["tipo"] = cat["tipo"].map({"Movie": "Película", "TV Show": "Serie"})

    # 5) Calificación 0 con 0 votos = "sin evaluar", no una nota real
    cat.loc[cat["votos"] == 0, "calificacion"] = np.nan

    # 6) Presupuesto / recaudación en 0 = dato no informado
    for col in ["presupuesto", "recaudacion"]:
        cat.loc[cat[col] <= 0, col] = np.nan

    # 7) Textos visibles normalizados al teclado latinoamericano
    cat["titulo"] = cat["titulo_original"].map(texto_teclado)
    cat["titulo_latino"] = cat["titulo"] != ""
    cat.loc[~cat["titulo_latino"], "titulo"] = (
        "Título en escritura no latina (id " + cat["id"].astype(str) + ")"
    )
    for col in ["director", "reparto", "descripcion"]:
        cat[col] = cat[col].map(texto_teclado)

    # 8) Variables derivadas
    cat["idioma"] = cat["idioma_cod"].map(cfg.IDIOMAS).fillna(
        "Otro (" + cat["idioma_cod"] + ")")
    cat["pais_principal_en"] = cat["paises"].str.split(", ").str[0]
    cat["pais_principal"] = cat["pais_principal_en"].map(cfg.PAISES).fillna(
        cat["pais_principal_en"]).fillna("Sin información")
    cat["generos"] = cat["generos_origen"].fillna("").map(
        lambda s: ", ".join(dict.fromkeys(
            cfg.MAPA_GENEROS.get(g.strip(), g.strip())
            for g in s.split(",") if g.strip())))
    cat.loc[cat["generos"] == "", "generos"] = "Sin clasificar"
    cat["genero_principal"] = cat["generos"].str.split(", ").str[0]
    cat["visibilidad"] = cat["votos"].map(_tramo_visibilidad)
    cat["roi"] = (cat["recaudacion"] - cat["presupuesto"]) / cat["presupuesto"]
    # ROI solo con presupuesto realista (>= USD 100.000) para evitar errores
    cat.loc[cat["presupuesto"] < 100_000, "roi"] = np.nan
    cat.loc[cat["recaudacion"] < 100_000, "roi"] = np.nan

    # 9) Calificación ponderada (fórmula bayesiana tipo IMDb) por tipo
    cat["calif_ponderada"] = np.nan
    for tipo, g in cat[cat["votos"] > 0].groupby("tipo"):
        m = g["votos"].median()          # votos mínimos de referencia
        c = g["calificacion"].mean()     # media del tipo
        v, r = g["votos"], g["calificacion"]
        cat.loc[g.index, "calif_ponderada"] = (v / (v + m)) * r + (m / (v + m)) * c
    cat["calif_ponderada"] = cat["calif_ponderada"].round(3)

    columnas = [
        "id", "tipo", "titulo", "titulo_latino", "anio", "generos",
        "genero_principal", "idioma_cod", "idioma", "paises",
        "pais_principal", "pais_principal_en", "director", "reparto",
        "popularidad", "votos", "visibilidad", "calificacion",
        "calif_ponderada", "presupuesto", "recaudacion", "roi", "descripcion",
    ]
    return cat[columnas], duplicados


def expandir(cat, columna, nombre):
    """Convierte una columna multivalor (separada por coma) a formato largo."""
    largo = cat[["id", "tipo", columna]].copy()
    largo[nombre] = largo[columna].fillna("").str.split(", ")
    largo = largo.explode(nombre).drop(columns=columna)
    largo = largo[largo[nombre].fillna("") != ""]
    return largo.drop_duplicates().reset_index(drop=True)


def ejecutar():
    peliculas, series = cargar_fuentes()
    cat, dup = integrar(peliculas, series)
    generos = expandir(cat, "generos", "genero")
    paises = expandir(cat, "paises", "pais_en")
    paises["pais"] = paises["pais_en"].map(cfg.PAISES).fillna(paises["pais_en"])

    cfg.DATA_PROC.mkdir(parents=True, exist_ok=True)
    cat.to_csv(cfg.CATALOGO, index=False)
    generos.to_csv(cfg.CATALOGO_GENEROS, index=False)
    paises.to_csv(cfg.CATALOGO_PAISES, index=False)
    print(f"Catálogo integrado: {len(cat):,} títulos (duplicados eliminados: {dup})")
    print(f"Relaciones título-género: {len(generos):,}")
    print(f"Relaciones título-país:   {len(paises):,}")
    return cat, generos, paises


if __name__ == "__main__":
    ejecutar()
