"""
evidencias.py — Las capturas de evidencia web (figuras/evidencias/) que van en el Anexo B de los entregables S2.

La fuente es figuras/evidencias/PLAN_CAPTURAS.md: cada fila marcada [x] cuyo PNG existe entra con el pie de figura del plan.
El nombre del archivo dice a qué entregable y sección pertenece: <entregable>_sec<NN>_<orden>_<slug>.png.
"""
import re
from pathlib import Path

import comun

CARPETA = comun.FIGURAS / "evidencias"
PLAN = CARPETA / "PLAN_CAPTURAS.md"

_FILA = re.compile(r"^\|\s*`\[(?P<estado>[ x])\]`\s*\|\s*`(?P<archivo>[^`]+\.png)`\s*\|.*\|\s*(?P<pie>[^|]+?)\s*\|\s*$")
_NOMBRE = re.compile(r"^(?P<clave>s\d_e\d)_sec(?P<sec>\d+)_(?P<orden>\d+)_")


def _limpiar(texto):
    """El pie viene en Markdown: sin comillas invertidas ni negritas."""
    return re.sub(r"[`*]", "", texto).strip()


def capturas(clave, plan=PLAN, carpeta=CARPETA):
    """[(seccion, orden, ruta_relativa_a_figuras, pie)] del entregable `clave` (p. ej. "s2_e1"), en orden de sección."""
    salida = []
    for linea in Path(plan).read_text(encoding="utf-8").splitlines():
        m = _FILA.match(linea)
        if not m or m["estado"] != "x":
            continue
        n = _NOMBRE.match(m["archivo"])
        if not n or n["clave"] != clave or not (Path(carpeta) / m["archivo"]).exists():
            continue
        salida.append((int(n["sec"]), int(n["orden"]), f"evidencias/{m['archivo']}", _limpiar(m["pie"])))
    return sorted(salida)
