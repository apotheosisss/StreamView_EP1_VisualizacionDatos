const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, AlignmentType,
  HeadingLevel, WidthType, ShadingType, BorderStyle, LevelFormat, PageBreak, Footer, Header,
  PageNumber, TableOfContents, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo, PositionalTabLeader,
} = require("docx");
const sizeOf = (p) => {
  // lee ancho/alto de un PNG sin dependencias
  const b = fs.readFileSync(p);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
};

const AZUL = "2E4A62", AMBAR = "E09F3E", ROJO = "C8102E", GRIS = "5B6270", TEXTO = "1F2430";
const ANCHO = 9360; // DXA contenido carta con margen 1"

// texto con **negrita**
function runs(texto, extra = {}) {
  const partes = texto.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return partes.map((t) => t.startsWith("**")
    ? new TextRun({ text: t.slice(2, -2), bold: true, ...extra })
    : new TextRun({ text: t, ...extra }));
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o.run || {}), spacing: { after: 120, line: 276 },
  alignment: o.align || AlignmentType.JUSTIFIED, ...o.para });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)], pageBreakBefore: true });
const H1b = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(t)] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(t)] });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun(t)] });
const B = (t, nivel = 0) => new Paragraph({ numbering: { reference: "guion", level: nivel }, children: runs(t),
  spacing: { after: 60, line: 264 } });
const N = (t, ref = "num") => new Paragraph({ numbering: { reference: ref, level: 0 }, children: runs(t),
  spacing: { after: 60, line: 264 } });
const SALTO = () => new Paragraph({ children: [new PageBreak()] });

function FIG(ruta, pie, anchoPulg = 6.5) {
  const { w, h } = sizeOf(ruta);
  const wpx = anchoPulg * 96, hpx = wpx * h / w;
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(ruta),
        transformation: { width: Math.round(wpx), height: Math.round(hpx) },
        altText: { title: pie, description: pie, name: pie } })] }),
    new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: 200 },
      children: runs(pie, { size: 18, color: GRIS, italics: true }) }),
  ];
}

const borde = { style: BorderStyle.SINGLE, size: 4, color: "D0D3D8" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
function TABLA(filas, anchos, opts = {}) {
  const total = anchos.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: anchos,
    rows: filas.map((fila, i) => new TableRow({
      tableHeader: i === 0, cantSplit: true,
      children: fila.map((celda, j) => new TableCell({
        borders: bordes, width: { size: anchos[j], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        shading: i === 0 ? { fill: AZUL, type: ShadingType.CLEAR, color: "auto" }
          : (i % 2 === 0 ? { fill: "F3F4F6", type: ShadingType.CLEAR, color: "auto" } : undefined),
        children: String(celda).split("\n").map((linea) => new Paragraph({
          spacing: { after: 20 },
          children: runs(linea, { size: opts.size || 18, color: i === 0 ? "FFFFFF" : TEXTO, bold: i === 0 ? true : undefined }),
        })),
      })),
    })),
  });
}
const ESPACIO = () => new Paragraph({ spacing: { after: 120 }, children: [] });

function CAJA(titulo, lineas, color = "FFF4E5") {
  return new Table({
    width: { size: ANCHO, type: WidthType.DXA }, columnWidths: [ANCHO],
    rows: [new TableRow({ children: [new TableCell({
      borders: { top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, bottom: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
        left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" } },
      width: { size: ANCHO, type: WidthType.DXA }, shading: { fill: color, type: ShadingType.CLEAR, color: "auto" },
      margins: { top: 140, bottom: 140, left: 200, right: 200 },
      children: [new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: titulo, bold: true, color: AZUL, size: 22 })] }),
        ...lineas.map((l) => new Paragraph({ spacing: { after: 60 }, children: runs(l, { size: 20 }) }))],
    })] })],
  });
}

function documento(secciones, titulo) {
  return new Document({
    creator: "Claudio Aro, Guillermo Cerda, Manuel Díaz", title: titulo,
    styles: {
      default: { document: { run: { font: "Arial", size: 21, color: TEXTO } } },
      paragraphStyles: [
        { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 32, bold: true, font: "Arial", color: AZUL }, paragraph: { spacing: { before: 120, after: 200 }, outlineLevel: 0 } },
        { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 25, bold: true, font: "Arial", color: AZUL }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
        { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
          run: { size: 22, bold: true, font: "Arial", color: GRIS }, paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
      ],
    },
    numbering: { config: [
      { reference: "guion", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "-", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "-", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 1080, hanging: 270 } } } }] },
      ...["num", "num2", "num3", "num4", "num5", "num6"].map((r) => ({ reference: r, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 360 } } } }] })),
    ] },
    sections: secciones.map((s) => ({
      properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, right: 1440, bottom: 1300, left: 1440 } } },
      headers: s.sinPie ? undefined : { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: titulo + " | ADY1104 Visualización de Datos", size: 16, color: GRIS })] })] }) },
      footers: s.sinPie ? undefined : { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Página ", size: 16, color: GRIS }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: GRIS })] })] }) },
      children: s.children,
    })),
  });
}

function PORTADA(titulo, subtitulo) {
  const c = (t, o) => new Paragraph({ alignment: AlignmentType.LEFT, spacing: { after: o.after || 120 }, children: [new TextRun({ text: t, ...o })] });
  return [
    c("Duoc UC | Escuela de Informática y Telecomunicaciones", { size: 20, color: GRIS, after: 60 }),
    c("Ingeniería en Informática, mención Ciencia de Datos | Sede Puerto Montt", { size: 20, color: GRIS, after: 1800 }),
    c("ADY1104 VISUALIZACIÓN DE DATOS", { size: 22, bold: true, color: ROJO, after: 200 }),
    c(titulo, { size: 52, bold: true, color: AZUL, after: 200 }),
    c(subtitulo, { size: 28, color: TEXTO, after: 1600 }),
    new Table({ width: { size: 6000, type: WidthType.DXA }, columnWidths: [2000, 4000], rows: [
      ["Evaluación", "Evaluación Parcial N°1 (Encargo y Presentación)"],
      ["Cliente", "StreamView Analytics (caso)"],
      ["Integrantes", "Claudio Aro\nGuillermo Cerda\nManuel Díaz"],
      ["Docente", "Claudio Andrés Gonzalez Penaloza"],
      ["Fecha", "Septiembre de 2026"],
    ].map((f) => new TableRow({ children: f.map((t, j) => new TableCell({
      borders: { top: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, bottom: { style: BorderStyle.SINGLE, size: 2, color: "D0D3D8" },
        left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" }, right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" } },
      width: { size: j ? 4000 : 2000, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 60, right: 60 },
      children: t.split("\n").map((l) => new Paragraph({ children: [new TextRun({ text: l, size: 21, bold: j === 0, color: j ? TEXTO : GRIS })] })),
    })) })) }),
  ];
}

function INDICE(titulos, paginas) {
  return titulos.map((t) => new Paragraph({ spacing: { after: 100 }, children: [
    new TextRun({ text: t, size: 22 }),
    new TextRun({ children: [new PositionalTab({ alignment: PositionalTabAlignment.RIGHT,
      relativeTo: PositionalTabRelativeTo.MARGIN, leader: PositionalTabLeader.DOT })] }),
    new TextRun({ text: String(paginas[t] || ""), size: 22 }),
  ] }));
}

module.exports = { INDICE, P, H1, H1b, H2, H3, B, N, SALTO, FIG, TABLA, CAJA, ESPACIO, documento, PORTADA, runs, Packer,
  TableOfContents, Paragraph, TextRun, AlignmentType, AZUL, ROJO, GRIS };
