"""
redactor.py — Una forma simple de escribir el contenido de un informe (títulos, párrafos, viñetas, tablas, figuras, bibliografía)
que luego generar_upeu.py vuelca en la plantilla UPeU con sus estilos. Los títulos no llevan número: la plantilla los numera sola.
"""


class Redactor:
    def __init__(self):
        self.eventos = []
        self.pies = {}

    def h1(self, texto):
        self.eventos.append(("h1", texto))

    def h2(self, texto):
        self.eventos.append(("h2", texto))

    def h3(self, texto):
        self.eventos.append(("h3", texto))

    def p(self, texto):
        self.eventos.append(("p", texto))

    def bullets(self, *items):
        for t in items:
            self.eventos.append(("bul", t))

    def tabla(self, encabezado, filas):
        self.eventos.append(("tabla", list(encabezado), [list(map(str, f)) for f in filas]))

    def fig(self, png, pie, ancho_cm=17.0):
        self.eventos.append(("fig", png, pie, ancho_cm))

    def biblio(self, *refs):
        self.eventos.append(("biblio", list(refs)))
