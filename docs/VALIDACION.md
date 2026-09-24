# Validación del proyecto StreamView (EP1 ADY1104)

Revisión completa de `ev1.rar`: código (`src/`), notebooks, dashboard, informe, presentación y guía.
Cada cifra se recalculó desde `data/raw`. La verificación automática de las cifras del paper queda en
`python -m src.verificacion` (76 de 76 cifras OK).

## 1. Reproducibilidad

| Prueba | Resultado |
|---|---|
| `python -m src.preparacion` regenera `data/processed` | Las 3 tablas son idénticas byte a byte a las entregadas |
| Notebooks 01 y 02 ejecutados de nuevo (`nbconvert --execute`) | Sin errores |
| `python -m src.graficos` | Las 10 figuras se generan sin errores |
| Dashboard: 6 páginas y filtros (prueba automática con `streamlit.testing`) | Sin excepciones; el aviso de "sin datos" funciona |
| CSV entregados aparte vs. `data/raw` | Idénticos (mismo MD5) |

## 2. Afirmaciones verificadas como correctas

KPIs (31.991 títulos; 13.210.726 votos; medianas 138/4; calificación ponderada 6,38/7,12; 7+ 25,8 %/61,8 %;
baja visibilidad 11,4 %/61,6 %; top 10 % 71,0 %/85,9 %); 9 duplicados exactos; 704 títulos no latinos;
894/3.666 títulos con 0 votos; ROI n = 3.362 (21 %); 83 idiomas; índices de tracción (x2,48; x1,98; x0,06; x0,09; etc.);
54 % vs 26 % en documentales; idiomas (52 %, 39 %, 35 %, 21 %; 72 % en series); Spearman 0,23/0,17;
ROI por género (150 %, 137 %, 119 %, 39 %, 17 %) y por año (-17 % en 2020, 61 % en 2024); EE. UU. 10.955 títulos;
funcionalidades del dashboard (6 KPIs, 5 filtros, 6 páginas, selección por lazo, CSV, joyas ocultas).

## 3. Afirmaciones falsas o imprecisas corregidas

| # | Dónde | Afirmación original | Qué muestran los datos | Corrección |
|---|---|---|---|---|
| 1 | Informe 4.3, notebook 01, dashboard pág. 6, presentación | "Se unifican en 18 géneros" | Son **21 géneros** más "Sin clasificar" (16 en cada tipo) | Cifra corregida y celda de verificación agregada al notebook 01 |
| 2 | Informe 5.2 y 10.1, presentación | "Ciencia ficción representa el 6,7 % de los títulos (series)"; "reality, talk show y noticias ocupan el 8 % de las series y < 1 % de los votos" | El índice se calcula sobre **asignaciones título-género**, no sobre títulos. El 12,2 % de las series tiene ciencia ficción y reúne el 41 % de los votos. El 14 % de las series tiene reality, talk show o noticias y recibe el 1,6 % de los votos | Definición precisada en paper, dashboard, README y `metricas.py` (el ranking no cambia) |
| 3 | Informe 5.3 | "Terror y suspenso concentran interacción con baja calificación" | Terror tiene tracción x0,74, bajo la mediana (x0,90): baja calidad **y** baja interacción | Corregido |
| 4 | Informe 5.3, figura 2 | Joyas ocultas en películas = documental, música e historia | Con la regla usada, **drama y romance** también caen en el cuadrante (cerca del umbral). En series, los motores incluyen además **drama e historia** | Explicitado en paper y subtítulo de la figura |
| 5 | Informe 5.6 y 10.1, fig. 6, dashboard, presentación | "La calidad mejora de forma sostenida / año a año" | La tendencia sube (ρ ≈ 0,87), pero con retrocesos: las películas alcanzan su máximo en 2019 (31 %) y bajan a 28 %. La mediana de votos cae de 221 a 61, lo que sugiere un posible **sesgo de antigüedad** | Redacción corregida; el texto del dashboard ahora se calcula sobre la selección |
| 6 | Informe 5.5, dashboard | "El japonés es el mejor evaluado en ambos tipos" | En películas es robusto. En series solo se cumple con el umbral de 200 títulos y ≥1 voto; con ≥10 votos lo superan el español, el turco y el chino. Además, 56 %/77 % del contenido japonés es animación | Se agregó tabla de robustez y el matiz "anime" |
| 7 | Recomendación 3 del informe y notas de la presentación | "Ampliar la producción coreana" | En series, el coreano (57 %) queda **bajo** el inglés (60 %) | Se limita a películas |
| 8 | Informe 5.8 | "En 2024-2025 el ROI se estabiliza en 61 %" | 2025 tiene solo **24 películas** con datos y recaudación incompleta; el ROI mide taquilla, no el valor en la plataforma | Advertencia agregada |
| 9 | Pie de todas las figuras | "32.000 títulos" | Catálogo integrado = **31.991** | Corregido |
| 10 | Todo el informe | "Fuentes corporativas"; votos = "usuarios que calificaron" | Los archivos son catálogos públicos con metadatos **TMDB** (los id coinciden: Inception = 27205). Los votos vienen de la comunidad TMDB | Declarado como proxy externo; las metas se redefinen con datos propios de reproducción |
| 11 | Recomendaciones | Meta "bajar % de series con < 10 votos de 62 % a < 45 %" | StreamView no puede mover votos de TMDB desde su interfaz | Se reemplaza por "% del catálogo con reproducciones en 90 días" (el 62 % queda como línea base aproximada) |
| 12 | Guía de defensa | Se cita la pauta con IE1-3, IE8, IE11 y IE12 | La pauta del encargo evalúa **IE4, IE5, IE6, IE7, IE9 e IE10** | El paper incluye un apéndice de trazabilidad con la pauta |

## 4. Observaciones menores (no corregidas)

- La calificación ponderada usa m = 9 votos en series, por lo que corrige poco: las "joyas ocultas" de series tienen una mediana de 4 votos. Se declara como limitación.
- Algunos países aparecen en inglés en el dashboard (p. ej., "Czech Republic", "Syrian Arab Republic").
- Streamlit ≥ 1.50 advierte que `use_container_width` está obsoleto (funciona en 1.64).
- El notebook 01 informa 3.674 series con 0 votos en los datos crudos (con duplicados) y el informe 3.666 (sin duplicados). Ambas cifras son correctas en su contexto.
