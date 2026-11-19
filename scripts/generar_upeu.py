#!/usr/bin/env python3
"""
generar_upeu.py — Los entregables S1_E1 y S1_E2 con la plantilla UPeU «Plan de Auditoría de Sistemas» (portada con logo, índice,
títulos numerados, encabezado y tablas de la universidad), en vez de la plantilla de la rúbrica.

No repite el contenido: ejecuta generar_s1_e1.py y generar_s1_e2.py «en seco», capturando lo que cada uno escribiría
(secciones, tablas y figuras) y lo vuelca en la plantilla UPeU con sus estilos. Así los dos formatos salen de la misma fuente.

    python3 scripts/generar_upeu.py            # genera los dos en entregables_upeu/
"""
import importlib
import re
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph

import comun

RAIZ = Path(__file__).resolve().parents[1]
UPEU = RAIZ / "templates/Plantilla Plan de Auditoria de Sistemas.docx"
SALIDA = RAIZ / "entregables_upeu"
ANCHO_TEXTO_CM = 15.0                    # A4 con márgenes de 3 cm
ANCHO_TABLA_DXA = 8500

UPEU_CORREGIDA = RAIZ / "templates/Plantilla Plan de Auditoria de Sistemas (logo alineado).docx"

PORTADAS = {
    "s2_e1": {"titulo": ("PLANIFICACIÓN E IMPLEMENTACIÓN", "DEL SGSI"), "entregable": "SEMESTRE 2 · ENTREGABLE 1 DE 3"},
    "s2_e2": {"titulo": ("IMPLEMENTACIÓN, TESTING", "Y MONITOREO DE RED"), "entregable": "SEMESTRE 2 · ENTREGABLE 2 DE 3"},
    "s2_e3": {"titulo": ("IMPLEMENTACIÓN, GESTIÓN Y CONTROL", "DE CENTRO DE DATOS"), "entregable": "SEMESTRE 2 · ENTREGABLE 3 DE 3"},
    "s1_e1": {"titulo": ("ANÁLISIS Y DISEÑO", "DE RED"), "entregable": "SEMESTRE 1 · ENTREGABLE 1 DE 2"},
    "s1_e2": {"titulo": ("ANÁLISIS Y DISEÑO DE", "CENTRO DE DATOS HÍBRIDO"), "entregable": "SEMESTRE 1 · ENTREGABLE 2 DE 2"},
}


# ── 0. Encabezado ────────────────────────────────────────────────────────────────────────────────────────────────
def corregir_logo_del_encabezado(doc):
    """El logo quedaba corrido: estaba dentro de una tabla (con su margen interno de celda) y su párrafo, de estilo Normal0,
    heredaba una sangría de primera línea de 1,25 cm. Sin ajustes sueltos sobre párrafos:
      · el estilo «Header» (que ya trae las tabulaciones centro y derecha) pierde la sangría de primera línea y la justificación;
      · el encabezado pasa a ser UN párrafo de estilo Header: logo, tabulaciones y «Página N» a la derecha."""
    header = doc.styles["Header"]
    header.paragraph_format.first_line_indent = Cm(0)
    header.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for sec in doc.sections:
        for h in (sec.header, sec.first_page_header, sec.even_page_header):
            if h.is_linked_to_previous:
                continue
            for tbl in list(h._element.findall(qn("w:tbl"))):
                celdas = tbl.findall(".//" + qn("w:tc"))
                logo = celdas[0].find(".//" + qn("w:r"))
                pagina = celdas[1].findall(".//" + qn("w:r"))
                p = OxmlElement("w:p")
                ppr = OxmlElement("w:pPr")
                ps = OxmlElement("w:pStyle")
                ps.set(qn("w:val"), "Header")
                ppr.append(ps)
                p.append(ppr)
                p.append(logo)
                for _ in range(2):                    # centro y derecha: «Página N» queda en el margen derecho
                    r = OxmlElement("w:r")
                    r.append(OxmlElement("w:tab"))
                    p.append(r)
                for r in pagina:
                    p.append(r)
                tbl.addprevious(p)
                h._element.remove(tbl)


def plantilla_corregida():
    """Una copia de la plantilla UPeU con el logo alineado (la original no se toca)."""
    if not UPEU.exists():                       # la original ya no está: la copia con el logo alineado es la base
        return UPEU_CORREGIDA
    doc = docx.Document(str(UPEU))
    corregir_logo_del_encabezado(doc)
    doc.save(str(UPEU_CORREGIDA))
    return UPEU_CORREGIDA


# ── 1. Captura del contenido ─────────────────────────────────────────────────────────────────────────────────────
def capturar(modulo):
    """Ejecuta main() del generador con sus funciones de escritura sustituidas por un registro: [(tipo, …)]."""
    eventos, pies, emitidos = [], {}, set()
    plantilla = docx.Document(str(modulo.PLANTILLA))
    h1 = {}
    for p in plantilla.paragraphs:
        m = re.match(r"^(\d+)\.\s+(.*)$", p.text.strip())
        if p.style.name == "Heading 1" and m:
            h1[m.group(1)] = m.group(2)

    def seccion(doc, encabezado, items):
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.*)$", encabezado.strip())
        numero, titulo = m.group(1), m.group(2)
        nivel = numero.count(".") + 1
        if nivel == 2 and numero.split(".")[0] not in emitidos:
            emitidos.add(numero.split(".")[0])
            eventos.append(("h1", h1[numero.split(".")[0]]))
        if nivel == 1:
            emitidos.add(numero)
        if titulo.strip() == "Referencias":
            eventos.append(("biblio", [t for _, t in items]))
            return
        eventos.append(("h%d" % nivel, titulo))
        for estilo, texto in items:
            eventos.append(("bul" if estilo == "List Paragraph" else "p", texto))

    def tabla(tbl, filas, encabezado=None):
        eventos.append(("tabla", encabezado or [c.text for c in tbl.rows[0].cells], [list(map(str, f)) for f in filas]))

    def figura(doc, tbl, png, ancho_cm=comun.ANCHO_UTIL_CM):
        sig = tbl._tbl.getnext()
        pie = Paragraph(sig, doc).text if sig is not None else ""
        eventos.append(("fig", png, pie.strip(), ancho_cm))

    modulo.reemplazar_seccion, modulo.llenar_tabla, modulo.poner_figura = seccion, tabla, figura
    modulo.cambiar_texto_que_contiene = lambda *a, **k: None
    modulo.cambiar_pie_de_figura = lambda doc, prefijo, nuevo: pies.__setitem__(prefijo, nuevo)
    if hasattr(modulo, "renombrar_titulo"):
        modulo.renombrar_titulo = lambda *a, **k: None
    modulo.SALIDA = Path(tempfile.gettempdir()) / "descartar.docx"
    # los generadores usan doc para leer tablas de la plantilla vieja; el documento que se guarda aquí se descarta
    modulo.main()
    return eventos, pies


# ── 2. Escritura en la plantilla UPeU ────────────────────────────────────────────────────────────────────────────
def estilo_parrafo(p, nombre):
    p.style = p.part.document.styles[nombre]


def agregar_texto(p, texto, negrita_inicial=False):
    """Un párrafo con el texto; en las viñetas, lo que está antes de «: » va en negrita (el término que se explica)."""
    if negrita_inicial and ": " in texto and len(texto.split(": ", 1)[0]) <= 70 and "." not in texto.split(": ", 1)[0]:
        cabeza, resto = texto.split(": ", 1)
        p.add_run(cabeza + ":").bold = True
        p.add_run(" " + resto)
    else:
        p.add_run(texto)


def nuevo_parrafo(doc, ancla, estilo, texto="", negrita_inicial=False):
    el = OxmlElement("w:p")
    ancla.addprevious(el)
    p = Paragraph(el, doc._body)
    estilo_parrafo(p, estilo)
    if texto:
        agregar_texto(p, texto, negrita_inicial)
    return p


def pesos_columnas(encabezado, filas):
    pesos = []
    for i, h in enumerate(encabezado):
        largo = max([len(h)] + [len(f[i]) for f in filas])
        pesos.append(max(min(largo, 46), 9))
    total = sum(pesos)
    return [max(int(ANCHO_TABLA_DXA * w / total), 900) for w in pesos]


def nueva_tabla(doc, ancla, prototipo, encabezado, filas):
    """Una tabla con el estilo TablaPlan de la plantilla (cabecera azul), a partir de la tabla de ejemplo."""
    tbl = deepcopy(prototipo)
    trs = tbl.findall(qn("w:tr"))
    cab_tr, cuerpo_tr = trs[0], trs[1]
    for tr in trs:
        tbl.remove(tr)
    anchos = pesos_columnas(encabezado, filas)
    grid = tbl.find(qn("w:tblGrid"))
    for g in list(grid):
        grid.remove(g)
    for a in anchos:
        g = OxmlElement("w:gridCol")
        g.set(qn("w:w"), str(a))
        grid.append(g)

    def fila(modelo, valores, es_cabecera):
        tr = deepcopy(modelo)
        tcs = tr.findall(qn("w:tc"))
        for tc in tcs[1:]:
            tr.remove(tc)
        base = tcs[0]
        tr.remove(base)
        for valor, ancho in zip(valores, anchos):
            tc = deepcopy(base)
            tc.find(qn("w:tcPr")).find(qn("w:tcW")).set(qn("w:w"), str(ancho))
            p = tc.find(qn("w:p"))
            for r in p.findall(qn("w:r")):
                p.remove(r)
            run = OxmlElement("w:r")
            t = OxmlElement("w:t")
            t.text = valor
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            run.append(t)
            p.append(run)
            tr.append(tc)
        trpr = tr.find(qn("w:trPr"))
        if trpr is None:
            trpr = OxmlElement("w:trPr")
            tr.insert(0, trpr)
        if es_cabecera:
            trpr.append(OxmlElement("w:tblHeader"))               # se repite al cambiar de página
        trpr.append(OxmlElement("w:cantSplit"))                    # una fila no se parte entre páginas
        return tr

    tbl.append(fila(cab_tr, encabezado, True))
    for f in filas:
        tbl.append(fila(cuerpo_tr, f, False))
    ancla.addprevious(tbl)
    # un párrafo vacío tras la tabla, para que no se pegue al texto siguiente
    nuevo_parrafo(doc, ancla, "Texto del Plan")


def portada(doc, clave):
    datos_p = PORTADAS[clave]
    cuerpo = list(doc.element.body)
    P = lambda i: Paragraph(cuerpo[i], doc._body)
    titulo = P(3)
    for r in list(titulo.runs):
        r._r.getparent().remove(r._r)
    titulo.add_run(datos_p["titulo"][0]).add_break()
    titulo.add_run(datos_p["titulo"][1])
    campos = {4: "ENTREGABLE", 5: datos_p["entregable"],
              7: "ORGANIZACIÓN", 8: "Co-Logistic S.A.C.",
              10: "MARCO DE REFERENCIA", 11: "ISO/IEC 27001:2022 · ISO/IEC 27002:2022",
              13: "EQUIPO",
              15: "DOCENTE DEL CURSO", 16: "[Grado y nombre del docente]"}
    for i, texto in campos.items():
        p = P(i)
        for r in list(p.runs)[1:]:
            r._r.getparent().remove(r._r)
        p.runs[0].text = texto
    equipo_p = P(14)
    for r in list(equipo_p.runs)[1:]:
        r._r.getparent().remove(r._r)
    lineas_equipo = [
        "Jhack Ernesto Quispe Mamani · Abel Is-boset Guevara Huasco · David Edison Guerra Ordoñez",
        "Alvaro Kenji Cuti Magaño · Javier Kevin Tello Rivas · Richard Josef Yaqui Inocente",
        "Daniel Hernan Calderon Camacho · Joshua Alfonzo Javier Jurgen · Sebastian Chinchay Collachagua",
    ]
    equipo_p.runs[0].text = lineas_equipo[0]
    for linea in lineas_equipo[1:]:
        equipo_p.runs[0].add_break()
        equipo_p.add_run(linea)
    fecha = P(18)
    for r in list(fecha.runs):
        fecha._p.remove(r._r)
    fecha.add_run("Lima – Perú").add_break()
    fecha.add_run("Noviembre 2026")


def volcar(doc, eventos, pies):
    cuerpo = list(doc.element.body)
    primero = next(i for i, e in enumerate(cuerpo) if e.tag == qn("w:p") and Paragraph(e, doc._body).style.name == "Heading 1")
    biblio_titulo = next(i for i, e in enumerate(cuerpo) if e.tag == qn("w:p") and Paragraph(e, doc._body).text.strip() == "BIBLIOGRAFÍA")
    prototipo = deepcopy(doc.tables[1]._tbl)
    for e in cuerpo[primero:biblio_titulo - 1]:                 # el cuerpo de ejemplo (queda el párrafo vacío antes de la bibliografía)
        e.getparent().remove(e)
    ancla = list(doc.element.body)[primero]                     # el párrafo vacío que quedó: se inserta antes de él
    for ev in eventos:
        tipo = ev[0]
        if tipo in ("h1", "h2", "h3"):
            nuevo_parrafo(doc, ancla, "Heading " + tipo[1], ev[1])
        elif tipo == "p":
            nuevo_parrafo(doc, ancla, "Texto del Plan", ev[1])
        elif tipo == "bul":
            nuevo_parrafo(doc, ancla, "List Bullet", ev[1], negrita_inicial=True)
        elif tipo == "tabla":
            nueva_tabla(doc, ancla, prototipo, ev[1], ev[2])
        elif tipo == "fig":
            _, png, pie, ancho = ev
            for prefijo, nuevo in pies.items():
                if pie.startswith(prefijo):
                    pie = nuevo
            p = nuevo_parrafo(doc, ancla, "Texto del Plan")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            p.add_run().add_picture(str(comun.FIGURAS / png), width=Cm(min(ancho * ANCHO_TEXTO_CM / comun.ANCHO_UTIL_CM, ANCHO_TEXTO_CM)))
            nuevo_parrafo(doc, ancla, "Caption", pie)
        elif tipo == "biblio":
            refs = ev[1]
    # bibliografía: se reemplaza el ejemplo de la plantilla
    cuerpo = list(doc.element.body)
    i_biblio = next(i for i, e in enumerate(cuerpo) if e.tag == qn("w:p") and Paragraph(e, doc._body).style.name == "Bibliography")
    ejemplo = cuerpo[i_biblio]
    for r in refs:
        m = re.match(r"^(\[\d+\])\s+(.*)$", r)
        p = nuevo_parrafo(doc, ejemplo, "Bibliography")
        p.add_run(f"{m.group(1)}\t{m.group(2)}")
    ejemplo.getparent().remove(ejemplo)
    # anexos: la plantilla trae el título vacío; se deja una referencia a la fuente de los datos
    cuerpo = list(doc.element.body)
    i_anexos = next(i for i, e in enumerate(cuerpo) if e.tag == qn("w:p") and Paragraph(e, doc._body).text.strip() == "ANEXOS")
    vacio = cuerpo[i_anexos + 1]
    nota = Paragraph(vacio, doc._body)
    estilo_parrafo(nota, "Texto del Plan")
    nota.add_run("Anexo A. Datos de origen: repositorio cologistic-nettop-datos (diseño) y cologistic-infra (especificación generada, reglas de pfSense y visor topologia.html), "
                 "de donde salen las tablas y figuras de este informe.")


def actualizar_indice(doc):
    """Pide a Word actualizar los campos al abrir (el índice es un campo)."""
    settings = doc.settings.element
    if settings.find(qn("w:updateFields")) is None:
        e = OxmlElement("w:updateFields")
        e.set(qn("w:val"), "true")
        settings.append(e)


def generar(clave, modulo_nombre, salida_nombre):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    modulo = importlib.import_module(modulo_nombre)
    if hasattr(modulo, "contenido"):                    # entregables escritos directamente con Redactor
        r = modulo.contenido()
        eventos, pies = r.eventos, r.pies
    else:                                               # entregables S1: se captura lo que escribirían sobre la plantilla de la rúbrica
        eventos, pies = capturar(modulo)
    doc = docx.Document(str(plantilla_corregida()))
    portada(doc, clave)
    volcar(doc, eventos, pies)
    actualizar_indice(doc)
    SALIDA.mkdir(exist_ok=True)
    ruta = SALIDA / salida_nombre
    doc.save(str(ruta))
    print(f"Guardado: {ruta}  ({sum(e[0] == 'tabla' for e in eventos)} tablas, {sum(e[0] == 'fig' for e in eventos)} figuras)")


if __name__ == "__main__":
    generar("s1_e1", "generar_s1_e1", "s1_e1_analisis_y_diseno_de_red.docx")
    generar("s1_e2", "generar_s1_e2", "s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido.docx")
    for clave, nombre in (("s2_e1", "s2_e1_planificacion_e_implementacion_del_sgsi"),
                          ("s2_e2", "s2_e2_implementacion_testing_y_monitoreo_de_red"),
                          ("s2_e3", "s2_e3_implementacion_gestion_y_control_de_centro_de_datos")):
        if (Path(__file__).resolve().parent / f"generar_{clave}.py").exists():
            generar(clave, f"generar_{clave}", nombre + ".docx")
