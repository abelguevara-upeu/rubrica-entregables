#!/usr/bin/env python3
"""
xlsx_s2.py — Los archivos Excel que piden las rúbricas del Semestre 2, con los mismos datos del informe:
  S2_E1: inventario de activos, matriz de riesgos (con fórmulas de nivel) y Declaración de Aplicabilidad
  S2_E2: plan y resultados de pruebas de red
  S2_E3: registro de prueba de recuperación

    python3 scripts/xlsx_s2.py            # genera en entregables_upeu/xlsx/
"""
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

import pruebas_datos as pd
import sgsi_datos as sg

SALIDA = Path(__file__).resolve().parents[1] / "entregables_upeu" / "xlsx"
AZUL = "133862"
BORDE = Border(*(Side(style="thin", color="B7C3D0"),) * 4)


def libro(nombre, hoja, encabezado, filas, anchos, titulo=None):
    wb = Workbook()
    ws = wb.active
    ws.title = hoja
    fila0 = 1
    if titulo:
        ws.cell(1, 1, titulo).font = Font(bold=True, size=13, color=AZUL)
        fila0 = 3
    for j, h in enumerate(encabezado, 1):
        c = ws.cell(fila0, j, h)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=AZUL)
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BORDE
    for i, f in enumerate(filas, fila0 + 1):
        for j, v in enumerate(f, 1):
            c = ws.cell(i, j, v)
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = BORDE
    for j, a in enumerate(anchos, 1):
        ws.column_dimensions[get_column_letter(j)].width = a
    ws.freeze_panes = ws.cell(fila0 + 1, 1)
    ws.auto_filter.ref = f"A{fila0}:{get_column_letter(len(encabezado))}{fila0 + len(filas)}"
    return wb, ws, fila0


def colorear_estado(ws, col, f1, f2, reglas):
    rango = f"{col}{f1}:{col}{f2}"
    for texto, color in reglas.items():
        ws.conditional_formatting.add(rango, CellIsRule(operator="equal", formula=[f'"{texto}"'], fill=PatternFill("solid", bgColor=color, fgColor=color)))


def inventario():
    filas = [list(a) for a in sg.inventario()]
    wb, ws, f0 = libro("inventario", "Inventario de activos",
                       ["ID", "Activo", "Tipo", "Propietario", "Ubicación", "Criticidad", "C (1-3)", "I (1-3)", "D (1-3)", "Clasificación"],
                       filas, [7, 58, 18, 30, 34, 12, 9, 9, 9, 15], "Inventario de activos — Co-Logistic S.A.C. (ISO/IEC 27001:2022, A.5.9 y A.5.12)")
    ws.cell(f0 + len(filas) + 2, 1, "Escala C-I-D: 1 baja, 2 media, 3 alta. Criticidad: la del mayor valor. Clasificación según la confidencialidad: 3 Confidencial, 2 Interna, 1 Pública.")
    wb.save(SALIDA / "S2_E1_inventario_de_activos.xlsx")


def riesgos():
    enc = ["ID", "Activo", "Amenaza", "Vulnerabilidad", "Impacto (1-5)", "Probabilidad (1-5)", "Valor", "Nivel", "Tratamiento", "Controles (Anexo A)",
           "Impacto residual", "Probabilidad residual", "Valor residual", "Nivel residual"]
    filas = []
    for x in sg.riesgos():
        filas.append([x[0], x[1], x[2], x[3], x[4], x[5], None, None, x[8], x[9], x[10], x[11], None, None])
    wb, ws, f0 = libro("riesgos", "Matriz de riesgos", enc, filas, [6, 24, 32, 38, 10, 12, 8, 10, 12, 24, 10, 12, 9, 10],
                       "Matriz de evaluación y tratamiento de riesgos (ISO/IEC 27005)")
    nivel = lambda c: f'=IF({c}>=20,"Crítico",IF({c}>=13,"Alto",IF({c}>=7,"Medio","Bajo")))'
    for i in range(f0 + 1, f0 + 1 + len(filas)):
        ws[f"G{i}"] = f"=E{i}*F{i}"
        ws[f"H{i}"] = nivel(f"G{i}")
        ws[f"M{i}"] = f"=K{i}*L{i}"
        ws[f"N{i}"] = nivel(f"M{i}")
    f1, f2 = f0 + 1, f0 + len(filas)
    colores = {"Crítico": "F4B6B6", "Alto": "F8D7A8", "Medio": "FFF2B3", "Bajo": "CDEBC5"}
    for col in ("H", "N"):
        colorear_estado(ws, col, f1, f2, colores)
    n = f0 + len(filas) + 2
    notas = ["Valor = impacto × probabilidad. Nivel: Bajo 1 a 6, Medio 7 a 12, Alto 13 a 19, Crítico desde 20 (las celdas de valor y nivel son fórmulas).",
             "Criterio de aceptación: la dirección acepta los riesgos Bajos; los Medio, Alto y Crítico requieren plan de tratamiento y seguimiento.",
             "Impacto y probabilidad residuales: los esperados después de aplicar los controles indicados."]
    for k, t in enumerate(notas):
        ws.cell(n + k, 1, t)
    wb.save(SALIDA / "S2_E1_matriz_de_riesgos.xlsx")


def soa():
    filas = [[c, nombre, "No" if e == "No aplica" else "Sí", e, j] for c, nombre, e, j in sg.soa()]
    wb, ws, f0 = libro("soa", "SoA", ["Control", "Nombre", "Aplica", "Estado", "Justificación y evidencia"], filas, [9, 52, 8, 14, 90],
                       "Declaración de Aplicabilidad — ISO/IEC 27001:2022, Anexo A (93 controles)")
    f1, f2 = f0 + 1, f0 + len(filas)
    colorear_estado(ws, "D", f1, f2, {"Implementado": "CDEBC5", "Parcial": "FFF2B3", "Planificado": "F8D7A8", "No aplica": "E3E3E3"})
    dv = DataValidation(type="list", formula1='"Implementado,Parcial,Planificado,No aplica"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"D{f1}:D{f2}")
    r = f2 + 2
    ws.cell(r, 2, "Resumen por estado").font = Font(bold=True)
    for k, e in enumerate(["Implementado", "Parcial", "Planificado", "No aplica"], 1):
        ws.cell(r + k, 2, e)
        ws.cell(r + k, 3, f'=COUNTIF(D{f1}:D{f2},B{r + k})')
    wb.save(SALIDA / "S2_E1_declaracion_de_aplicabilidad.xlsx")


def plan_pruebas():
    filas = [[t[0], t[5], t[1], t[2], t[3], t[4], "", "", "Pendiente"] for t in pd.PRUEBAS_RED]
    wb, ws, f0 = libro("pruebas", "Plan de pruebas",
                       ["Caso", "Tipo", "Objetivo", "Precondición", "Pasos", "Resultado esperado", "Resultado obtenido", "Evidencia (archivo o captura)", "Estado"],
                       filas, [7, 20, 38, 34, 46, 40, 34, 28, 12], "Plan y resultados de pruebas de red — S2_E2")
    f1, f2 = f0 + 1, f0 + len(filas)
    dv = DataValidation(type="list", formula1='"Pendiente,Aprobada,Fallida,Bloqueada"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"I{f1}:I{f2}")
    colorear_estado(ws, "I", f1, f2, {"Pendiente": "E3E3E3", "Aprobada": "CDEBC5", "Fallida": "F4B6B6", "Bloqueada": "FFF2B3"})
    r = f2 + 2
    ws.cell(r, 3, "Resumen").font = Font(bold=True)
    for k, e in enumerate(["Pendiente", "Aprobada", "Fallida", "Bloqueada"], 1):
        ws.cell(r + k, 3, e)
        ws.cell(r + k, 4, f'=COUNTIF(I{f1}:I{f2},C{r + k})')
    ws.cell(r + 6, 3, "Resultado obtenido y evidencia: se completan al ejecutar cada caso en el laboratorio. No se registran resultados sin evidencia.")
    wb.save(SALIDA / "S2_E2_plan_y_resultados_de_pruebas.xlsx")


def recuperacion():
    destino = SALIDA / "S2_E3_registro_de_prueba_de_recuperacion.xlsx"
    if destino.exists():
        import openpyxl as _ox
        wb_prev = _ox.load_workbook(destino)
        ws_prev = wb_prev.active
        if any(row[7] not in (None, "Pendiente", "Estado") for row in ws_prev.iter_rows(min_row=4, max_row=8, values_only=True)):
            print("Conservando registro existente con evidencias reales en", destino.name)
            return
    filas = [[s, rto, rpo, "", "", "", "", "Pendiente"] for s, rto, rpo in pd.RECUPERACION]
    wb, ws, f0 = libro("rec", "Registro de recuperación",
                       ["Servicio", "RTO objetivo", "RPO objetivo", "Fecha y hora de la falla", "Servicio restablecido a las", "RTO obtenido", "RPO obtenido", "Estado"],
                       filas, [44, 16, 16, 22, 22, 16, 16, 14], "Registro de prueba de recuperación — S2_E3")
    f1, f2 = f0 + 1, f0 + len(filas)
    dv = DataValidation(type="list", formula1='"Pendiente,Cumple el objetivo,No cumple"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"H{f1}:H{f2}")
    r = f2 + 2
    ws.cell(r, 1, "Procedimiento").font = Font(bold=True)
    for k, p in enumerate(pd.PASOS_RECUPERACION, 1):
        ws.cell(r + k, 1, f"{k}. {p}")
    ws.cell(r + len(pd.PASOS_RECUPERACION) + 2, 1, "Evidencia: adjuntar la salida de los comandos y capturas, sin contraseñas. RTO y RPO obtenidos se completan al ejecutar el ejercicio.")
    wb.save(destino)


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    for f in (inventario, riesgos, soa, plan_pruebas, recuperacion):
        f()
    print("Guardado en", SALIDA, [p.name for p in sorted(SALIDA.glob("*.xlsx"))])
