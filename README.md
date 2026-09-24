# StreamView Analytics - Solución de visualización de datos

**Evaluación Parcial N°1 - ADY1104 Visualización de Datos - Duoc UC 2026**
Equipo consultor: **Claudio Aro, Guillermo Cerda, Manuel Díaz**

Solución integral de visualización para apoyar a StreamView Analytics en decisiones de
retención, engagement, preferencias de contenido y experiencia de usuario, a partir de su
catálogo de películas y series 2010-2025 (32.000 registros; 31.991 títulos tras eliminar duplicados).

## Estructura del proyecto

```
StreamView_EP1_VisualizacionDatos/
|-- README.md                  <- este archivo
|-- requirements.txt           <- dependencias de Python
|-- .streamlit/config.toml     <- tema visual del dashboard
|-- data/
|   |-- raw/                   <- fuentes originales (no se modifican)
|   `-- processed/             <- catálogo integrado y tablas largas (generadas)
|-- src/
|   |-- config.py              <- rutas, paleta de colores, diccionarios de traducción
|   |-- preparacion.py         <- limpieza e integración de fuentes
|   |-- metricas.py            <- KPIs y tablas agregadas
|   |-- graficos.py            <- figuras estáticas (presentación y notebooks)
|   |-- graficos_paper.py      <- figuras vectoriales del informe en formato paper
|   `-- verificacion.py        <- verifica automáticamente las cifras citadas en el paper
|-- notebooks/
|   |-- 01_integracion_limpieza.ipynb
|   `-- 02_analisis_exploratorio.ipynb
|-- dashboard/
|   `-- app.py                 <- dashboard interactivo (Streamlit + Plotly)
|-- images/                    <- figuras (fig01-fig09) y capturas del dashboard
`-- docs/
    |-- Informe_Ejecutivo_StreamView.pdf   <- informe ejecutivo para gerencia (10 secciones de la pauta)
    |-- Informe_Tecnico_StreamView.pdf     <- informe técnico en formato paper (IEEE): metodología completa
    |-- VALIDACION.md                      <- verificación de cifras y correcciones
    |-- Presentación_Ejecutiva_StreamView.pptx / .pdf   <- resumen ejecutivo
    |-- Guía_Defensa_StreamView.pdf / .docx
    `-- fuentes_generacion/    <- generador del informe ejecutivo (informe_ejecutivo/), LaTeX del informe técnico (paper/) y scripts de la presentación y la guía
```

## Cómo ejecutar (Python 3.10 o superior)

```bash
# 1. Crear entorno e instalar dependencias
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

# 2. (Opcional) regenerar datos procesados y figuras
python -m src.preparacion
python -m src.graficos
python -m src.graficos_paper
python docs/fuentes_generacion/informe_ejecutivo/generar_informe.py   # informe ejecutivo (HTML + PDF)
python -m src.verificacion      # debe terminar con "76/76 cifras verificadas"

# 3. Abrir el dashboard (desde la raíz del proyecto)
streamlit run dashboard/app.py
```

El dashboard se abre en http://localhost:8501. Si los datos procesados no existen,
el dashboard los genera automáticamente desde `data/raw/`.

## Dashboard

| Página | Contenido |
|---|---|
| 1. Resumen ejecutivo | 6 KPIs, índice de tracción por género, concentración y visibilidad |
| 2. Géneros | Matriz calidad vs interacción con selección por clic o lazo y detalle de títulos |
| 3. Idiomas y origen | Calidad por idioma, mapa de países productores, top 15 países |
| 4. Tendencias | Evolución anual con selector de indicador; popularidad vs calificación |
| 5. Explorador | Búsqueda por título/director/reparto, orden, filtro "joyas ocultas" |
| 6. Metodología | Definición de indicadores y limitaciones |

Filtros globales (barra lateral): tipo, rango de años, géneros, idioma, votos mínimos,
botón para restablecer y descarga de la selección en CSV.

## Indicadores

- **Votos**: proxy de interacción (engagement).
- **Calificación ponderada**: (v/(v+m))*R + (m/(v+m))*C; m = mediana de votos del tipo, C = media del tipo.
- **Índice de tracción**: % de votos del género / % de asignaciones título-género del género
  (participaciones calculadas sobre la tabla larga `catalogo_generos.csv`).
- **% baja visibilidad**: títulos con menos de 10 votos.
- **ROI**: (recaudación - presupuesto) / presupuesto (solo películas con datos).

## Limitaciones de los datos

Las fuentes son catálogos públicos con metadatos de TMDB (votos, calificación y popularidad
provienen de la comunidad TMDB, no de usuarios de StreamView) y no describen el comportamiento
individual (reproducciones, suscripciones, dispositivos). La muestra está balanceada (1.000 títulos por año y tipo),
por lo que no se analiza el crecimiento del volumen. Detalle en el informe técnico (`docs/Informe_Tecnico_StreamView.pdf`, sección X) y en `docs/VALIDACION.md`.

## Nota sobre nombres

Los textos visibles (informe, presentación, dashboard, figuras, notebooks) usan tildes y ñ.
Los nombres de carpetas, archivos de código y columnas de datos (por ejemplo `anio`,
`titulo`, `calificacion`) se mantienen sin tildes por compatibilidad entre sistemas
operativos y librerías; en el dashboard y los gráficos se muestran con su nombre correcto
("Año", "Título", "Calificación").
