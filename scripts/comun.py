"""
comun.py — Lo que comparten los generadores de S1_E1 y S1_E2: llenar tablas y secciones de la plantilla sin tocar
su formato (se usan solo los estilos del documento) y reemplazar los cuadros de diagrama por las figuras reales.
"""
from copy import deepcopy
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from docx.text.paragraph import Paragraph

RAIZ = Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "figuras"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
ANCHO_UTIL_CM = 17.0          # A4 con márgenes de 2 cm


def llenar_tabla(tbl, filas, encabezado=None):
    """Reemplaza las filas de datos (no la de encabezado) conservando bordes y márgenes de celda de la plantilla."""
    ref = tbl.rows[1] if len(tbl.rows) > 1 else tbl.rows[0]
    ref_pr = [c._tc.get_or_add_tcPr() for c in ref.cells]
    if encabezado:
        for celda, texto in zip(tbl.rows[0].cells, encabezado):
            celda.text = texto
    for r in list(tbl.rows[1:]):
        tbl._tbl.remove(r._tr)
    for valores in filas:
        tr = tbl.add_row()
        for i, v in enumerate(valores):
            celda = tr.cells[i]
            nuevo = celda._tc.get_or_add_tcPr()
            for etiqueta in ("tcBorders", "tcMar"):
                hallado = ref_pr[i].find(W + etiqueta)
                if hallado is not None:
                    nuevo.append(deepcopy(hallado))
            celda.text = str(v)
            if celda.paragraphs:
                celda.paragraphs[0].style = "Normal"


def reemplazar_seccion(doc, encabezado, items):
    _viñeta_de_la_plantilla(doc)
    """Quita los párrafos de guía bajo `encabezado` (hasta el siguiente título, tabla o «Figura») y pone `items`: [(estilo, texto)]."""
    objetivo = next((p for p in doc.paragraphs if p.text.strip() == encabezado.strip()), None)
    if objetivo is None:
        raise SystemExit(f"No encuentro el título «{encabezado}» en la plantilla")
    viejos, actual = [], objetivo._p.getnext()
    while actual is not None:
        etiqueta = actual.tag.split("}")[-1]
        if etiqueta == "p":
            p = Paragraph(actual, doc)
            if p.style.name.startswith("Heading") or p.text.strip().startswith("Figura "):
                break
            viejos.append(actual)
        elif etiqueta == "tbl":
            break
        actual = actual.getnext()
    viñeta = _viñeta_de_la_plantilla(doc)
    cursor = objetivo._p
    for estilo, texto in items:
        nuevo = doc._body._element.makeelement(W + "p")
        cursor.addnext(nuevo)
        p = Paragraph(nuevo, doc)
        p.style = estilo
        p.text = texto
        if estilo == "List Paragraph" and viñeta is not None:
            p._p.get_or_add_pPr().append(deepcopy(viñeta))      # la misma viñeta que usa la plantilla
        cursor = nuevo
    for e in viejos:
        e.getparent().remove(e)


def _viñeta_de_la_plantilla(doc):
    """El numPr (viñeta) del primer párrafo de lista de la plantilla; hay que tomarlo antes de que se reemplacen sus guías."""
    if not hasattr(doc, "_viñeta"):
        doc._viñeta = next((p._p.pPr.numPr for p in doc.paragraphs if p.style.name == "List Paragraph" and p._p.pPr is not None and p._p.pPr.numPr is not None), None)
        if doc._viñeta is not None:
            doc._viñeta = deepcopy(doc._viñeta)
    return doc._viñeta


def poner_figura(doc, tabla, png, ancho_cm=ANCHO_UTIL_CM):
    """Reemplaza un cuadro de diagrama (tabla 1x1) por la imagen `png` centrada. El pie «Figura x.y — …» que le sigue se conserva."""
    ruta = FIGURAS / png
    if not ruta.exists():
        raise SystemExit(f"Falta la figura {ruta}: corre scripts/capturar_figuras.js")
    nuevo = doc._body._element.makeelement(W + "p")
    tabla._tbl.addprevious(nuevo)
    p = Paragraph(nuevo, doc)
    p.style = "Normal"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ruta), width=Cm(ancho_cm))
    tabla._tbl.getparent().remove(tabla._tbl)


def cambiar_texto_que_contiene(doc, fragmento, nuevo):
    """Reemplaza el texto del primer párrafo (de las primeras líneas) que contenga `fragmento`."""
    for p in doc.paragraphs[:14]:
        if fragmento in p.text:
            p.text = nuevo
            return


def franja_en_dos_filas(origen, destino, primera_fila=3, margen=40):
    """Parte una imagen ancha (una fila de cajas) en dos filas apiladas, cortando por un hueco entre cajas, para que quepa legible en la página.
    `primera_fila`: cuántas cajas van arriba."""
    from PIL import Image
    im = Image.open(FIGURAS / origen).convert("RGB")
    w, h = im.size
    px = im.load()
    fondo = px[3, 3]
    vacias = []
    for x in range(w):
        ocupada = any(sum(abs(a - b) for a, b in zip(px[x, y], fondo)) > 60 for y in range(0, h, 4))
        vacias.append(not ocupada)
    huecos, inicio = [], None                         # tramos de columnas sin nada: separan las cajas
    for x, v in enumerate(vacias + [False]):
        if v and inicio is None:
            inicio = x
        elif not v and inicio is not None:
            if x - inicio > 6:
                huecos.append((inicio + x) // 2)
            inicio = None
    huecos = [x for x in huecos if 0.05 * w < x < 0.95 * w]       # los márgenes de los bordes no separan cajas
    corte = huecos[primera_fila - 1] if len(huecos) >= primera_fila else w // 2
    arriba, abajo = im.crop((0, 0, corte, h)), im.crop((corte, 0, w, h))
    ancho = max(arriba.width, abajo.width)
    lienzo = Image.new("RGB", (ancho, 2 * h + margen), fondo)
    lienzo.paste(arriba, ((ancho - arriba.width) // 2, 0))
    lienzo.paste(abajo, ((ancho - abajo.width) // 2, h + margen))
    lienzo.save(FIGURAS / destino)
    return destino


def cambiar_pie_de_figura(doc, prefijo, nuevo):
    """Cambia el texto del pie «Figura x.y — …» conservando su formato (la plantilla trae pies de la versión ESXi/AWS)."""
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefijo):
            runs = p.runs
            runs[0].text = nuevo
            for r in runs[1:]:
                r._r.getparent().remove(r._r)
            return
    raise SystemExit(f"No encuentro el pie «{prefijo}»")


def mitad_superior(origen, destino, fraccion=0.5):
    """La parte de arriba de una figura (la de zonas es la mitad superior de la vista de red: nube, router, WAN, firewalls y las primeras zonas)."""
    from PIL import Image
    im = Image.open(FIGURAS / origen)
    im.crop((0, 0, im.width, int(im.height * fraccion))).save(FIGURAS / destino)
    return destino
