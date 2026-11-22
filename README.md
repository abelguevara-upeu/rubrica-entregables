# Entregables UPeU y SGSI — Co-Logistic S.A.C.

Repositorio de generación reproducible de los **5 entregables UPeU** (DOCX + PDF) y las **5 matrices Excel (XLSX)** del proyecto integrador de Infraestructura Híbrida y SGSI ISO/IEC 27001:2022 de **Co-Logistic S.A.C.**.

> **Contexto técnico completo de la infraestructura viva:** ver `../cologistic-infra/CONTEXTO-PROYECTO.md`.

---

## 1. Integrantes del Equipo (Portada de los 5 Entregables)

Definidos de forma centralizada en `scripts/generar_upeu.py` (`portada()`):

- Jhack Ernesto Quispe Mamani · Abel Is-boset Guevara Huasco · David Edison Guerra Ordoñez
- Alvaro Kenji Cuti Magaño · Javier Kevin Tello Rivas · Richard Josef Yaqui Inocente
- Daniel Hernan Calderon Camacho · Joshua Alfonzo Javier Jurgen · Sebastian Chinchay Collachagua
- Fernando Asin Gomez

Ciclo: X (aparece en la portada como «EQUIPO · X CICLO»).

---

## 2. Mapa de Entregables (`entregables_upeu/`)

| Entregable | Documento DOCX / PDF | Matrices XLSX Asociadas (`entregables_upeu/xlsx/`) | Script Fuente |
| :--- | :--- | :--- | :--- |
| **S1 · E1** | `s1_e1_analisis_y_diseno_de_red.{docx,pdf}` | — | `scripts/generar_s1_e1.py` |
| **S1 · E2** | `s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido.{docx,pdf}` | — | `scripts/generar_s1_e2.py` |
| **S2 · E1 (SGSI)** | `s2_e1_planificacion_e_implementacion_del_sgsi.{docx,pdf}` | `S2_E1_inventario_de_activos.xlsx`, `S2_E1_matriz_de_riesgos.xlsx`, `S2_E1_declaracion_de_aplicabilidad.xlsx` | `scripts/generar_s2_e1.py` + `scripts/sgsi_datos.py` |
| **S2 · E2 (Red)** | `s2_e2_implementacion_testing_y_monitoreo_de_red.{docx,pdf}` | `S2_E2_plan_y_resultados_de_pruebas.xlsx` | `scripts/generar_s2_e2.py` + `scripts/pruebas_datos.py` |
| **S2 · E3 (Datacenter)** | `s2_e3_implementacion_gestion_y_control_de_centro_de_datos.{docx,pdf}` | `S2_E3_registro_de_prueba_de_recuperacion.xlsx` | `scripts/generar_s2_e3.py` + `scripts/pruebas_datos.py` |

---

## 3. Cómo Regenerar Todo sin Desincronizar

Nunca editar los `.docx` a mano sin actualizar primero el script correspondiente en `scripts/`:

```bash
# 1. Regenerar los 5 DOCX con portada UPeU y estilos unificados:
python3 scripts/generar_upeu.py

# 2. Regenerar las 5 matrices XLSX:
python3 scripts/xlsx_s2.py

# 3. Exportar a PDF actualizando los índices mediante Microsoft Word (macOS):
for f in entregables_upeu/*.docx; do
  sh scripts/exportar_pdf.sh "$(pwd)/$f"
done
```

---

## 4. Regla de Coherencia y Seguridad

- **Cero secretos reales** en textos, capturas, tablas o scripts.
- Todo dato de red, VMs y nube se lee automáticamente desde `../cologistic-infra/especificacion/` vía `scripts/datos.py`.
- Estado de hallazgos al **19/11/2026:** **7/9 cerrados** (`H01, H02, H03, H05, H06, H07, H08`; 0 no conformidades mayores abiertas), 1 menor abierta (`H04`, step-ca en WAF01) y 1 riesgo aceptado (`H09`, SSH C1000 en VLAN 70).
