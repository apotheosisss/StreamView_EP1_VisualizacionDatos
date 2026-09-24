const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");
const IMG = path.join(__dirname, "..", "..", "images") + path.sep;
const SALIDA = process.env.SALIDA || path.join(__dirname, "..", "Presentación_Ejecutiva_StreamView.pptx");

// ---------------------------------------------------------------- sistema de color
// Datos:      AZUL = películas, AMBAR = series
// Semántica:  PETROLEO = oportunidad / positivo, ROJO = alerta / negativo, GRISC = contexto
// Estructura: OSC (textos, números y marcadores)
const OSC = "1F2430", AZUL = "2E4A62", AMBAR = "E09F3E", ROJO = "C8102E", PETROLEO = "0F7C8C",
  GRIS = "5B6270", GRISC = "B8BCC2", FONDO = "F3F4F6", PET_CLARO = "E3F1F3", ROJO_CLARO = "FBE3E6", CREMA = "FFF4E5";
const F = "Arial";
const MIN = 11; // tamaño mínimo de texto legible al proyectar
const FUENTE = "Fuente: catálogo StreamView 2010-2025 (31.991 títulos). Elaboración propia.";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.author = "Claudio Aro, Guillermo Cerda, Manuel Díaz";
pres.title = "StreamView Analytics - Presentación ejecutiva EP2";

const sizeOf = (p) => { const b = fs.readFileSync(p); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; };
function img(s, p, x, y, w, hMax) {
  const { w: iw, h: ih } = sizeOf(p); let h = w * ih / iw; let ww = w;
  if (hMax && h > hMax) { h = hMax; ww = h * iw / ih; }
  s.addImage({ path: p, x, y, w: ww, h }); return { x, y, w: ww, h };
}
const T = (s, text, o) => s.addText(text, { fontFace: F, isTextBox: true, margin: 0, color: OSC, valign: "top", ...o });
function titulo(s, t, sub, orador) {
  T(s, t, { x: 0.5, y: 0.35, w: 9, h: 0.6, fontSize: 24, bold: true, fit: "shrink" });
  if (sub) T(s, sub, { x: 0.5, y: 0.98, w: 9, h: 0.32, fontSize: 13, color: GRIS });
  if (orador) T(s, orador, { x: 7.0, y: 0.1, w: 2.5, h: 0.22, fontSize: MIN, color: GRIS, align: "right" });
}
// pie: fuente de datos + justificación del gráfico
const pie = (s, porque) => T(s, [{ text: FUENTE }, ...(porque ? [{ text: "  Gráfico: ", options: { bold: true } }, { text: porque }] : [])],
  { x: 0.5, y: 5.08, w: 9, h: 0.42, fontSize: MIN, color: GRIS, valign: "bottom" });
const tarjeta = (s, x, y, w, h, fill = FONDO) => s.addShape(pres.shapes.ROUNDED_RECTANGLE,
  { x, y, w, h, fill: { color: fill }, line: { color: fill }, rectRadius: 0.08 });
function circulo(s, x, y, d, color, txt, fs = 14) {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color }, line: { color: "FFFFFF", width: 1.5 } });
  T(s, txt, { x, y, w: d, h: d, fontSize: fs, bold: true, color: "FFFFFF", align: "center", valign: "middle" });
}
const EJES = { catAxisLabelColor: OSC, valAxisLabelColor: GRIS, catAxisLabelFontSize: MIN, valAxisLabelFontSize: MIN,
  valGridLine: { color: "E5E7EB", size: 0.5 }, catGridLine: { style: "none" } };

// ================================================================== 1 portada
let s = pres.addSlide(); s.background = { color: OSC };
T(s, "ADY1104 VISUALIZACIÓN DE DATOS  |  EVALUACIÓN PARCIAL N°2  |  PRESENTACIÓN", { x: 0.6, y: 0.55, w: 8.8, h: 0.3, fontSize: 12, color: AMBAR, bold: true, charSpacing: 1 });
T(s, "Del catálogo al descubrimiento", { x: 0.6, y: 1.35, w: 8.8, h: 0.9, fontSize: 40, bold: true, color: "FFFFFF" });
T(s, "Qué contenido genera interacción en StreamView y cuál el usuario no alcanza a ver", { x: 0.6, y: 2.3, w: 8, h: 0.7, fontSize: 18, color: "D9DCE0" });
["Claudio Aro", "Guillermo Cerda", "Manuel Díaz"].forEach((n, i) => {
  const ini = n.split(" ").map((p) => p[0]).join("");
  circulo(s, 0.6 + i * 2.6, 3.85, 0.55, "3A4254", ini);
  T(s, n, { x: 1.28 + i * 2.6, y: 3.97, w: 1.9, h: 0.35, fontSize: 14, color: "FFFFFF" });
});
T(s, "Docente: Claudio Andrés Gonzalez Peñaloza  |  Duoc UC, sede Puerto Montt  |  Septiembre 2026", { x: 0.6, y: 4.95, w: 8.8, h: 0.3, fontSize: MIN, color: GRISC });
s.addNotes("[Claudio - 15 s] Buenos días. Somos el equipo consultor contratado por StreamView Analytics. En 10 minutos mostraremos qué contenido genera interacción, cuál valoran los usuarios, qué parte del catálogo no se descubre y qué decisiones proponemos. Yo presento el problema, la estrategia, la metodología y los datos; Guillermo, los hallazgos y por qué elegimos cada gráfico; Manuel, la solución y las recomendaciones.");

// ================================================================== 2 problema y audiencia
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Un gran catálogo no retiene si el usuario no lo descubre", "Problema de negocio, audiencia y propósito de la solución", "Claudio Aro");
tarjeta(s, 0.5, 1.5, 4.1, 3.5, CREMA);
T(s, "El problema", { x: 0.75, y: 1.68, w: 3.6, h: 0.35, fontSize: 16, bold: true, color: ROJO });
T(s, [
  { text: "StreamView vive de suscripciones: su valor depende del engagement y la retención.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "No existe una vista integrada que diga qué contenido genera interacción, cuál satisface y cuál no se descubre.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Propósito: ", options: { bold: true } }, { text: "persuadir a la gerencia para decidir sobre descubrimiento, adquisición y datos, y habilitar la exploración autónoma." },
], { x: 0.75, y: 2.12, w: 3.65, h: 2.8, fontSize: 13 });
T(s, "¿Para quién es la solución?", { x: 5.0, y: 1.5, w: 4.5, h: 0.35, fontSize: 16, bold: true });
[["Directorio y gerencia general", "Qué pasa y qué decidir: presentación e informe."],
 ["Contenidos y adquisiciones", "Qué géneros e idiomas priorizar: dashboard."],
 ["Producto y experiencia de usuario", "Qué contenido no se descubre: dashboard."],
 ["Equipo de analítica", "Reproducir y extender: notebooks y código."]].forEach(([t, d], i) => {
  const y = 1.95 + i * 0.78;
  circulo(s, 5.0, y + 0.05, 0.36, i === 0 ? OSC : GRIS, String(i + 1), 12);
  T(s, t, { x: 5.5, y, w: 4.0, h: 0.3, fontSize: 13, bold: true });
  T(s, d, { x: 5.5, y: y + 0.3, w: 4.0, h: 0.35, fontSize: 12, color: GRIS });
});
T(s, "1 = audiencia primaria", { x: 5.0, y: 4.9, w: 4.5, h: 0.25, fontSize: MIN, color: GRIS, italic: true });
s.addNotes("[Claudio - 45 s] StreamView es un negocio de suscripción: gana cuando el usuario encuentra algo que ver y se queda. Hoy no hay una vista integrada que conecte oferta, interacción y satisfacción. Nuestra audiencia principal es el directorio y la gerencia general, que decide con poco tiempo y sin perfil técnico. Las gerencias de contenidos y de producto necesitan explorar el detalle, y el equipo de analítica, reproducirlo. Por eso el propósito es doble: persuadir para aprobar tres decisiones y habilitar a cada gerencia para responder sus propias preguntas.");

// ================================================================== 3 estrategia de comunicación
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Elegimos la estrategia según quién decide", "Estrategia de comunicación: qué hicimos y por qué", "Claudio Aro");
[["Pirámide invertida", "Conclusión y decisión en el primer minuto: la gerencia tiene poco tiempo."],
 ["Una idea central", "Un mensaje memorable que ordena todos los gráficos."],
 ["Arco en tres actos", "Contexto, conflicto y resolución: la tensión lleva a la decisión."],
 ["Títulos-mensaje", "El título dice el hallazgo; el gráfico lo demuestra."],
 ["Dos productos", "Presentación e informe para decidir; dashboard para explorar."],
 ["Lenguaje de negocio", "\"Tracción\" y \"joyas ocultas\" en vez de jerga estadística."]].forEach(([t, d], i) => {
  const x = 0.5 + (i % 3) * 3.05, y = 1.45 + Math.floor(i / 3) * 1.25;
  tarjeta(s, x, y, 2.85, 1.1, i === 0 ? PET_CLARO : FONDO);
  T(s, t, { x: x + 0.18, y: y + 0.12, w: 2.5, h: 0.3, fontSize: 14, bold: true, color: i === 0 ? PETROLEO : OSC });
  T(s, d, { x: x + 0.18, y: y + 0.47, w: 2.55, h: 0.58, fontSize: 12, color: GRIS });
});
tarjeta(s, 0.5, 4.05, 9, 0.95, CREMA);
T(s, [{ text: "Descartamos: ", options: { bold: true, color: ROJO } },
  { text: "el relato cronológico del análisis (entierra la conclusión), un único dashboard para todos (sobrecarga a quien decide) y la jerga estadística en el mensaje (aleja a la audiencia primaria)." }],
{ x: 0.7, y: 4.1, w: 8.6, h: 0.85, fontSize: 12, valign: "middle" });
s.addNotes("[Claudio - 40 s] La estrategia sale de la audiencia. Como la gerencia decide con poco tiempo, usamos pirámide invertida: la conclusión y la decisión llegan primero. Todo se ordena en torno a una idea central y a un arco de tres actos: contexto, conflicto y resolución. Cada gráfico lleva un título que dice el hallazgo, así nadie tiene que deducirlo. Hicimos dos productos porque las audiencias necesitan cosas distintas: esta presentación para decidir y un dashboard para explorar. Descartamos contar el análisis en orden cronológico, porque la conclusión quedaría al final.");

// ================================================================== 4 metodología CRISP-DM
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Seguimos CRISP-DM: del negocio al despliegue", "Metodología del proyecto: seis fases iterativas", "Claudio Aro");
[["Negocio", "Problema, 8 preguntas y 4 audiencias"],
 ["Datos", "2 fuentes, 32.000 registros; calidad y origen TMDB"],
 ["Preparación", "Limpieza, 21 géneros, 31.991 títulos"],
 ["Modelado", "Calificación ponderada, tracción, Lorenz (descriptivo)"],
 ["Evaluación", "76 cifras verificadas y pruebas de robustez"],
 ["Despliegue", "Dashboard, informe, presentación y proyecto reproducible"]].forEach(([t, d], i) => {
  const x = 0.5 + i * 1.528;
  tarjeta(s, x, 1.5, 1.36, 2.45, i >= 4 ? PET_CLARO : FONDO);
  circulo(s, x + 0.45, 1.65, 0.46, i >= 4 ? PETROLEO : OSC, String(i + 1), 14);
  T(s, t, { x: x + 0.08, y: 2.22, w: 1.2, h: 0.3, fontSize: 13, bold: true, align: "center" });
  T(s, d, { x: x + 0.1, y: 2.6, w: 1.16, h: 1.3, fontSize: MIN, color: GRIS, align: "center" });
  if (i < 5) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.375, y: 2.62, w: 0.14, h: 0.22, fill: { color: GRISC }, line: { color: GRISC } });
});
tarjeta(s, 0.5, 4.15, 9, 0.85, CREMA);
T(s, [{ text: "Iteramos: ", options: { bold: true } },
  { text: "notas 0 sin votos, volvimos a preparar; promedios engañosos, volvimos a modelar; votos de TMDB y no de suscriptores, volvimos al negocio para redefinir las metas." }],
{ x: 0.7, y: 4.2, w: 8.6, h: 0.75, fontSize: 12, valign: "middle" });
s.addNotes("[Claudio - 40 s] Trabajamos con CRISP-DM porque parte del negocio y no de los datos. Primero definimos el problema, las preguntas y las audiencias. Luego entendimos y preparamos los datos, construimos los indicadores, que en este caso son descriptivos y no predictivos, evaluamos verificando todas las cifras y, al final, desplegamos el dashboard, el informe y esta presentación. No fue lineal: por ejemplo, cuando vimos que los votos venían de TMDB y no de nuestros suscriptores, volvimos a la fase de negocio para redefinir cómo mediríamos las metas.");

// ================================================================== 5 datos
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Integramos dos fuentes en un catálogo comparable", "Descripción e integración de las fuentes de datos", "Claudio Aro");
[["Películas", "16.000 registros\n18 variables", AZUL, 1.55], ["Series", "16.000 registros\n16 variables", AMBAR, 3.0]].forEach(([n, d, c, y]) => {
  tarjeta(s, 0.5, y, 2.0, 1.25, c);
  T(s, n, { x: 0.7, y: y + 0.15, w: 1.7, h: 0.35, fontSize: 16, bold: true, color: c === AMBAR ? OSC : "FFFFFF" });
  T(s, d, { x: 0.7, y: y + 0.57, w: 1.7, h: 0.6, fontSize: 12, color: c === AMBAR ? OSC : "FFFFFF" });
});
s.addShape(pres.shapes.RIGHT_ARROW, { x: 2.62, y: 2.5, w: 0.45, h: 0.4, fill: { color: GRISC }, line: { color: GRISC } });
tarjeta(s, 3.2, 1.55, 3.3, 2.7, FONDO);
T(s, "Limpieza e integración", { x: 3.4, y: 1.7, w: 3.0, h: 0.3, fontSize: 13, bold: true });
T(s, ["21 géneros unificados en español", "Nota 0 sin votos = sin evaluar", "Calificación ponderada (bayesiana)",
  "Duplicados y columnas vacías fuera", "Textos al teclado latinoamericano"].map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })),
{ x: 3.4, y: 2.1, w: 3.0, h: 2.1, fontSize: MIN, paraSpaceAfter: 5 });
s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.62, y: 2.5, w: 0.45, h: 0.4, fill: { color: GRISC }, line: { color: GRISC } });
[["31.991", "títulos integrados"], ["13,2 M", "votos (interacción)"], ["83", "idiomas"], ["2010-2025", "años de estreno"]].forEach(([n, l], i) => {
  const y = 1.5 + i * 0.7;
  T(s, n, { x: 7.2, y, w: 2.3, h: 0.4, fontSize: 22, bold: true });
  T(s, l, { x: 7.2, y: y + 0.38, w: 2.3, h: 0.25, fontSize: MIN, color: GRIS });
});
tarjeta(s, 0.5, 4.4, 9, 0.65, CREMA);
T(s, [{ text: "Variables clave: ", options: { bold: true } }, { text: "votos = interacción | calificación ponderada = satisfacción | popularidad = atención | presupuesto y recaudación = rentabilidad. " },
  { text: "Limitación: ", options: { bold: true, color: ROJO } }, { text: "no hay datos individuales de reproducción ni suscripción." }],
{ x: 0.7, y: 4.45, w: 8.6, h: 0.55, fontSize: MIN, valign: "middle" });
s.addNotes("[Claudio - 40 s] Usamos dos fuentes: películas y series, 16 mil registros cada una, de 2010 a 2025. Las integramos en un catálogo de 31.991 títulos: unificamos 21 géneros, tratamos las notas cero sin votos como 'sin evaluar' y creamos una calificación ponderada, para que un título con dos votos y nota 10 no le gane a uno con 20 mil votos y nota 8,5. Los votos vienen de TMDB, no de nuestros suscriptores, así que los usamos como aproximación del engagement. Le paso la palabra a Guillermo.");

// ================================================================== 6 concentración
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "El 10% de los títulos concentra casi toda la interacción", "Curva de concentración de votos por título (Lorenz)", "Guillermo Cerda");
const xs = Array.from({ length: 11 }, (_, i) => `${i * 10}%`);
s.addChart(pres.charts.LINE, [
  { name: "Series", labels: xs, values: [0, 85.9, 94.8, 97.8, 99.0, 99.5, 99.8, 99.9, 100, 100, 100] },
  { name: "Películas", labels: xs, values: [0, 71.0, 84.3, 90.3, 93.8, 96.2, 97.8, 98.9, 99.7, 100, 100] },
  { name: "Distribución igualitaria", labels: xs, values: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100] },
], { x: 0.4, y: 1.4, w: 5.7, h: 3.6, chartColors: [AMBAR, AZUL, GRISC], lineSize: 3, lineDataSymbol: "none", ...EJES,
  catAxisTitle: "% acumulado de títulos (de más a menos votados)", showCatAxisTitle: true, catAxisTitleFontSize: MIN, catAxisTitleColor: GRIS,
  valAxisTitle: "% acumulado de votos", showValAxisTitle: true, valAxisTitleFontSize: MIN, valAxisTitleColor: GRIS,
  valAxisMaxVal: 100, valAxisMajorUnit: 25, showLegend: true, legendPos: "b", legendFontSize: MIN });
[["86%", "de los votos de series está en el 10% de títulos más votados", AMBAR],
 ["71%", "de los votos de películas está en el 10% de títulos más votados", AZUL],
 ["62%", "de las series tiene menos de 10 votos: son prácticamente invisibles", ROJO]].forEach(([n, l, c], i) => {
  const y = 1.45 + i * 1.18;
  T(s, n, { x: 6.4, y, w: 3.1, h: 0.58, fontSize: 36, bold: true, color: c });
  T(s, l, { x: 6.4, y: y + 0.6, w: 3.1, h: 0.5, fontSize: 12 });
});
pie(s, "curva de Lorenz; la distancia a la diagonal mide la concentración.");
s.addNotes("[Guillermo - 40 s] Primer hallazgo: la interacción está extremadamente concentrada. Este gráfico ordena los títulos de más a menos votados; si todos recibieran lo mismo, la curva sería la diagonal gris. En series, el 10% de los títulos se lleva el 86% de los votos y en películas el 71%. Y lo más preocupante, en rojo: 6 de cada 10 series tienen menos de 10 votos. Para el usuario, ese contenido prácticamente no existe.");

// ================================================================== 7 tracción
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Invertimos en géneros que no generan interacción", "Series: índice de tracción = % de votos / % de asignaciones del género (x1 = proporcional)", "Guillermo Cerda");
const gen = [["Ciencia ficción", 2.5], ["Acción/aventura", 2.0], ["Misterio", 1.75], ["Crimen", 1.7], ["Drama", 1.1], ["Animación", 0.95],
  ["Historia/bélico", 0.8], ["Comedia", 0.7], ["Infantil", 0.4], ["Familiar", 0.4], ["Telenovela", 0.4], ["Documental", 0.2],
  ["Noticias", 0.1], ["Reality", 0.1], ["Talk show", 0.06]].reverse();
const fmt = (v) => "x" + (v < 0.1 ? "0,06" : v.toFixed(1).replace(".", ","));
const lab = gen.map((g) => `${g[0]} ${fmt(g[1])}`);
const serie = (f) => gen.map((g) => (f(g[1]) ? g[1] : 0));
s.addChart(pres.charts.BAR, [
  { name: "Motor (x1,5 o más)", labels: lab, values: serie((v) => v >= 1.5) },
  { name: "Cercano a proporcional", labels: lab, values: serie((v) => v > 0.4 && v < 1.5) },
  { name: "Baja tracción (x0,4 o menos)", labels: lab, values: serie((v) => v <= 0.4) },
], { x: 0.4, y: 1.35, w: 5.9, h: 3.35, barDir: "bar", barGrouping: "stacked", chartColors: [PETROLEO, GRISC, ROJO], barGapWidthPct: 30,
  ...EJES, catAxisLabelFontSize: 10.5, catAxisLabelFrequency: 1, valAxisHidden: true, valGridLine: { style: "none" }, showLegend: false });
T(s, [{ text: "Azul petróleo: motor   ", options: { color: PETROLEO, bold: true } }, { text: "Gris: proporcional   ", options: { color: GRIS, bold: true } },
  { text: "Rojo: baja tracción", options: { color: ROJO, bold: true } }], { x: 0.5, y: 4.72, w: 5.8, h: 0.25, fontSize: MIN });
tarjeta(s, 6.6, 1.45, 2.9, 1.6, PET_CLARO);
T(s, "x2,5", { x: 6.8, y: 1.55, w: 2.5, h: 0.55, fontSize: 30, bold: true, color: PETROLEO });
T(s, "Ciencia ficción y fantasía: 6,7% de las asignaciones de género, 16,5% de los votos.", { x: 6.8, y: 2.15, w: 2.5, h: 0.8, fontSize: 12 });
tarjeta(s, 6.6, 3.2, 2.9, 1.6, ROJO_CLARO);
T(s, "x0,1", { x: 6.8, y: 3.3, w: 2.5, h: 0.55, fontSize: 30, bold: true, color: ROJO });
T(s, "Reality, talk show y noticias: 8% de las asignaciones de género, 0,7% de los votos.", { x: 6.8, y: 3.9, w: 2.5, h: 0.8, fontSize: 12 });
pie(s, "barras horizontales ordenadas; color solo en los extremos.");
s.addNotes("[Guillermo - 40 s] Segundo hallazgo: la oferta no está alineada con lo que genera interacción. Creamos el índice de tracción: el porcentaje de votos de un género dividido por su porcentaje de asignaciones de género (cada título aporta a todos sus géneros). Si vale 1, el género rinde lo que pesa. Ciencia ficción y fantasía rinde 2,5 veces su peso; acción, misterio y crimen también superan 1,5. En cambio reality, talk show y noticias ocupan el 8% de las asignaciones de género y generan el 0,7% de la interacción; dicho en títulos, el 14% de las series lleva alguno de esos géneros y recibe solo el 1,6% de los votos. En películas el patrón es el mismo. Ojo: reality y talk show pueden verse sin que nadie los califique en TMDB, por eso proponemos confirmarlo con reproducciones antes de desinvertir.");

// ================================================================== 8 joyas ocultas
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Y tenemos contenido valorado que nadie está viendo", "Películas: calidad vs interacción por género. Tamaño = cantidad de títulos", "Guillermo Cerda");
img(s, IMG + "fig02b_matriz_peliculas_presentacion.png", 0.4, 1.35, 6.3, 3.62);
tarjeta(s, 6.9, 1.45, 2.6, 3.5, PET_CLARO);
T(s, "Joyas ocultas", { x: 7.1, y: 1.6, w: 2.2, h: 0.35, fontSize: 16, bold: true, color: PETROLEO });
T(s, [
  { text: "Documental, música e historia: ", options: { bold: true } }, { text: "bien evaluados y poco descubiertos.", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "54% ", options: { bold: true, color: PETROLEO } }, { text: "de los documentales tiene nota 7 o más (26% del total).", options: { breakLine: true } },
  { text: " ", options: { breakLine: true, fontSize: 6 } },
  { text: "Es contenido ya pagado: exponerlo es la mejora más barata.", options: { italic: true } },
], { x: 7.1, y: 2.0, w: 2.25, h: 2.9, fontSize: 12 });
pie(s, "matriz de burbujas por cuadrantes; cada cuadrante es una acción.");
s.addNotes("[Guillermo - 40 s] Tercer hallazgo. Cruzamos calidad, eje vertical, con interacción, eje horizontal; cada burbuja es un género de películas y su tamaño es la cantidad de títulos. Arriba a la derecha están los motores. Arriba a la izquierda, en azul petróleo, las joyas ocultas: documental, música e historia. El 54% de los documentales tiene nota 7 o más, el doble que el promedio de películas, pero casi no reciben votos. Además, popularidad y calificación se relacionan débilmente: si recomendamos solo por popularidad, reforzamos la concentración y escondemos la calidad.");

// ================================================================== 9 idiomas
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "El contenido japonés es el mejor evaluado", "Películas: % de títulos con calificación 7 o más, por idioma original (200+ títulos evaluados)", "Guillermo Cerda");
const idi = [["Japonés", 52], ["Coreano", 39], ["Español", 35], ["Hindi", 31], ["Chino", 28], ["Alemán", 26], ["Italiano", 22], ["Inglés", 21], ["Francés", 19]].reverse();
const il = idi.map((x) => `${x[0]} ${x[1]}%`);
s.addChart(pres.charts.BAR, [
  { name: "Japonés", labels: il, values: idi.map((x) => (x[0] === "Japonés" ? x[1] : 0)) },
  { name: "Inglés (referencia)", labels: il, values: idi.map((x) => (x[0] === "Inglés" ? x[1] : 0)) },
  { name: "Otros", labels: il, values: idi.map((x) => (x[0] !== "Japonés" && x[0] !== "Inglés" ? x[1] : 0)) },
], { x: 0.4, y: 1.4, w: 5.6, h: 3.55, barDir: "bar", barGrouping: "stacked", chartColors: [PETROLEO, AZUL, GRISC], barGapWidthPct: 30,
  ...EJES, catAxisLabelFontSize: 12, catAxisLabelFrequency: 1, valAxisHidden: true, valGridLine: { style: "none" }, showLegend: false });
[["52% vs 21%", "de películas bien evaluadas: japonés vs inglés", PETROLEO], ["72%", "de las series japonesas tiene nota 7 o más (inglés: 60%)", PETROLEO],
 ["88%", "de los votos de películas es para contenido en inglés", AZUL]].forEach(([n, l, c], i) => {
  const y = 1.45 + i * 1.18;
  T(s, n, { x: 6.4, y, w: 3.1, h: 0.55, fontSize: 28, bold: true, color: c });
  T(s, l, { x: 6.4, y: y + 0.57, w: 3.1, h: 0.5, fontSize: 12 });
});
pie(s, "barras ordenadas; petróleo = mejor resultado, azul = referencia (inglés).");
s.addNotes("[Guillermo - 30 s] Cuarto hallazgo: el idioma. El inglés concentra el 88% de los votos de películas, pero no es donde está la mejor calidad percibida: el 52% de las películas japonesas tiene nota 7 o más, contra 21% en inglés. En películas, coreano y español también superan al inglés. En series, el 72% de las japonesas está bien evaluado, aunque ahí el orden depende del mínimo de votos. La oportunidad robusta es el anime.");

// ================================================================== 10 calidad y rentabilidad
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Calidad al alza; la rentabilidad no se recupera", "Evolución por año de estreno, 2010-2024", "Guillermo Cerda");
const anios = Array.from({ length: 15 }, (_, i) => (i % 2 === 0 ? String(2010 + i) : " ")); // 2010-2024; rótulo cada 2 años
T(s, "% de títulos con calificación 7 o más", { x: 0.5, y: 1.4, w: 4.4, h: 0.3, fontSize: 13, bold: true });
s.addChart(pres.charts.LINE, [
  { name: "Series", labels: anios, values: [56.2, 55.9, 56.6, 58.1, 59.3, 60.1, 56.4, 58.5, 64.2, 67.1, 66.6, 63.6, 60.1, 66.7, 71.1] },
  { name: "Películas", labels: anios, values: [20.3, 20.7, 20.6, 22.1, 21.5, 23.1, 24.9, 27.0, 27.7, 31.3, 30.0, 30.8, 27.5, 28.3, 28.4] },
], { x: 0.4, y: 1.7, w: 4.5, h: 2.75, chartColors: [AMBAR, AZUL], lineSize: 3, lineDataSymbol: "none", ...EJES,
  valAxisMinVal: 0, valAxisMaxVal: 80, valAxisMajorUnit: 20, catAxisLabelFrequency: 2, showLegend: true, legendPos: "b", legendFontSize: MIN });
T(s, "ROI mediano de películas (%)", { x: 5.2, y: 1.4, w: 4.3, h: 0.3, fontSize: 13, bold: true });
s.addChart(pres.charts.LINE, [
  { name: "ROI mediano", labels: anios, values: [70, 108, 86, 118, 111, 113, 93, 110, 95, 102, -17, 0, 24, 26, 61] },
], { x: 5.1, y: 1.7, w: 4.4, h: 2.75, chartColors: [ROJO], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 5, ...EJES,
  valAxisMinVal: -40, valAxisMaxVal: 120, valAxisMajorUnit: 40, catAxisLabelFrequency: 2, showLegend: false, catAxisLabelPos: "low" });
T(s, "2020: -17%", { x: 7.1, y: 4.02, w: 1.1, h: 0.25, fontSize: 12, bold: true, color: ROJO });
tarjeta(s, 0.5, 4.5, 9, 0.55, CREMA);
T(s, [{ text: "La calidad no es el problema: ", options: { bold: true } }, { text: "películas de 20% a 28% y series de 56% a 71% bien evaluadas. " },
  { text: "Popularidad y calificación apenas se relacionan (0,23 y 0,17).", options: { bold: true } }],
{ x: 0.7, y: 4.52, w: 8.6, h: 0.5, fontSize: 12, valign: "middle" });
pie(s, null);
s.addNotes("[Guillermo - 30 s] En el tiempo, la proporción de títulos bien evaluados tiende a subir, con retrocesos: películas de 20% a 28% y series de 56% a 71%. Parte puede ser sesgo de antigüedad, porque los títulos recientes tienen menos votos; aun así, la calidad no es el problema. En rojo, la alerta: la rentabilidad de las películas cayó a -17% en 2020 y en 2024 va en 61%, bajo el 100% previo.");

// ================================================================== 11 justificación técnica
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Cada gráfico se eligió por la tarea que resuelve", "Justificación técnica de las representaciones y atributos visuales", "Guillermo Cerda");
const cab = (t) => ({ text: t, options: { bold: true, color: "FFFFFF", fill: { color: OSC } } });
const filas = [
  [cab("Tarea"), cab("Gráfico"), cab("Atributo"), cab("Descartado")],
  ["Concentración", "Curva de Lorenz", "Posición", "Pareto de 16.000 barras"],
  ["Oferta vs. interacción", "Barras ordenadas", "Longitud", "Torta: ángulos imprecisos"],
  ["Calidad vs. interacción", "Burbujas por cuadrantes (log)", "Posición + tamaño", "Tabla: exige comparar números"],
  ["Ranking de idiomas", "Barras horizontales", "Longitud", "Mapa: el idioma no es geográfico"],
  ["Evolución anual", "Línea temporal", "Pendiente", "Barras por año: fragmentan"],
];
s.addTable(filas, { x: 0.5, y: 1.45, w: 6.0, colW: [1.45, 1.6, 1.15, 1.8], fontFace: F, fontSize: MIN, color: OSC,
  border: { type: "solid", pt: 0.5, color: "E5E7EB" }, fill: { color: "FFFFFF" }, rowH: 0.42, valign: "middle", margin: 0.05 });
tarjeta(s, 6.75, 1.45, 2.75, 3.3, PET_CLARO);
T(s, "Principios aplicados", { x: 6.95, y: 1.58, w: 2.4, h: 0.3, fontSize: 14, bold: true, color: PETROLEO });
T(s, ["Un color, un significado: petróleo = oportunidad, rojo = alerta", "Gris para el contexto: el ojo va primero al dato destacado",
  "Sin par verde-rojo (daltonismo)", "Etiquetas directas y texto de 11 pt o más", "Escala log: la tracción va de 0,06 a 2,5"]
  .map((t, i, a) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })),
{ x: 6.95, y: 1.98, w: 2.45, h: 2.7, fontSize: MIN, paraSpaceAfter: 6 });
T(s, "Posición y longitud son los atributos que el ojo compara con más precisión (Cleveland y McGill, 1984); el color se reserva para el énfasis.",
  { x: 0.5, y: 4.5, w: 6.0, h: 0.5, fontSize: MIN, color: GRIS, italic: true });
s.addNotes("[Guillermo - 40 s] ¿Por qué estos gráficos? Cada uno responde a una tarea. Para concentración, la curva de Lorenz, que es el estándar; con 16 mil títulos, un Pareto sería ilegible. Para comparar géneros e idiomas, barras ordenadas, porque la longitud se compara con precisión; descartamos tortas. Para cruzar calidad e interacción, burbujas por cuadrantes en escala log. Y para el tiempo, líneas. El color tiene un solo significado: petróleo es oportunidad, rojo es alerta y el gris es contexto; evitamos verde y rojo por el daltonismo. Le paso la palabra a Manuel.");

// ================================================================== 12 idea central
s = pres.addSlide(); s.background = { color: OSC };
T(s, "LA IDEA CENTRAL", { x: 0.8, y: 1.2, w: 8.4, h: 0.35, fontSize: 13, bold: true, color: AMBAR, charSpacing: 2 });
T(s, "StreamView no necesita más títulos:\nnecesita que los títulos correctos sean descubiertos.", { x: 0.8, y: 1.75, w: 8.4, h: 1.7, fontSize: 30, bold: true, color: "FFFFFF" });
T(s, "Concentración (86%)  +  oferta desalineada (x0,1)  +  calidad escondida (joyas ocultas)  =  valor que no llega al usuario y riesgo para la retención.",
  { x: 0.8, y: 3.75, w: 8.4, h: 0.8, fontSize: 15, color: "D9DCE0" });
T(s, "Manuel Díaz", { x: 7.0, y: 0.1, w: 2.5, h: 0.22, fontSize: MIN, color: GRISC, align: "right" });
s.addNotes("[Manuel - 20 s] Si juntamos todo: la interacción se concentra, la oferta no está alineada con lo que el usuario busca y el contenido que más se valora está escondido. Nuestra conclusión es simple: StreamView no necesita más títulos, necesita que los títulos correctos sean descubiertos.");

// ================================================================== 13 dashboard
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Un dashboard para que cada gerencia explore", "Streamlit + Plotly: 6 páginas, 6 KPIs, 5 filtros globales y exploración a nivel de título", "Manuel Díaz");
const r = img(s, IMG + "dash_presentacion.png", 0.4, 1.35, 6.45, 3.7);
s.addShape(pres.shapes.RECTANGLE, { x: r.x, y: r.y, w: r.w, h: r.h, fill: { type: "none" }, line: { color: GRISC, width: 0.75 } });
// marcadores numerados sobre la captura (posiciones relativas medidas en la imagen)
[[0.235, 0.20], [0.175, 0.29], [0.175, 0.70], [0.60, 0.44]].forEach(([px, py], i) => {
  circulo(s, r.x + px * r.w - 0.17, r.y + py * r.h - 0.17, 0.34, OSC, String(i + 1), 12);
});
[["KPIs con comparación", "Diferencia de la selección contra el catálogo completo."],
 ["Navegación", "6 páginas: resumen, géneros, idiomas, tendencias, explorador, metodología."],
 ["Filtros globales", "Tipo, años, género, idioma y votos mínimos; botón para restablecer."],
 ["Gráficos interactivos", "Tooltips, selección por clic o lazo, búsqueda y descarga CSV."]].forEach(([t, d], i) => {
  const y = 1.4 + i * 0.9;
  circulo(s, 7.0, y, 0.34, OSC, String(i + 1), 12);
  T(s, t, { x: 7.42, y: y - 0.02, w: 2.1, h: 0.28, fontSize: 12, bold: true });
  T(s, d, { x: 7.42, y: y + 0.27, w: 2.1, h: 0.6, fontSize: MIN, color: GRIS });
});
pie(s, "captura de la página 1 del dashboard (la demo en vivo es opcional).");
s.addNotes("[Manuel - 60 s] Para que estas preguntas no dependan de un informe, construimos un dashboard en Streamlit con Plotly. Uno: seis KPIs que muestran cuánto se aleja la selección del catálogo completo. Dos: seis páginas navegables desde la barra lateral. Tres: filtros globales por tipo, años, género, idioma y votos mínimos. Cuatro: gráficos interactivos; por ejemplo, en la matriz de géneros se puede seleccionar una burbuja y ver sus títulos mejor evaluados, y en el explorador se activa 'solo joyas ocultas' para obtener la lista que producto podría usar en una fila de recomendación. [Si hay tiempo y el equipo lo permite, mostrar en vivo; si no, explicar sobre la captura.] Los colores son los mismos del informe: azul películas, ámbar series, petróleo oportunidad y rojo alerta.");

// ================================================================== 14 recomendaciones
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Tres decisiones, con metas medibles", "Cada recomendación se apoya en un hallazgo del análisis", "Manuel Díaz");
[["1", "Exponer las joyas ocultas", "Producto / UX", "Filas de \"joyas ocultas\" y cuota de exposición para títulos bien evaluados con pocos votos.", "Bajar el % de catálogo sin reproducciones (proxy hoy: 62% de series con <10 votos)", "Evidencia: diap. 6 y 8"],
 ["2", "Reorientar la adquisición", "Contenidos", "Priorizar ciencia ficción, acción, misterio y crimen; revisar reality y talk show; ampliar anime.", "Tracción con reproducciones de nuevas adquisiciones >= x1,0", "Evidencia: diap. 7 y 9"],
 ["3", "Medir el comportamiento real", "Analítica / TI", "Integrar reproducciones, abandono, suscripciones y dispositivos al dashboard.", "Dashboard de retención en 6 meses", "Evidencia: limitación, diap. 15"]].forEach(([n, t, rs, d, k, ev], i) => {
  const x = 0.5 + i * 3.05;
  tarjeta(s, x, 1.45, 2.85, 3.55, FONDO);
  circulo(s, x + 0.2, 1.62, 0.45, OSC, n);
  T(s, t, { x: x + 0.78, y: 1.62, w: 1.95, h: 0.5, fontSize: 13, bold: true, valign: "middle" });
  T(s, rs, { x: x + 0.2, y: 2.25, w: 2.45, h: 0.25, fontSize: MIN, bold: true, color: GRIS });
  T(s, d, { x: x + 0.2, y: 2.55, w: 2.45, h: 1.0, fontSize: 12 });
  T(s, ev, { x: x + 0.2, y: 3.6, w: 2.45, h: 0.3, fontSize: MIN, bold: true, color: PETROLEO });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.15, y: 4.0, w: 2.55, h: 0.85, fill: { color: PET_CLARO }, line: { color: PET_CLARO }, rectRadius: 0.06 });
  T(s, [{ text: "Meta: ", options: { bold: true, color: PETROLEO } }, { text: k }], { x: x + 0.28, y: 4.05, w: 2.3, h: 0.75, fontSize: MIN, valign: "middle" });
});
pie(s, null);
s.addNotes("[Manuel - 50 s] Tres decisiones, cada una con su evidencia. Primera, para producto: filas de joyas ocultas y un ranking que combine popularidad y calidad, porque la interacción se concentra y hay contenido valorado que no se ve. La meta se medirá con reproducciones propias; hoy el proxy es que el 62% de las series tiene menos de 10 votos. Segunda, para contenidos: priorizar los géneros de alta tracción y ampliar el anime. Tercera, para analítica: medir reproducción, abandono y suscripción, porque hoy dependemos de votos externos.");

// ================================================================== 15 evaluación crítica
s = pres.addSlide(); s.background = { color: "FFFFFF" };
titulo(s, "Evaluación crítica de nuestra solución", "Fortalezas, limitaciones y oportunidades de mejora", "Manuel Díaz");
[["Fortalezas", PETROLEO, ["Mismos cálculos en informe, figuras y dashboard", "76 cifras verificadas automáticamente", "Películas y series comparables", "Proyecto reproducible (CRISP-DM)"]],
 ["Limitaciones", ROJO, ["Votos de TMDB, no de suscriptores", "Muestra de 1.000 títulos por año y tipo", "Títulos de 2025 con pocos votos", "Datos financieros en 21% de películas"]],
 ["Mejoras", OSC, ["Integrar datos de uso y suscripción", "Publicar con actualización automática", "Pruebas de usabilidad por gerencia", "Medir impacto con pruebas A/B"]]].forEach(([t, c, items], i) => {
  const x = 0.5 + i * 3.05;
  tarjeta(s, x, 1.45, 2.85, 3.55, FONDO);
  T(s, t, { x: x + 0.2, y: 1.6, w: 2.45, h: 0.35, fontSize: 16, bold: true, color: c });
  T(s, items.map((it, j) => ({ text: it, options: { bullet: true, breakLine: j < items.length - 1 } })),
    { x: x + 0.2, y: 2.05, w: 2.5, h: 2.85, fontSize: 12, paraSpaceAfter: 10 });
});
s.addNotes("[Manuel - 35 s] Evaluamos críticamente la solución. Fortalezas: todos los productos usan el mismo código, verificamos automáticamente las 76 cifras del informe y el proyecto se reproduce completo. Limitación principal: los votos vienen de TMDB y no de nuestros suscriptores, y la muestra es de mil títulos por año. Como mejora, integrar datos de uso, publicar el dashboard y validarlo con cada gerencia.");

// ================================================================== 16 cierre
s = pres.addSlide(); s.background = { color: OSC };
T(s, "En resumen", { x: 0.8, y: 0.9, w: 8.4, h: 0.4, fontSize: 15, bold: true, color: AMBAR });
T(s, [
  { text: "La interacción se concentra en el 10% de los títulos y 6 de cada 10 series no se descubren.", options: { bullet: true, breakLine: true } },
  { text: "La oferta no está alineada con lo que genera interacción, y el contenido mejor valorado está escondido.", options: { bullet: true, breakLine: true } },
  { text: "La mejor inversión inmediata es hacer visible el valor que ya tenemos, y medir si retiene.", options: { bullet: true } },
], { x: 0.8, y: 1.45, w: 8.4, h: 2.1, fontSize: 17, color: "FFFFFF", paraSpaceAfter: 10 });
T(s, "Gracias. ¿Preguntas?", { x: 0.8, y: 3.9, w: 8.4, h: 0.7, fontSize: 32, bold: true, color: "FFFFFF" });
T(s, "Claudio Aro  |  Guillermo Cerda  |  Manuel Díaz", { x: 0.8, y: 4.75, w: 8.4, h: 0.3, fontSize: 13, color: GRISC });
s.addNotes("[Manuel - 15 s] Cerramos con tres ideas: la interacción está concentrada, la oferta no está alineada y la calidad está escondida. Por eso proponemos hacer visible el valor que ya existe y medir si eso mejora la retención. Muchas gracias; quedamos atentos a sus preguntas.");

pres.writeFile({ fileName: SALIDA }).then(() => console.log("ok"));
