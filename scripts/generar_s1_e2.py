#!/usr/bin/env python3
"""
generar_s1_e2.py
Genera el Entregable 2 de Semestre 1 (S1_E2): Análisis y Diseño de Centro de Datos Híbrido.
Cumple con la rúbrica oficial de Proyecto Integrador UPeU / Co-Logistic S.A.C.
Sin overrides manuales de fuente/color/tamaño: usa estrictamente los estilos del documento.
"""

import sys
import docx
from copy import deepcopy

TEMPLATE_PATH = "/Users/abelguevarah/Desktop/perfil-egreso/rubrica-entregables/templates/s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido_crmjbimadn.docx"
OUTPUT_PATH = "/Users/abelguevarah/Desktop/perfil-egreso/rubrica-entregables/entregables/s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido.docx"

def populate_table(tbl, rows_data):
    """Reemplaza filas de datos de una tabla manteniendo el formato y bordes de celda del template."""
    ref_row = tbl.rows[1] if len(tbl.rows) > 1 else tbl.rows[0]
    ref_tcPr_list = [c._tc.get_or_add_tcPr() for c in ref_row.cells]
    
    # Eliminar filas existentes de ejemplo
    for r in list(tbl.rows[1:]):
        tbl._tbl.remove(r._tr)
        
    # Añadir nuevas filas
    for row_values in rows_data:
        new_tr = tbl.add_row()
        for col_idx, val in enumerate(row_values):
            cell = new_tr.cells[col_idx]
            ref_tcPr = ref_tcPr_list[col_idx]
            borders = ref_tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcBorders')
            mar = ref_tcPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tcMar')
            new_tcPr = cell._tc.get_or_add_tcPr()
            if borders is not None:
                new_tcPr.append(deepcopy(borders))
            if mar is not None:
                new_tcPr.append(deepcopy(mar))
            cell.text = str(val)
            if cell.paragraphs:
                cell.paragraphs[0].style = 'Normal'

def replace_section_content(doc, heading_text, new_items):
    """
    Localiza heading_text en el documento, elimina los párrafos de guía que le siguen
    (hasta el siguiente heading o tabla) e inserta los nuevos párrafos usando los estilos definidos.
    new_items es una lista de tuplas: (style_name, text)
    """
    target_h = None
    for p in doc.paragraphs:
        if p.text.strip() == heading_text.strip():
            target_h = p
            break
            
    if target_h is None:
        print(f"[WARN] Heading no encontrado: '{heading_text}'")
        return

    # Identificar elementos antiguos a remover entre este heading y el próximo heading o tabla
    to_remove = []
    curr = target_h._p.getnext()
    while curr is not None:
        tag = curr.tag.split('}')[-1]
        if tag == 'p':
            p_obj = docx.text.paragraph.Paragraph(curr, doc)
            if p_obj.style.name.startswith('Heading'):
                break
            if p_obj.text.strip().startswith('Figura '):
                break
            to_remove.append(curr)
        elif tag == 'tbl':
            break
        curr = curr.getnext()

    # Insertar nuevos párrafos en orden
    cursor = target_h._p
    for style, txt in new_items:
        new_elm = doc._body._element.makeelement('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
        cursor.addnext(new_elm)
        p = docx.text.paragraph.Paragraph(new_elm, doc)
        p.style = style
        p.text = txt
        cursor = new_elm

    # Remover viejos
    for elm in to_remove:
        elm.getparent().remove(elm)

def update_diagram_box(tbl, diagram_text):
    """Actualiza la caja de diagrama 1x1 preservando bordes y asignando estilo Normal."""
    cell = tbl.rows[0].cells[0]
    cell.text = diagram_text.strip()
    if cell.paragraphs:
        cell.paragraphs[0].style = 'Normal'

def main():
    print("Cargando plantilla S1_E2...")
    doc = docx.Document(TEMPLATE_PATH)

    # 1. Portada y Metadatos
    print("Actualizando portada y metadatos...")
    for p in doc.paragraphs[:12]:
        txt = p.text.strip()
        if "On-Premise (VMware ESXi) + AWS" in txt:
            p.text = "On-Premise (Proxmox VE KVM / VMware ESXi) + Cloud (Google Cloud Platform / AWS)"
        elif "Preparado por:" in txt:
            p.text = "Preparado por: Abel Guevara Huillca"
        elif "Docente / curso:" in txt:
            p.text = "Docente / curso: Proyecto Integrador · Seguridad de la Información / Habilidades Directivas"
        elif "2026" in txt:
            p.text = "Organización: Co-Logistic S.A.C.  |  Juliaca, Perú  |  Año: 2026"

    # 2. Resumen Ejecutivo
    print("Redactando Sección 1: Resumen ejecutivo...")
    sec1_content = [
        ("Normal", "El presente informe establece el diseño arquitectónico formal del centro de datos híbrido para Co-Logistic S.A.C., operador logístico 3PL líder en la región sur del Perú con sede central en la ciudad de Juliaca. El proyecto responde a la necesidad crítica de dotar a la organización de una infraestructura de cómputo, virtualización y almacenamiento altamente disponible, resiliente y escalable, superando las limitaciones de aislamiento físico previo y estableciendo una estrategia de recuperación ante desastres (Disaster Recovery Plan - DRP) costo-eficiente, en estricto cumplimiento con la norma ISO/IEC 27001:2022."),
        ("Normal", "Dimensiones cardinales del diseño arquitectónico formulado:"),
        ("List Paragraph", "Organización y escenario: Co-Logistic S.A.C., centro de distribución de 12,000 m² en Juliaca, con 45 usuarios administrativos/operativos y más de 60 terminales móviles industriales de captura de datos (pistolas RF Zebra y tabletas de picking) que operan en turnos continuos 24/7."),
        ("List Paragraph", "Problema de infraestructura resuelto: Servidores físicos dispersos sin redundancia (SPOF), datastores locales no replicados con riesgo inminente de pérdida catastrófica de información transaccional, y carencia de un entorno alterno de contingencia ante eventos disruptivos físicos (sismos, incendios o cortes prolongados de energía)."),
        ("List Paragraph", "Tecnología On-Premise seleccionada: Clúster de virtualización de 5 servidores físicos Dell Precision / PowerEdge gobernados por Proxmox VE 8.x Enterprise KVM (clúster PVE-COLOGISTIC: HV-MAIN, HV1, HV2, HV3 y HV4), alojados en el Gabinete Rack R1 (24U). Esta solución ofrece paridad técnica 1:1 con la arquitectura de VMware ESXi (conmutación virtual basada en bridges/vSwitches con 802.1Q trunking, aislamiento de memoria y CPU por hardware), con la ventaja determinante de permitir aprovisionamiento declarativo automatizado como Infraestructura como Código (IaC con Cloud-Init y Terraform) y cero fricción por licenciamiento privativo."),
        ("List Paragraph", "Tecnología Cloud seleccionada y justificación: Google Cloud Platform (GCP) en la región southamerica-west1 (Santiago de Chile), con arquitectura homóloga y portable a Amazon Web Services (AWS sa-east-1). Se justifica técnicamente por la existencia de enlaces de fibra óptica submarina por el Pacífico que proporcionan una latencia ultrabaja de ~38 ms hacia el Perú (en contraste con >110 ms de regiones en Norteamérica como us-east-1 Virginia), viabilizando la sincronización continua de respaldos y el cumplimiento estricto de los SLAs de recuperación."),
        ("List Paragraph", "Dimensionamiento de cómputo y almacenamiento: Capacidad física local consolidada de 40 núcleos físicos (80 hilos vCPU), 188 GB de memoria RAM y 2.4 TB de almacenamiento ZFS de alta velocidad. Sobre este sustrato se distribuyen 22 máquinas virtuales Linux Debian 12 (optimizadas para microservicios y bases de datos) y 2 estaciones administrativas Windows 11 (PAW), requiriendo 41 vCPUs (tasa de sobreasignación segura de 1.02:1), 63 GB de RAM (33.5 % de ocupación física) y 685 GB de disco (28.5 % del almacenamiento local), garantizando más de un 60 % de margen de crecimiento libre."),
        ("List Paragraph", "Resultados proyectados y hoja de ruta: Alta disponibilidad local por servicio (regla D03: ningún par redundante comparte el mismo hipervisor físico), respaldo inmutable offsite 3-2-1 mediante Bareos y Google Cloud Storage, objetivo de punto de recuperación (RPO) < 15 min y tiempo de recuperación (RTO) < 30 min ante contingencia. En el Semestre 2 (Entregable S2_E3) se automatizará el aprovisionamiento de las VMs vía Terraform y se ejecutará el simulacro de contingencia DR.")
    ]
    replace_section_content(doc, "1. Resumen ejecutivo del diseño del centro de datos híbrido", sec1_content)

    # Diagrama 1.1: Topología ejecutiva del centro de datos
    diag_1_1 = """[ FIGURA 1.1: ARQUITECTURA EJECUTIVA DEL CENTRO DE DATOS HÍBRIDO ]
===================================================================================================
DATACENTER LOCAL JULIACA (ON-PREMISE)                    GOOGLE CLOUD PLATFORM (SANTIAGO DE CHILE)
Gabinete Rack R1 (24U) · Clúster PVE-COLOGISTIC          VPC-COLOGISTIC (10.20.0.0/24) · Región: southamerica-west1
+-------------------------------------------------+     +-------------------------------------------------+
| RED TRONCAL & PERÍMETRO                         |     | NUBE DE CONTINGENCIA & RESPALDO OFFSITE         |
| Cisco Catalyst Core (SW1/SW2) 10G EtherChannel  |     |                                                 |
| Firewalls pfSense HA (FW-MAIN / FW-BACKUP) CARP |     | Subred NUBE-BORDE (10.20.0.0/28)                |
+------------------------+------------------------+     | └── VM GCP-BORDE (Compute Engine e2-micro)      |
                         |                              |     ├── IP Pública: 34.176.121.24 (Nginx Web DRP|
+------------------------v------------------------+     |     └── IP Privada: 10.20.0.4 (Terminación VPN) |
| HIPERVISORES FÍSICOS (188 GB RAM · 2.4 TB ZFS)  |     |                                                 |
| ├── HV-MAIN: Respaldo, DB Standby, WMS Standby  |     | Subred NUBE-TUNEL (10.20.0.16/29)               |
| ├── HV1: DMZ (WAF, SFTP), PBX, PAW01            |     | └── Interfaz VPN wg0: 10.20.0.17                |
| ├── HV2: Core TI (FreeIPA, INFRA01), MGMT, Honey|     |                                                 |
| ├── HV3: Apps (WMS01), SIEM01, GLPI/Oxidized    |     | Subred NUBE-PRIVADA (10.20.0.32/28)             |
| └── HV4: Data (DB01 Master, DW01), OpenVAS, NVR |     | └── Cargas de contingencia internas aisladas    |
| Total: 22 VMs Linux Debian 12 + 2 VMs Win 11    |     |                                                 |
+------------------------+------------------------+     | Cloud Storage Buckets (Object Storage):         |
                         |                              | ├── cologistic-respaldos-cologistic-cloud       |
                         |                              | └── cologistic-tfstate-cologistic-cloud         |
                         +============== TÚNEL SEGURO ===================+
                                  WireGuard VPN (UDP 51820)
                                  Cifrado: ChaCha20-Poly1305 · Latencia: ~38 ms"""
    update_diagram_box(doc.tables[0], diag_1_1)

    # 3. Descripción de la Organización y Necesidades de Infraestructura
    print("Redactando Sección 2: Organización y necesidades de cómputo...")
    sec2_content = [
        ("Normal", "Co-Logistic S.A.C. opera como socio estratégico de la cadena de suministro para importantes empresas del sector retail, alimentos, farmacéutica y materiales de construcción en el sur del país. La continuidad de su centro de distribución en Juliaca depende de un ecosistema informático transaccional de alta frecuencia y disponibilidad ininterrumpida."),
        ("Normal", "Criterios técnicos para el reparto de cargas entre infraestructura on-premise y nube:"),
        ("List Paragraph", "Procesamiento Local On-Premise (90 % de la carga transaccional): Aloja el sistema WMS, el motor de base de datos PostgreSQL, la telefonía IP Asterisk y el sistema de videovigilancia NVR. El criterio rector es la minimización de latencia (RTT < 2 ms en red local) para garantizar la operatividad continua de las terminales de radiofrecuencia de almacén, preservando la autonomía operativa total de la sede ante eventuales cortes de los enlaces a Internet."),
        ("List Paragraph", "Servicios en Nube Pública (10 % de la carga + Contingencia DRP): Aloja la réplica inmutable offsite de respaldos en Google Cloud Storage, el estado IaC de Terraform y una máquina virtual de borde (GCP-BORDE) con portal web corporativo de contingencia y orquestador de recuperación de desastres. El criterio rector es la resiliencia geográfica (alta disponibilidad 99.99 % del proveedor), asegurando que un siniestro físico en Juliaca no comprometa los datos históricos ni la relación contractual con los clientes."),
        ("List Paragraph", "Importancia y clasificación de la información: Los datos de stock e inventarios (PostgreSQL en VLAN 32) se clasifican como 'Confidencial - Crítica'; los registros de trazabilidad y analítica de despachos (VLAN 33) como 'Interna - Alta'; las configuraciones y respaldos (VLAN 120) como 'Restringida - Crítica'; y el portal web y landing corporativa (DMZ / Nube) como 'Pública'."),
        ("List Paragraph", "Proyección de crecimiento: El dimensionamiento físico y virtual cubre holgadamente un horizonte de crecimiento de 5 años con una tasa anual estimada del 15 % en transacciones de almacén, manteniendo más de un 60 % de recursos físicos ociosos para amortiguar picos estacionales de demanda (campañas comerciales).")
    ]
    replace_section_content(doc, "2. Descripción de la organización y necesidades de infraestructura", sec2_content)

    # 4. Alcance del Diseño de Centro de Datos Híbrido
    print("Redactando Sección 3: Alcance del diseño de centro de datos...")
    sec3_1_content = [
        ("Normal", "El alcance del diseño comprende la infraestructura física y virtualizada del centro de datos local (Gabinete Rack R1 de 24U, servidores hipervisores Dell Precision / PowerEdge, conmutación virtual con Linux Bridges VLAN-aware, y almacenamiento ZFS), así como el entorno virtual en la nube (VPC en Google Cloud Platform, subredes, reglas de cortafuegos, instancias de cómputo y buckets de almacenamiento seguro), integrados formalmente mediante un túnel VPN sitio a sitio WireGuard para soportar los servicios corporativos de Co-Logistic S.A.C.")
    ]
    replace_section_content(doc, "3.1 Declaración de alcance", sec3_1_content)

    sec3_2_content = [
        ("Normal", "Los límites arquitectónicos se delimitan en los siguientes aspectos:"),
        ("List Paragraph", "Límites Físicos: Gabinete Rack R1 (24U) en la sala de servidores de la sede Juliaca, sistema de climatización de precisión, sistema de alimentación ininterrumpida (UPS APC Smart-UPS 3000VA con tarjeta SNMP), 5 servidores físicos para hipervisores, 2 servidores dedicados para firewalls pfSense, cabecera de almacenamiento y switches de conmutación."),
        ("List Paragraph", "Límites Tecnológicos: Hipervisor KVM / Proxmox VE (con equivalencia arquitectónica demostrada para VMware ESXi), bridges virtuales VLAN-aware con bonds LACP (802.3ad), máquinas virtuales Debian 12 aprovisionadas mediante Cloud-Init, VPC de Google Cloud (VPC-COLOGISTIC), Compute Engine, Cloud Storage, y reglas de firewall stateful."),
        ("List Paragraph", "Límites Organizacionales: La gestión, supervisión de capacidad y respuesta a incidentes de cómputo corresponde de forma exclusiva a la Jefatura de Infraestructura y Operaciones TI, rigiéndose por los roles definidos en el manual de seguridad de la información del SGSI.")
    ]
    replace_section_content(doc, "3.2 Límites", sec3_2_content)

    sec3_3_content = [
        ("Normal", "Se formalizan las siguientes exclusiones técnicas:"),
        ("List Paragraph", "Equipamiento informático de usuario final: Las estaciones portátiles y teléfonos celulares corporativos quedan excluidos del alcance de este diseño de centro de datos, considerándose puntos terminales de consumo."),
        ("List Paragraph", "Cargas de trabajo contenerizadas en Kubernetes: De acuerdo con la decisión de diseño D06, se excluye el uso de clústeres complejos de Kubernetes, estandarizando la contenerización ligera mediante Docker Compose sobre máquinas virtuales robustas Debian 12 para simplificar la operación y el DRP."),
        ("List Paragraph", "Infraestructura física del proveedor cloud: La administración física de los servidores, redes y centros de datos de Google Cloud en Santiago de Chile corresponde a dicho proveedor bajo el modelo de responsabilidad compartida de la nube.")
    ]
    replace_section_content(doc, "3.3 Exclusiones", sec3_3_content)

    # 5. Objetivos del Diseño de Centro de Datos
    print("Redactando Sección 4: Objetivos del diseño...")
    sec4_content = [
        ("Normal", "En conformidad con los requisitos del perfil de egreso y los controles de disponibilidad de ISO/IEC 27001:2022 (control A.8.14 Redundancia de instalaciones de procesamiento), se formulan los siguientes objetivos cuantitativos:")
    ]
    replace_section_content(doc, "4. Objetivos del diseño de centro de datos", sec4_content)

    table_objetivos_dc = [
        ["Dimensionar el clúster de hipervisores on-premise", "Capacidad asignada vs capacidad física del clúster", "< 65 % uso normal (N+1)", "Abel Guevara (Infraestructura)"],
        ["Diseñar entorno Cloud costo-eficiente para DRP", "Costo mensual proyectado con 99.9 % disponibilidad", "< $30 USD / mes", "Abel Guevara (Cloud)"],
        ["Garantizar aislamiento estricto en virtualización", "Separación de interfaces virtuales y bridges por VLAN", "100 % VMs asignadas a VLAN", "Abel Guevara (Ciberseguridad)"],
        ["Definir métricas de continuidad RTO y RPO", "Tiempo de recuperación (RTO) y punto de respaldo (RPO)", "RPO < 15 m / RTO < 30 m", "Abel Guevara (Continuidad TI)"]
    ]
    populate_table(doc.tables[1], table_objetivos_dc)

    # 6. Arquitectura On-Premise (VMware ESXi / Proxmox VE KVM)
    print("Redactando Sección 5: Arquitectura on-premise...")
    sec5_1_content = [
        ("Normal", "La topología física del centro de datos local se consolida en un único Gabinete de Comunicaciones y Servidores estándar de 19 pulgadas y 24 Unidades de Rack (24U), designado como Rack R1, ubicado en la sala de servidores climatizada de la sede Juliaca. La distribución vertical optimiza el flujo térmico (pasillo frío/caliente) y segrega el cableado de potencia del cableado de datos:")
    ]
    replace_section_content(doc, "5.1 Topología física propuesta", sec5_1_content)

    diag_5_1_rack = """[ FIGURA 5.1: ELEVACIÓN FÍSICA DE GABINETE RACK R1 (24U) — SEDE JULIACA ]
+---------------------------------------------------------------------------------+
| U24 [=========================================================================] | Organizador horizontal de fibra óptica OM4
| U23 [=========================================================================] | Patch Panel Cat 6A (24 puertos blindados RJ-45)
| U22 [  SW1-CORE1: Switch Cisco Catalyst 3850 (24 puertos 10G/1G LACP Master)  ] | Switch Core 1 (10G Backbone)
| U21 [  SW2-CORE2: Switch Cisco Catalyst 3850 (24 puertos 10G/1G LACP Standby) ] | Switch Core 2 (Redundante)
| U20 [  SW7-TOR1: Switch Top-of-Rack Cisco Catalyst 3650 (Servidores Lado A)   ] | Switch ToR 1 (Conexión NIC1 servidores)
| U19 [  SW6-TOR2: Switch Top-of-Rack Cisco Catalyst 3650 (Servidores Lado B)   ] | Switch ToR 2 (Conexión NIC2 servidores)
| U18 [  SW3-DIST1: Switch Distribución Cisco 2960X (Nave Logística / Almacén)  ] | Distribución Almacén
| U17 [  Router Cisco C1111-4P (Borde WAN · Acometida Fibra Telefónica / Claro) ] | Router de Frontera
| U16 [  FW-MAIN: Servidor Appliance Físico pfSense CE (Firewall Activo CARP)   ] | Perímetro Activo (10.10.x.2)
| U15 [  FW-BACKUP: Servidor Appliance Físico pfSense CE (Firewall Standby CARP)] | Perímetro Respaldo (10.10.x.3)
| U14 [  HV-MAIN: Servidor Físico 64 GB RAM / 1 TB NVMe (Nodo Respaldo / HA)    ] | Hipervisor Maestro Clúster
| U13 [  HV1: Servidor Físico 32 GB RAM / 500 GB SSD (DMZ, WAF, SFTP, PBX, PAW) ] | Hipervisor Nodo 1
| U12 [  HV2: Servidor Físico 32 GB RAM / 500 GB SSD (Core TI, FreeIPA, Honeypot)] | Hipervisor Nodo 2
| U11 [  HV3: Servidor Físico 32 GB RAM / 500 GB SSD (WMS01, SIEM01 Wazuh, ITSM) ] | Hipervisor Nodo 3
| U10 [  HV4: Servidor Físico 32 GB RAM / 500 GB SSD (DB01 Postgres HA, DW01)    ] | Hipervisor Nodo 4
| U09 [=========================================================================] | Pasacables con cepillo térmico
| U08 [  STORAGE-ZFS: Cabecera NAS Almacenamiento Local (ZFS RAID-10 Mirror)     ] | Almacenamiento ZFS Pool
| U07 [  STORAGE-ZFS: Bandeja de Expansión de Discos Enterprise SATA 6 Gbps     ] | Datastore Secundario
| U06 [=========================================================================] | Pasacables organizador
| U05 [=========================================================================] | Espacio libre de ventilación
| U04 [  PDU Inteligente con medición de corriente y tomas C13/C19              ] | Unidad de Distribución de Energía
| U03 [  UPS APC Smart-UPS RT 3000VA (Módulo Electrónico de Potencia)           ] | Sistema de Respaldo Eléctrico
| U02 [  UPS APC Smart-UPS RT 3000VA (Módulo de Baterías de Autonomía Extendida) ] | Autonomía 45 minutos
| U01 [  Bandeja de ventiladores de piso y anclaje antisísmico a losa           ] | Base de Gabinete
+---------------------------------------------------------------------------------+"""
    update_diagram_box(doc.tables[2], diag_5_1_rack)

    # 5.2 Diseño del Hipervisor
    sec5_2_content = [
        ("Normal", "La arquitectura de virtualización del clúster PVE-COLOGISTIC sigue estrictamente el modelo de hipervisor Tipo 1 (Bare-Metal). Aunque el catálogo institucional del proyecto integrador hace referencia conceptual a VMware ESXi, la implementación carrier-grade de Co-Logistic S.A.C. emplea Proxmox VE 8.x Enterprise KVM, demostrándose a continuación la equivalencia técnica absoluta entre ambos paradigmas:"),
        ("List Paragraph", "Conmutación Virtual (vSwitch / Linux Bridge): En VMware ESXi se emplea un vSphere Standard Switch (vSS) o Distributed Switch (vDS) con etiquetas de VLAN en modo VGT. En Proxmox VE se implementa un Linux Bridge `vmbr1` con la bandera `vlan_aware: true`. Ambos garantizan aislamiento estricto de Capa 2 y multiplexación 802.1Q troncal hacia los switches físicos."),
        ("List Paragraph", "Agregación de Enlaces (NIC Teaming / Bond LACP): Ambos hipervisores implementan un enlace agregado (bond0 en Linux / NIC Teaming en ESXi) combinando dos interfaces físicas de red (nic1 conectada a SW7-TOR1 y nic2 a SW6-TOR2) en modo active-backup con balanceo de carga, asegurando conmutación automática ante el corte de cualquier cable o falla de un switch ToR."),
        ("List Paragraph", "Interfaces de Gestión del Hipervisor (VMkernel / Linux VLAN Interface): En ESXi la gestión fuera de banda se efectúa por el puerto `vmk0` asociado al Port Group de gestión. En Proxmox VE se configura la subinterfaz lógica `vmbr1.70` con dirección estática en la VLAN 70 (ej. 10.10.70.41 para HV-MAIN), quedando totalmente inaccesible desde las redes de usuario."),
        ("List Paragraph", "Asignación de Puertos y Port Groups por Zona: Cada interfaz virtual de red de una máquina virtual (`net0`) se vincula a un puerto del bridge especificando el VLAN Tag respectivo (ej. tag=31 para WMS, tag=32 para PostgreSQL), garantizando que los paquetes salgan etiquetados sin posibilidad de saltos inter-VLAN no autorizados."),
        ("List Paragraph", "Regla de Oro de Tolerancia a Fallos D03 (Anti-Affinity): Ningún par redundante de servicios críticos (Directorio Activo FreeIPA, WMS, Base de Datos PostgreSQL o Firewall) puede residir en el mismo nodo físico. Si el host maestro falla, la réplica en el host alterno asume la carga inmediatamente."),
        ("Normal", "A continuación se detalla la matriz completa de las 22 máquinas virtuales Linux y 2 estaciones administrativas Windows que integran el centro de datos:")
    ]
    replace_section_content(doc, "5.2 Diseño del hipervisor", sec5_2_content)

    table_vms_data = [
        ["AAA01", "1 vCPU", "1024 MB", "15 GB", "Debian 12", "FreeIPA Kerberos / FreeRADIUS primario (HV2 - VLAN 30)"],
        ["AAA02", "1 vCPU", "1024 MB", "15 GB", "Debian 12", "FreeIPA Kerberos / FreeRADIUS réplica (HV-MAIN - VLAN 30)"],
        ["WMS01", "2 vCPU", "4096 MB", "30 GB", "Debian 12", "Sistema WMS Web Nginx y API REST Docker (HV3 - VLAN 31)"],
        ["WMS02", "2 vCPU", "4096 MB", "30 GB", "Debian 12", "Sistema WMS Standby / Réplica HA Docker (HV-MAIN - VLAN 31)"],
        ["DB01", "2 vCPU", "4096 MB", "30 GB", "Debian 12", "Base de Datos PostgreSQL 16 Master (HV4 - VLAN 32)"],
        ["DB02", "1 vCPU", "3072 MB", "30 GB", "Debian 12", "Base de Datos PostgreSQL 16 Réplica WAL (HV-MAIN - VLAN 32)"],
        ["DW01", "2 vCPU", "4096 MB", "30 GB", "Debian 12", "Data Warehouse PostgreSQL y Metabase BI (HV4 - VLAN 33)"],
        ["BKP01", "2 vCPU", "4096 MB", "50 GB", "Debian 12", "Servidor de Respaldos Bareos y ZFS Storage (HV-MAIN - VLAN 120)"],
        ["WAF01", "2 vCPU", "2048 MB", "20 GB", "Debian 12", "Proxy WAF Inverso Nginx con ModSecurity (HV1 - VLAN 80 DMZ)"],
        ["SFTP01", "1 vCPU", "2048 MB", "40 GB", "Debian 12", "Servidor SFTP Seguro para Clientes B2B (HV1 - VLAN 80 DMZ)"],
        ["PBX01", "2 vCPU", "2048 MB", "20 GB", "Debian 12", "Central Telefónica IP PBX Asterisk VoIP (HV1 - VLAN 35)"],
        ["MAIL01", "1 vCPU", "1024 MB", "15 GB", "Debian 12", "Relé de Correo SMTP Autenticado Postfix (HV1 - VLAN 35)"],
        ["ITSM01", "2 vCPU", "3072 MB", "45 GB", "Debian 12", "Mesa de Ayuda GLPI e Inventario Oxidized (HV3 - VLAN 34)"],
        ["INFRA01", "2 vCPU", "2048 MB", "40 GB", "Debian 12", "Core TI: DNS, DHCP, NTP, Step-CA y Cacher (HV2 - VLAN 30)"],
        ["FS01", "2 vCPU", "2048 MB", "30 GB", "Debian 12", "Servidor de Archivos Nextcloud / Samba (HV2 - VLAN 30)"],
        ["MGMT01", "2 vCPU", "2048 MB", "25 GB", "Debian 12", "Bastión Guacamole y Gestor Vaultwarden (HV2 - VLAN 70)"],
        ["MON01", "2 vCPU", "3072 MB", "30 GB", "Debian 12", "Servidor de Monitoreo Zabbix Server (HV-MAIN - VLAN 34)"],
        ["SIEM01", "3 vCPU", "6144 MB", "50 GB", "Debian 12", "Plataforma SIEM Wazuh Manager e Indexer (HV3 - VLAN 34)"],
        ["VULN01", "2 vCPU", "4096 MB", "40 GB", "Debian 12", "Escáner Vulnerabilidades OpenVAS Greenbone (HV4 - VLAN 34)"],
        ["NVR01", "2 vCPU", "2048 MB", "40 GB", "Debian 12", "Servidor Videovigilancia y Grabador NVR (HV4 - VLAN 40)"],
        ["WLC01", "1 vCPU", "2048 MB", "20 GB", "Debian 12", "Controlador WiFi Industrial para APs (HV1 - VLAN 70)"],
        ["HONEY01", "1 vCPU", "1024 MB", "10 GB", "Debian 12", "Honeypot Señuelo Trampa Cowrie/Dionaea (HV2 - VLAN 130)"],
        ["PAW01", "2 vCPU", "4096 MB", "50 GB", "Windows 11", "Estación Administrativa Privilegiada (HV1 - VLAN 10)"],
        ["PAW02", "2 vCPU", "4096 MB", "50 GB", "Windows 11", "Estación Administrativa de Respaldo (HV-MAIN - VLAN 10)"]
    ]
    populate_table(doc.tables[3], table_vms_data)

    diag_5_2_hypervisor = """[ FIGURA 5.2: DISEÑO INTERNO DEL HIPERVISOR (CONMUTACIÓN VIRTUAL Y BONDING) ]
+---------------------------------------------------------------------------------------------------+
| SERVIDOR FÍSICO (NODO HIPERVISOR: Dell Precision / PowerEdge · Proxmox VE 8.x Enterprise KVM)     |
| Interfaz de Gestión Fuera de Banda: vmbr1.70 (10.10.70.x/24)                                      |
+---------------------------------------------------------------------------------------------------+
| MÁQUINAS VIRTUALES (AISLAMIENTO DE PROCESO Y MEMORIA KVM)                                         |
|  [VM: WMS01]           [VM: DB01]            [VM: SIEM01]          [VM: BASTION]     [VM: HONEY]  |
|  net0: tag=31          net0: tag=32          net0: tag=34          net0: tag=70      net0: tag=130|
|  IP: 10.10.31.11       IP: 10.10.32.11       IP: 10.10.34.20       IP: 10.10.70.5    IP: .130.10  |
+------+----------------------+---------------------+---------------------+-----------------+-------+
       |                      |                     |                     |                 |
+------v----------------------v---------------------v---------------------v-----------------v-------+
| CONMUTADOR VIRTUAL CENTRAL: LINUX BRIDGE vmbr1 (vlan_aware = true) [Equivalente vDS de VMware]    |
| Multiplexación 802.1Q · Filtrado estricto de MAC por puerto · Prevención de VLAN Hopping          |
+-------------------------------------------------+-------------------------------------------------+
                                                  |
                               +------------------v------------------+
                               | ENLACE AGREGADO: bond0              |
                               | Modo: active-backup (LACP failover) |
                               +---------+-----------------+---------+
                                         |                 |
                   +---------------------+                 +---------------------+
                   | (Cable UTP Cat 6A)                            | (Cable UTP Cat 6A)
         +---------v---------+                           +---------v---------+
         | Interfaz nic1     |                           | Interfaz nic2     |
         +---------+---------+                           +---------+---------+
                   |                                               |
+------------------v------------------+                 +----------v--------------------+
| SWITCH SW7-TOR1 (ToR Lado A)        |                 | SWITCH SW6-TOR2 (ToR Lado B)  |
| Cisco Catalyst 3650 Datacenter      |                 | Cisco Catalyst 3650 Datacenter|
+-------------------------------------+                 +-------------------------------+"""
    update_diagram_box(doc.tables[4], diag_5_2_hypervisor)

    # 7. Arquitectura Cloud (GCP / AWS)
    print("Redactando Sección 6: Arquitectura Cloud...")
    sec6_1_content = [
        ("Normal", "La selección de la infraestructura en nube para Co-Logistic S.A.C. responde a un riguroso análisis de latencia de red, costo operativo y soberanía de datos:"),
        ("List Paragraph", "Región Cloud Seleccionada: Google Cloud Platform, región southamerica-west1 (Santiago de Chile, Chile). En un escenario alterno bajo Amazon Web Services, la región equivalente es sa-east-1 (São Paulo, Brasil)."),
        ("List Paragraph", "Justificación Técnica de Latencia: Las conexiones hacia Santiago de Chile transitan por los cables submarinos de fibra óptica del Pacífico (cable South American Crossing - SAC y Mistral), registrando tiempos de ida y vuelta (RTT) estables de entre 35 y 40 ms desde el Perú. En contraste, las regiones tradicionales de Norteamérica (us-east-1 Virginia) presentan latencias superiores a 110 ms, lo que triplica los tiempos de sincronización de datos y degrada la experiencia de contingencia."),
        ("List Paragraph", "Cumplimiento y Continuidad Operativa: Alojar los respaldos en la región sudamericana cumple con los requerimientos de soberanía y protección de datos exigidos por la Ley N° 29733 (Ley de Protección de Datos Personales del Perú) y facilita la interoperabilidad con las plataformas de SUNAT.")
    ]
    replace_section_content(doc, "6.1 Selección de región y justificación", sec6_1_content)

    sec6_2_content = [
        ("Normal", "Se ha diseñado una nube privada virtual (Virtual Private Cloud - VPC) en Google Cloud designada como `VPC-COLOGISTIC`, con un rango no superpuesto 10.20.0.0/24 (preservando el rango 10.10.0.0/16 para el centro de datos local). La VPC implementa subredes personalizadas (custom subnetting) segregadas por función y nivel de acceso:")
    ]
    replace_section_content(doc, "6.2 Diseño de VPC", sec6_2_content)

    table_subredes_cloud = [
        ["NUBE-BORDE", "10.20.0.0/28", "Pública (NAT / Gateway)", "Aloja la VM GCP-BORDE con IP externa y terminación VPN"],
        ["NUBE-TUNEL", "10.20.0.16/29", "Tránsito VPN (Privada)", "Espacio punto a punto para interfaces virtuales WireGuard wg0"],
        ["NUBE-PRIVADA", "10.20.0.32/28", "Privada (Internal Only)", "Cargas de cómputo de contingencia interna y acceso privado a Google"]
    ]
    populate_table(doc.tables[5], table_subredes_cloud)

    diag_6_1_vpc = """[ FIGURA 6.1: DISEÑO DE ARQUITECTURA CLOUD (VPC, SUBREDES Y GATEWAYS) ]
+---------------------------------------------------------------------------------------------------+
| GOOGLE CLOUD PLATFORM / AWS · REGIÓN: southamerica-west1 (Santiago de Chile)                      |
| VPC: VPC-COLOGISTIC (Bloque IPv4: 10.20.0.0/24)                                                   |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  +-------------------------------------+       +-----------------------------------------------+  |
|  | SUBRED: NUBE-BORDE (10.20.0.0/28)   |       | SUBRED: NUBE-PRIVADA (10.20.0.32/28)          |  |
|  | Tipo: Pública (Acceso a Internet)   |       | Tipo: Privada (Private Google Access = true)  |  |
|  |                                     |       |                                               |  |
|  | [ Instancia Compute Engine:         |       | [ Cargas de Contingencia DRP Internas ]       |  |
|  |   GCP-BORDE (e2-micro) ]            |       | Aisladas de Internet; acceso exclusivo vía    |  |
|  |   - IP Externa: 34.176.121.24       |       | túnel VPN o Private Service Connect           |  |
|  |   - IP Privada: 10.20.0.4           |       |                                               |  |
|  |   - Landing Page DRP (Nginx Web)    |       |                                               |  |
|  |   - Orquestador de Restauración     |       |                                               |  |
|  +------------------+------------------+       +-----------------------------------------------+  |
|                     |                                                                             |
|  +------------------v------------------+       +-----------------------------------------------+  |
|  | SUBRED: NUBE-TUNEL (10.20.0.16/29)  |       | BUCKETS DE OBJECT STORAGE (Cloud Storage / S3)|  |
|  | Tránsito VPN WireGuard               |       | ├── cologistic-respaldos-cologistic-cloud     |  |
|  | - Interfaz Cloud wg0: 10.20.0.17    |       | │   (Almacén inmutable de respaldos Bareos)   |  |
|  | - Interfaz Local wg0: 10.20.0.18    |       | └── cologistic-tfstate-cologistic-cloud       |  |
|  +------------------+------------------+       |     (Estado de infraestructura Terraform IaC) |  |
|                     |                          +-----------------------------------------------+  |
+---------------------|-----------------------------------------------------------------------------+
                      |
                      +==================== ENLACE HÍBRIDO CIFRADO =====================+
                               Túnel WireGuard UDP 51820 · ChaCha20-Poly1305
                               Datacenter On-Premise Juliaca (10.10.0.0/16)"""
    update_diagram_box(doc.tables[6], diag_6_1_vpc)

    # 6.3 Servicios EC2 / Compute Engine Planeados
    sec6_3_intro = [
        ("Normal", "La arquitectura cloud adopta un enfoque minimalista y de alta eficiencia de costos, desplegando únicamente los recursos indispensables para la terminación del túnel, contingencia web y almacenamiento seguro:")
    ]
    replace_section_content(doc, "6.3 Servicios EC2 planeados", sec6_3_intro)

    table_instancias_cloud = [
        ["GCP-BORDE / EC2-Borde", "e2-micro / t3.micro", "Borde WireGuard, landing page DRP y orquestador", "NUBE-BORDE (10.20.0.4 / 34.176.121.24)"],
        ["cologistic-respaldos", "Cloud Storage / S3 Standard", "Almacenamiento seguro offsite para Bareos y ZFS", "Global / Región Chile (Endpoint Privado)"],
        ["cologistic-tfstate", "Cloud Storage / S3 Standard", "Almacenamiento versionado del estado Terraform", "Global / Región Chile (Endpoint Privado)"]
    ]
    populate_table(doc.tables[7], table_instancias_cloud)

    # 6.4 Security Groups y VPC Firewall Rules Planeados
    sec6_4_intro = [
        ("Normal", "La seguridad en la nube se estructura mediante reglas de cortafuegos de VPC (homólogas a los Security Groups y Network ACLs de AWS) gobernadas por una política predeterminada de denegación total (Default Deny Ingress):")
    ]
    replace_section_content(doc, "6.4 Security Groups y NACL planeados", sec6_4_intro)

    table_firewall_cloud = [
        ["fw-allow-wireguard", "Instancia GCP-BORDE", "Permite UDP 51820 únicamente desde IP WAN Juliaca (168.121.48.246)"],
        ["fw-allow-web-contingencia", "Instancia GCP-BORDE", "Permite TCP 80 y 443 desde Internet (0.0.0.0/0) para portal DRP"],
        ["fw-allow-internal-tunnel", "VPC-COLOGISTIC", "Permite todo protocolo originado en la red local (10.10.0.0/16)"],
        ["fw-allow-ssh-mgmt", "Instancia GCP-BORDE", "Permite TCP 22 exclusivamente desde la VLAN de gestión (10.10.70.0/24)"],
        ["fw-deny-all-ingress", "VPC-COLOGISTIC", "Deniega por defecto todo tráfico de entrada no autorizado (Zero-Trust)"]
    ]
    populate_table(doc.tables[8], table_firewall_cloud)

    # 8. Mecanismo de Integración Híbrida
    print("Redactando Sección 7: Mecanismo de integración híbrida...")
    sec7_content = [
        ("Normal", "El mecanismo de integración híbrida articula directamente el presente diseño de centro de datos con el documento 'Análisis y Diseño de Red' (S1_E1), manteniendo una coherencia técnica estricta:"),
        ("List Paragraph", "Convergencia de Enrutamiento: El clúster pfSense on-premise enruta el bloque cloud 10.20.0.0/24 hacia la IP de túnel 10.20.0.17 (interfaz wg0 de GCP-BORDE). A su vez, la tabla de rutas de la VPC de Google Cloud posee la ruta 10.10.0.0/16 con siguiente salto (next-hop) en la IP privada 10.20.0.4, habilitando comunicación bidireccional transparente entre ambas infraestructuras."),
        ("List Paragraph", "Replicación de Respaldos Offsite hacia Cloud Storage: El servidor de respaldos Bareos (BKP01, 10.10.120.11) ubicado en el centro de datos local genera copias completas e incrementales de las máquinas virtuales y bases de datos. Mediante scripts automatizados y el CLI de almacenamiento seguro, los volúmenes de respaldo se cifran localmente con AES-256-GCM y se transfieren al bucket `cologistic-respaldos-cologistic-cloud` utilizando una Cuenta de Servicio IAM con privilegios mínimos (sa-logs / sa-terraform), sin exponer credenciales estáticas."),
        ("List Paragraph", "Mecanismo de Activación DRP ante Desastre: Si la sede física de Juliaca sufre un siniestro total, el equipo de TI activa el plan de contingencia: la instancia GCP-BORDE descarga el volcado más reciente de PostgreSQL desde el bucket de almacenamiento seguro, monta la estructura transaccional y pone en línea la interfaz web de contingencia (http://34.176.121.24), restableciendo la visibilidad operativa en menos de 30 minutos.")
    ]
    replace_section_content(doc, "7. Mecanismo de integración híbrida", sec7_content)

    # 9. Matriz de Componentes del Centro de Datos
    print("Redactando Sección 8: Matriz consolidada de componentes...")
    sec8_content = [
        ("Normal", "La totalidad de los componentes de hardware, hipervisores, almacenamiento y servicios cloud que integran el centro de datos híbrido se consolidan en la siguiente matriz técnica:")
    ]
    replace_section_content(doc, "8. Matriz de componentes del centro de datos", sec8_content)

    table_componentes_dc = [
        ["Clúster Hipervisores (HV-MAIN, HV1-HV4)", "On-Premise", "Cómputo Físico", "Ejecución de las 24 VMs en Proxmox VE KVM", "Crítica"],
        ["Switches Core & Distribución (SW1-SW4)", "On-Premise", "Red Troncal", "Conmutación 10G LACP y agregación de tráfico", "Crítica"],
        ["Switches Top-of-Rack (SW6-TOR2, SW7-TOR1)", "On-Premise", "Red ToR Datacenter", "Conexión redundante NIC1/NIC2 de servidores", "Crítica"],
        ["Firewalls de Perímetro (FW-MAIN / BACKUP)", "On-Premise", "Seguridad Perimetral", "Enrutamiento inter-VLAN, CARP e inspección IDS", "Crítica"],
        ["Router de Frontera Cisco C1111-4P", "On-Premise", "Conectividad WAN", "Terminación de fibra ISP1/ISP2 y NAT público", "Crítica"],
        ["Almacenamiento Local ZFS (BKP01)", "On-Premise", "Storage ZFS RAID-10", "Datastore local, snapshots y servidor Bareos", "Alta"],
        ["UPS APC Smart-UPS RT 3000VA", "On-Premise", "Energía Estabilizada", "Suministro ininterrumpido ante cortes de fluido", "Crítica"],
        ["Instancia de Borde Cloud (GCP-BORDE)", "Google Cloud", "Compute Engine", "Terminación WireGuard, contingencia web y DRP", "Alta"],
        ["Cloud Storage Bucket (cologistic-respaldos)", "Google Cloud", "Object Storage", "Almacenamiento offsite inmutable de respaldos", "Crítica"],
        ["Cloud Storage Bucket (cologistic-tfstate)", "Google Cloud", "Object Storage", "Control de versiones de infraestructura como código", "Alta"],
        ["Red Virtual Cloud (VPC-COLOGISTIC)", "Google Cloud", "Red Definida Software", "Aislamiento y subredes seguras en la nube", "Crítica"]
    ]
    populate_table(doc.tables[9], table_componentes_dc)

    # 10. Dimensionamiento y Capacidad
    print("Redactando Sección 9: Dimensionamiento y capacidad...")
    sec9_content = [
        ("Normal", "Se presenta la memoria de cálculo y sustentación cuantitativa del dimensionamiento técnico:"),
        ("List Paragraph", "Capacidad Física Consolidada en el Clúster Local: 5 servidores físicos totalizan 40 núcleos físicos de procesamiento (80 hilos vCPU lógicos gracias a Hyper-Threading), 188 GB de memoria RAM ECC registrada (HV-MAIN con 60 GB y cuatro nodos con 32 GB cada uno) y 2.4 TB de almacenamiento útil en arreglos de discos ZFS de alta velocidad."),
        ("List Paragraph", "Recursos Asignados a la Flota de 24 Máquinas Virtuales: Un total de 41 vCPUs asignadas, 63 GB de memoria RAM asignada (64,512 MB) y 685 GB de almacenamiento virtual en disco."),
        ("List Paragraph", "Análisis de Sobreasignación de CPU (Overcommit Ratio): La relación vCPU asignadas vs núcleos físicos reales es de 41 / 40 = 1.02:1 (prácticamente 1:1), encontrándose extraordinariamente lejos del límite conservador de la industria (3:1 a 4:1 en entornos de producción), garantizando que las tareas de cómputo crítico nunca sufran inanición (CPU starvation)."),
        ("List Paragraph", "Holgura y Margen Libre de Memoria RAM: La memoria asignada (63 GB) representa únicamente el 33.5 % de la memoria física disponible (188 GB). Los 125 GB de memoria RAM restantes (66.5 % libre) se destinan estratégicamente a la memoria caché de lectura ZFS (Adaptive Replacement Cache - ARC), garantizando tiempos de respuesta ultrarrápidos para las bases de datos PostgreSQL, y sirviendo como reserva de absorción ante contingencias."),
        ("List Paragraph", "Tolerancia a Fallos N+1: Si el nodo de mayor envergadura (HV-MAIN con 60 GB) quedase fuera de servicio por avería catastrófica de hardware, los 4 hipervisores restantes (128 GB de RAM física) pueden albergar la totalidad de las 24 VMs con una tasa de ocupación agregada de apenas el 49.2 % de la memoria, demostrando resiliencia estructural completa.")
    ]
    replace_section_content(doc, "9. Dimensionamiento y capacidad", sec9_content)

    # 11. Disponibilidad y Continuidad en el Diseño
    print("Redactando Sección 10: Disponibilidad y continuidad...")
    sec10_content = [
        ("Normal", "La arquitectura integra previsiones de continuidad operativa estructuradas en tres niveles:"),
        ("List Paragraph", "Alta Disponibilidad Local por Servicio (Regla D03): Para mitigar la ausencia de almacenamiento SAN compartido de alto costo, la redundancia se garantiza a nivel de servicio. Los servicios críticos operan en pares activo/pasivo desacoplados en nodos físicos distintos: Directorio Activo (AAA01 en HV2, AAA02 en HV-MAIN), Sistema WMS (WMS01 en HV3, WMS02 en HV-MAIN) y Base de Datos (DB01 Master en HV4, DB02 Réplica en HV-MAIN con replicación continua de registros de transacciones Write-Ahead Logging - WAL)."),
        ("List Paragraph", "Estrategia de Respaldo 3-2-1: Se mantiene un esquema riguroso compuesto por 3 copias de los datos de negocio (producción local, volúmenes de respaldo en Bareos BKP01, y réplica en la nube), en 2 medios de almacenamiento diferentes (discos SSD/NVMe locales y almacenamiento de objetos en la nube), y 1 copia fuera de sede (Google Cloud Storage en Santiago de Chile)."),
        ("List Paragraph", "Objetivos de Recuperación Formalizados (RTO y RPO): Para la base de datos transaccional PostgreSQL y el sistema WMS: RPO < 15 minutos (mediante snapshots ZFS periódicos y archivado de WALs) y RTO < 30 minutos (tiempo de conmutación a réplica o levantamiento del entorno de contingencia). Para servicios de archivos generales y monitoreo: RPO < 1 hora y RTO < 2 horas."),
        ("List Paragraph", "Protección Eléctrica y Climatización: El sistema UPS APC Smart-UPS RT 3000VA garantiza hasta 45 minutos de autonomía continua ante cortes imprevistos en la red eléctrica comercial, permitiendo el apagado ordenado de las VMs no críticas mediante el demonio de apagado controlado apcupsd.")
    ]
    replace_section_content(doc, "10. Consideraciones de disponibilidad y continuidad en el diseño", sec10_content)

    # 12. Conclusiones y Hoja de Ruta
    print("Redactando Sección 11: Conclusiones y hoja de ruta...")
    sec11_content = [
        ("Normal", "Conclusiones del diseño de centro de datos híbrido:"),
        ("List Paragraph", "Se ha formulado un diseño integral, moderno y auditable que resuelve la dispersión de servidores previos, consolidando las cargas en un clúster local de 5 hipervisores de alta disponibilidad con topología física en Rack R1 (24U) y conmutación virtual 802.1Q."),
        ("List Paragraph", "Se demostró la equivalencia conceptual y técnica entre VMware ESXi y Proxmox VE KVM, justificando la adopción de este último por su capacidad nativa de gestión como Infraestructura como Código (IaC con Cloud-Init y Terraform) y su soberanía operativa."),
        ("List Paragraph", "La selección de Google Cloud en Santiago de Chile (~38 ms de latencia) proporciona un entorno de contingencia y respaldo offsite que garantiza el cumplimiento de los SLAs institucionales y las exigencias de la norma ISO/IEC 27001:2022."),
        ("List Paragraph", "Hitos alcanzados en Semestre 1: Especificación formal en código YAML en cologistic-infra (18/18 pruebas unitarias superadas) y despliegue funcional en la nube verificado exitosamente en el proyecto cologistic-cloud."),
        ("List Paragraph", "Hoja de ruta para el Semestre 2 (Entregable S2_E3): Aprovisionamiento automatizado de las 22 VMs mediante Terraform en Proxmox VE, configuración de la replicación WAL en PostgreSQL 16, configuración de trabajos de respaldo Bareos hacia Cloud Storage, y ejecución del simulacro formal de contingencia y recuperación DRP con medición de RTO y RPO reales.")
    ]
    replace_section_content(doc, "11. Conclusiones y hoja de ruta hacia la implementación", sec11_content)

    # 13. Referencias
    print("Redactando Sección 12: Referencias...")
    sec12_content = [
        ("Normal", "[1] Proxmox Server Solutions GmbH, \"Proxmox VE Administration Guide: Virtualization, Storage and Networking,\" Release 8.2, Vienna, Austria, 2024. [Online]. Disponible: https://pve.proxmox.com/pve-docs/"),
        ("Normal", "[2] VMware Inc., \"VMware vSphere 8.0 Deployment Guide: Virtual Networking, vDS and High Availability Architecture,\" Broadcom Technical Publications, San Jose, CA, 2023."),
        ("Normal", "[3] Google Cloud, \"Compute Engine Architecture Framework: System Design, Disaster Recovery and Networking,\" Google Cloud Architecture Center, Mountain View, CA, 2024."),
        ("Normal", "[4] Amazon Web Services, \"AWS Well-Architected Framework: Reliability and Security Pillars for Hybrid Workloads,\" AWS Whitepapers, Seattle, WA, 2023."),
        ("Normal", "[5] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection — Requirements,\" Geneva, Switzerland, 2022."),
        ("Normal", "[6] Bareos Project, \"Bareos Open Source Backup & Recovery: Disaster Recovery and Cloud Storage Integration,\" Version 23.0, Cologne, Germany, 2024. [Online]. Disponible: https://docs.bareos.org/"),
        ("Normal", "[7] PostgreSQL Global Development Group, \"PostgreSQL 16 Documentation: High Availability, Load Balancing, and Replication Architecture,\" 2024. [Online]. Disponible: https://www.postgresql.org/docs/16/high-availability.html")
    ]
    replace_section_content(doc, "12. Referencias", sec12_content)

    print(f"Guardando documento final en: {OUTPUT_PATH}")
    doc.save(OUTPUT_PATH)
    print("¡Entregable S1_E2 generado exitosamente!")

if __name__ == "__main__":
    main()
