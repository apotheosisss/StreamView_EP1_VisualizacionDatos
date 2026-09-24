"""
Configuración central del proyecto: rutas, paleta de colores y diccionarios
de traducción. Notebooks, dashboard e informe importan desde aquí para
mantener coherencia visual y de nomenclatura.
"""
from pathlib import Path

# ---------------------------------------------------------------- rutas
RAIZ = Path(__file__).resolve().parents[1]
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROC = RAIZ / "data" / "processed"
IMAGES = RAIZ / "images"

ARCHIVO_PELICULAS = DATA_RAW / "netflix_movies_detailed_up_to_2025.csv"
ARCHIVO_SERIES = DATA_RAW / "netflix_tv_shows_detailed_up_to_2025.csv"

CATALOGO = DATA_PROC / "catalogo_integrado.csv"
CATALOGO_GENEROS = DATA_PROC / "catalogo_generos.csv"
CATALOGO_PAISES = DATA_PROC / "catalogo_paises.csv"

# ---------------------------------------------------------------- paleta
# Regla de diseño: el gris es el color de contexto y solo el dato que se
# quiere destacar recibe color de acento (atención preatentiva).
COLOR_PELICULA = "#2E4A62"   # azul pizarra
COLOR_SERIE = "#E09F3E"      # ámbar
COLOR_ACENTO = "#C8102E"     # rojo de énfasis (un solo mensaje por gráfico)
COLOR_POSITIVO = "#0F7C8C"   # azul petróleo = oportunidad (distinguible del rojo con daltonismo)
COLOR_GRIS = "#B8BCC2"
COLOR_GRIS_OSCURO = "#5B6270"
COLOR_TEXTO = "#1F2430"

COLORES_TIPO = {"Película": COLOR_PELICULA, "Serie": COLOR_SERIE}

# ---------------------------------------------------------------- géneros
# Películas y series usan taxonomías distintas; se unifican en una sola
# clasificación en español para poder compararlas.
MAPA_GENEROS = {
    # películas
    "Drama": "Drama",
    "Comedy": "Comedia",
    "Thriller": "Suspenso",
    "Action": "Acción y aventura",
    "Adventure": "Acción y aventura",
    "Romance": "Romance",
    "Horror": "Terror",
    "Crime": "Crimen",
    "Animation": "Animación",
    "Family": "Familiar",
    "Science Fiction": "Ciencia ficción y fantasía",
    "Fantasy": "Ciencia ficción y fantasía",
    "Mystery": "Misterio",
    "Documentary": "Documental",
    "History": "Historia y bélico",
    "War": "Historia y bélico",
    "TV Movie": "Película para TV",
    "Music": "Música",
    "Western": "Western",
    # series
    "Action & Adventure": "Acción y aventura",
    "Sci-Fi & Fantasy": "Ciencia ficción y fantasía",
    "Reality": "Reality",
    "Kids": "Infantil",
    "Talk": "Talk show",
    "Soap": "Telenovela",
    "War & Politics": "Historia y bélico",
    "News": "Noticias",
    "Unknown": "Sin clasificar",
}

# ---------------------------------------------------------------- idiomas
IDIOMAS = {
    "en": "Inglés", "ja": "Japonés", "ko": "Coreano", "zh": "Chino",
    "cn": "Cantonés", "es": "Español", "fr": "Francés",
    "de": "Alemán", "hi": "Hindi", "it": "Italiano", "pt": "Portugués",
    "tl": "Tagalo", "ar": "Árabe", "tr": "Turco", "ru": "Ruso",
    "th": "Tailandés", "id": "Indonesio", "pl": "Polaco", "nl": "Neerlandés",
    "sv": "Sueco", "da": "Danés", "no": "Noruego", "fi": "Finés",
    "ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "he": "Hebreo",
    "fa": "Persa", "el": "Griego", "uk": "Ucraniano", "ms": "Malayo",
    "vi": "Vietnamita", "cs": "Checo", "hu": "Húngaro", "ro": "Rumano",
    "ur": "Urdu", "ca": "Catalán", "af": "Afrikáans", "sr": "Serbio",
    "bn": "Bengalí", "sk": "Eslovaco", "hr": "Croata", "is": "Islandés",
    "lt": "Lituano", "bg": "Búlgaro", "et": "Estonio", "xx": "Sin idioma",
    "kn": "Canarés", "lv": "Letón", "ka": "Georgiano", "mr": "Maratí",
    "km": "Jemer", "mk": "Macedonio", "sl": "Esloveno", "gl": "Gallego",
    "si": "Cingalés", "mn": "Mongol", "pa": "Panyabí", "zu": "Zulú",
    "am": "Amhárico", "kk": "Kazajo", "ga": "Irlandés", "ne": "Nepalí",
    "cy": "Galés", "ku": "Kurdo", "eu": "Euskera", "la": "Latín",
    "nb": "Noruego", "hy": "Armenio", "bs": "Bosnio", "lb": "Luxemburgués",
}

# ---------------------------------------------------------------- países
PAISES = {
    "United States of America": "Estados Unidos", "United Kingdom": "Reino Unido",
    "France": "Francia", "Canada": "Canadá", "Japan": "Japón",
    "South Korea": "Corea del Sur", "Germany": "Alemania", "Spain": "España",
    "India": "India", "Belgium": "Bélgica", "China": "China", "Italy": "Italia",
    "Philippines": "Filipinas", "Mexico": "México", "Turkey": "Turquía",
    "Australia": "Australia", "Brazil": "Brasil", "Argentina": "Argentina",
    "Chile": "Chile", "Colombia": "Colombia", "Taiwan": "Taiwán",
    "Thailand": "Tailandia", "Russia": "Rusia", "Sweden": "Suecia",
    "Denmark": "Dinamarca", "Norway": "Noruega", "Netherlands": "Países Bajos",
    "Ireland": "Irlanda", "Hong Kong": "Hong Kong", "Egypt": "Egipto",
    "Poland": "Polonia", "Indonesia": "Indonesia", "Switzerland": "Suiza",
    "Austria": "Austria", "New Zealand": "Nueva Zelanda",
    "South Africa": "Sudáfrica", "Nigeria": "Nigeria", "Israel": "Israel",
    "Saudi Arabia": "Arabia Saudita", "Luxembourg": "Luxemburgo",
}

# Tramos de visibilidad (cantidad de votos recibidos por título)
TRAMOS_VISIBILIDAD = [
    (-1, 0, "Sin votos"),
    (0, 9, "Baja (1-9)"),
    (9, 99, "Media (10-99)"),
    (99, 999, "Alta (100-999)"),
    (999, float("inf"), "Muy alta (1000+)"),
]
ORDEN_VISIBILIDAD = [t[2] for t in TRAMOS_VISIBILIDAD]
