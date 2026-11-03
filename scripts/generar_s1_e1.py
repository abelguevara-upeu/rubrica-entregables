#!/usr/bin/env python3
"""
generar_s1_e1.py
Genera el Entregable 1 de Semestre 1 (S1_E1): Análisis y Diseño de Red.
Cumple con la rúbrica oficial de Proyecto Integrador UPeU / Co-Logistic S.A.C.
Sin overrides manuales de fuente/color/tamaño: usa estrictamente los estilos del documento.
"""

import sys
import docx
from copy import deepcopy

TEMPLATE_PATH = "/Users/abelguevarah/Desktop/perfil-egreso/rubrica-entregables/templates/s1_e1_analisis_y_diseno_de_red_nlcwgpwptr.docx"
OUTPUT_PATH = "/Users/abelguevarah/Desktop/perfil-egreso/rubrica-entregables/entregables/s1_e1_analisis_y_diseno_de_red.docx"

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
            # No remover si es un pie de figura que queremos conservar
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
    print("Cargando plantilla S1_E1...")
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
        ("Normal", "El presente informe técnico formula el diseño integral y formal de la arquitectura de red y seguridad perimetral para Co-Logistic S.A.C., un operador logístico 3PL especializado en almacenamiento y distribución en la región sur del Perú, cuya sede central y centro de distribución opera en Juliaca, Departamento de Puno. El proyecto responde a la necesidad crítica de resolver la obsolescencia de una infraestructura previa plana y vulnerable, carente de segmentación y con múltiples puntos únicos de fallo (SPOF), alineando las tecnologías de conectividad y control con los lineamientos de la norma internacional ISO/IEC 27001:2022."),
        ("Normal", "Principales dimensiones del diseño desarrollado:"),
        ("List Paragraph", "Organización y escenario: Co-Logistic S.A.C., centro de distribución de 12,000 m², con una dotación de 45 usuarios administrativos/operativos y un parque de más de 60 terminales móviles de radiofrecuencia (pistolas RF Zebra), balanzas conectadas y tabletas de picking en almacén."),
        ("List Paragraph", "Problema abordado: Red corporativa no segmentada, concurrencia desordenada de tráfico administrativo con datos de misión crítica (WMS y PostgreSQL) y videovigilancia de alto ancho de banda, exposición de servicios sin DMZ, ausencia de cifrado intersitio y alta vulnerabilidad frente a movimientos laterales de código malicioso."),
        ("List Paragraph", "Topología de infraestructura propuesta: Arquitectura jerárquica carrier-grade de 10 Gbps con switches Cisco Catalyst (Core SW1/SW2 en VSS/LACP, Distribución SW3/SW4, Acceso SW5 y Top-of-Rack SW6/SW7 en centro de datos). El perímetro y ruteo inter-VLAN se encomienda a un par de appliances pfSense Community Edition en cluster de alta disponibilidad activo/pasivo mediante el protocolo CARP y sincronización pfsync en capa 2."),
        ("List Paragraph", "Mecanismo de integración híbrida: Túnel VPN sitio a sitio basado en WireGuard (UDP 51820) sobre criptografía moderna de curvas elípticas (Curve25519 y ChaCha20-Poly1305), interconectando el centro de datos local (10.10.0.0/16) con la nube VPC en Google Cloud Platform (región southamerica-west1, Santiago de Chile, 10.20.0.0/24). Esta selección ofrece una latencia óptima (~38 ms) frente a nubes en Norteamérica (>110 ms), garantizando la viabilidad de la replicación de respaldos y contingencia operativa."),
        ("List Paragraph", "Zonificación y segmentación de seguridad: Implementación de 18 redes de área local virtuales (VLANs IEEE 802.1Q) categorizadas en 12 zonas de seguridad independientes (Perímetro, DMZ, LAN Administrativa, Operaciones WMS, Servicios Core, Base de Datos, Inteligencia de Negocios, Monitoreo/SOC, Telefonía VoIP, CCTV, IoT/Control de Acceso, Respaldo/Storage y Honeypot)."),
        ("List Paragraph", "Riesgos de red mitigados: Secuestro de sesiones, interceptación de tráfico no cifrado, movimiento lateral de ransomware entre estaciones ofimáticas y servidores de base de datos, ataques de denegación de servicio (DoS) y brechas por compromiso de terminales IoT o dispositivos de invitados."),
        ("List Paragraph", "Resultados del diseño y hoja de ruta: Se entrega una arquitectura completamente documentada como Fuente Única de Verdad (SSOT) en código, validada mediante 18 pruebas automatizadas de coherencia topológica. Para el Semestre 2 (Entregable S2_E2) se proyecta el aprovisionamiento en hardware físico, pruebas de penetración, validación de conmutación por falla CARP en <3 segundos y afinamiento del motor IDS/IPS Suricata con Wazuh SIEM.")
    ]
    replace_section_content(doc, "1. Resumen ejecutivo del diseño de red", sec1_content)

    # Diagrama 1.1: Topología ejecutiva
    diag_1_1 = """[ FIGURA 1.1: ARQUITECTURA EJECUTIVA SIMPLIFICADA — CO-LOGISTIC S.A.C. ]
+---------------------------------------------------------------------------------------------------+
| INTERNET / ACCESO PÚBLICO                                                                         |
| ISP 1: Telefónica (Fibra Óptica Dedicada)           ISP 2: Claro Telecom (Enlace de Respaldo)     |
+------------------------------------+--------------------------------------------------------------+
                                     |
                        +------------v------------+
                        |  Router Cisco C1111-4P  | (Frontera WAN · NAT · IP: 168.121.48.246)
                        +------------+------------+
                                     | (VLANs 901-904 /30)
                 +-------------------+-------------------+
                 |                                       |
    +------------v------------+             +------------v------------+
    | FW-CORE-01 (pfSense)    |<=== CARP ===>| FW-CORE-02 (pfSense)    | (Cluster Alta Disponibilidad)
    | Activo (Master)         |  (VLAN 100) | Standby (Backup)        | VIPs Gateways: 10.10.x.1
    +------------+------------+             +------------+------------+
                 |                                       |
                 +-------------------+-------------------+
                                     | (Trunk 802.1Q / LACP)
    +--------------------------------v------------------------------------+
    | SWITCHES CORE & DISTRIBUCIÓN CISCO CATALYST (SW1-CORE1 / SW2-CORE2) |
    +---+------------------------+-------------------+----------------+---+
        |                        |                   |                |
+-------v-------+        +-------v-------+   +-------v-------+ +------v------+
| ZONA ACCESO   |        | ZONA WMS OPS  |   | ZONA DMZ      | | CENTRO DATOS|
| VLAN 10 Admin |        | VLAN 20 WMS   |   | VLAN 80 DMZ   | | VLANs 30-35 |
| VLAN 50 Voz   |        | VLAN 90 WiFi  |   | Proxy WAF01   | | DB, WMS App |
| VLAN 60 Guest |        | Balanzas/PFRF |   | SFTP B2B      | | ZFS, Bareos |
+---------------+        +---------------+   +---------------+ +-------------+
                                     |
    =================================v===================================
    ENLACE HÍBRIDO: TÚNEL VPN WIREGUARD (UDP 51820 · ChaCha20-Poly1305)
    Datacenter On-Premise (10.10.0.0/16) <=========> Cloud VPC GCP (10.20.0.0/24)
    =====================================================================
    GOOGLE CLOUD PLATFORM (southamerica-west1 Santiago de Chile)
    ├── Subred NUBE-BORDE (10.20.0.0/28)    -> VM GCP-BORDE (IP Pública: 34.176.121.24)
    ├── Subred NUBE-TUNEL (10.20.0.16/29)   -> Interfaz VPN wg0 (10.20.0.17 / 10.20.0.18)
    └── Subred NUBE-PRIVADA (10.20.0.32/28) -> Almacenamiento Cloud Storage (Respaldos offsite)"""
    update_diagram_box(doc.tables[0], diag_1_1)

    # 3. Descripción de la Organización y Necesidades de Red
    print("Redactando Sección 2: Organización y necesidades...")
    sec2_1_content = [
        ("Normal", "Co-Logistic S.A.C. es una empresa peruana dedicada al suministro de servicios de logística integral para terceros (Third-Party Logistics - 3PL), cubriendo servicios de recepción, custodia, preparación de pedidos (picking/packing) y despacho capilar en las regiones de Puno, Cusco, Arequipa y Moquegua. La sede operativa principal y centro de distribución se sitúa en el Parque Industrial de la ciudad de Juliaca."),
        ("Normal", "La escala y dinámica de las operaciones determinan requerimientos técnicos precisos:"),
        ("List Paragraph", "Usuarios y puestos de trabajo: La sede alberga 45 puestos corporativos (gerencia, finanzas, operaciones, aduanas, seguridad patrimonial y mesa de ayuda) y más de 60 terminales de captura móvil distribuidos en la nave logística de 12,000 m²."),
        ("List Paragraph", "Servicios TI dependientes de la red: Sistema de Gestión de Almacenes (WMS basado en arquitectura de microservicios contenerizados), motor de base de datos relacional PostgreSQL en alta disponibilidad, ERP corporativo Odoo para facturación electrónica homologada con SUNAT, telefonía IP Asterisk para coordinación operativa, y sistema de videovigilancia con 32 cámaras IP de alta definición."),
        ("List Paragraph", "Uso balanceado de infraestructura local y nube: El procesamiento operativo transaccional se consolida on-premise en el centro de datos local para garantizar latencias inferiores a 2 ms requeridas por las terminales de radiofrecuencia, mientras que los servicios de respaldo inmutable offsite y portal web corporativo de contingencia residen en la nube de Google Cloud Platform (región Santiago de Chile)."),
        ("List Paragraph", "Demanda de ancho de banda y resiliencia: Enlaces simétricos redundantes con dos proveedores independientes (Telefónica y Claro) para mitigar cortes de fibra óptica pública, garantizando disponibilidad de 99.9% para la operación continua 24/7.")
    ]
    replace_section_content(doc, "2.1 Descripción general", sec2_1_content)

    # Tabla 2.2: Procesos Críticos
    sec2_2_intro = [
        ("Normal", "La operación logística demanda una estricta clasificación de los procesos de negocio en función de su impacto directo ante una degradación o interrupción de la red. A continuación se identifican los procesos críticos institucionales:")
    ]
    replace_section_content(doc, "2.2 Servicios y procesos críticos dependientes de la red", sec2_2_intro)

    table_procesos_data = [
        ["Recepción y Registro de Carga", "WMS Inbound API / Nginx Web", "Crítica"],
        ["Control de Stock y Ubicaciones", "Base de Datos PostgreSQL 16 HA", "Crítica"],
        ["Preparación de Pedidos (Picking)", "WMS Mobile API & Scanners RF", "Crítica"],
        ["Despacho y Facturación Electrónica", "ERP Odoo & Interfaz Web SUNAT", "Alta"],
        ["Autenticación y Control de Acceso", "FreeIPA Kerberos / FreeRADIUS 802.1X", "Crítica"],
        ["Seguridad Patrimonial y Circuito Cerrado", "NVR Hikvision & Cámaras RTSP", "Alta"],
        ["Telefonía y Comunicaciones Operativas", "PBX Asterisk SIP / Telefonía IP", "Media"],
        ["Auditoría y Monitoreo de Seguridad", "Wazuh SIEM / Suricata IDS / Zabbix", "Alta"],
        ["Respaldo Offsite y Protección de Datos", "Bareos & Google Cloud Storage", "Alta"]
    ]
    populate_table(doc.tables[1], table_procesos_data)

    sec2_3_content = [
        ("Normal", "Para asegurar la pertinencia del diseño de red y dar cumplimiento a los controles del SGSI bajo ISO/IEC 27001:2022 (cláusula 4.2), se han catalogado las partes interesadas relevantes y sus expectativas específicas de conectividad y ciberseguridad:"),
        ("List Paragraph", "Clientes Corporativos (Retail y Consumo Masivo): Exigen disponibilidad permanente de inventarios (SLA 99.9%), confidencialidad estricta en datos de mercadería e interfaces B2B (SFTP/API) seguras y auditables."),
        ("List Paragraph", "Operadores de Almacén y Cuadrillas: Demandan conectividad inalámbrica continua y de baja latencia en toda la nave de 12,000 m², con itinerancia (roaming) transparente para las pistolas RF Zebra sin cortes de sesión."),
        ("List Paragraph", "Dirección General y Gerencia de Operaciones: Requieren protección frente a incidentes de ransomware que puedan paralizar los despachos, cumplimiento de regulaciones aduaneras y optimización de costos en enlaces y nube."),
        ("List Paragraph", "Equipo de TI y Ciberseguridad: Necesitan gestión fuera de banda (OOB) aislada, trazabilidad total de conexiones inter-VLAN mediante logs centralizados en SIEM y herramientas de detección temprana (IDS y Honeypot)."),
        ("List Paragraph", "Proveedores de Enlace (ISP) y Cloud (GCP/AWS): Demandan interfaces normalizadas de demarcación WAN (RFC 1918), protocolos de enrutamiento estables y parámetros de seguridad estandarizados en el túnel VPN."),
        ("List Paragraph", "Organismos Reguladores (SUNAT, MTC, MinJus/DGPDP): Exigen trazabilidad fiscal inalterable, conservación de bitácoras por periodos normados y protección de datos personales conforme a la Ley N° 29733.")
    ]
    replace_section_content(doc, "2.3 Partes interesadas relevantes a la red", sec2_3_content)

    # 4. Alcance del Diseño de Red
    print("Redactando Sección 3: Alcance del diseño de red...")
    sec3_1_content = [
        ("Normal", "El alcance del presente diseño abarca la arquitectura completa de conectividad de Capa 2 y Capa 3, direccionamiento IPv4 según RFC 1918, segmentación mediante 18 VLANs basadas en el estándar IEEE 802.1Q, cluster de seguridad perimetral pfSense en alta disponibilidad (CARP/pfsync), túnel de interconexión híbrida WireGuard hacia la nube de Google Cloud Platform (región Santiago de Chile), políticas de filtrado Zero-Trust y controles de detección de intrusiones (IDS/IPS y Honeypot) para la sede principal de Co-Logistic S.A.C. en Juliaca.")
    ]
    replace_section_content(doc, "3.1 Declaración de alcance", sec3_1_content)

    sec3_2_content = [
        ("Normal", "Los límites del proyecto se estructuran bajo tres dimensiones:"),
        ("List Paragraph", "Límites Físicos: Centro de datos de la sede Juliaca (Gabinete Rack R1 de 24U, sala de servidores climatizada), infraestructura de cableado estructurado Categoría 6A y enlaces de fibra óptica OM4, switches de distribución en nave logística y equipos de borde."),
        ("List Paragraph", "Límites Tecnológicos: Switches Cisco Catalyst gestionados (SW1 a SW7), appliances pfSense CE (FW-CORE-01 y FW-CORE-02), router perimetral Cisco C1111-4P, enlaces punto a punto WAN, túnel WireGuard VPN, VPC de Google Cloud Platform (VPC-COLOGISTIC), motor IDS/IPS Suricata, agentes Wazuh HIDS y señuelo Dionaea/Cowrie."),
        ("List Paragraph", "Límites Organizacionales: La administración, mantenimiento y monitoreo corresponden de forma privativa a la Jefatura de Infraestructura y Ciberseguridad de Co-Logistic S.A.C. Los niveles de acceso se delimitan mediante Control de Acceso Basado en Roles (RBAC) y perfiles formalizados en el SGSI.")
    ]
    replace_section_content(doc, "3.2 Límites", sec3_2_content)

    sec3_3_content = [
        ("Normal", "Se definen formalmente las siguientes exclusiones técnicas:"),
        ("List Paragraph", "Dispositivos personales de trabajadores (BYOD): Quedan estrictamente segregados de los recursos corporativos y bases de datos; únicamente disponen de acceso a Internet mediante la red inalámbrica de invitados (VLAN 60) con aislamiento de clientes (Client Isolation) y ancho de banda restringido."),
        ("List Paragraph", "Infraestructura WAN externa: Los tramos de fibra óptica y equipamiento pertenecientes a las redes metropolitanas de los proveedores ISP (Telefónica y Claro) se consideran cajas negras reguladas por sus respectivos Acuerdos de Nivel de Servicio (SLA)."),
        ("List Paragraph", "Desarrollo aplicativo de software: La arquitectura interna de código del sistema WMS o del ERP Odoo queda fuera del alcance de este diseño de red, circunscribiéndose este documento a su aprovisionamiento, conectividad, aislamiento y entrega segura.")
    ]
    replace_section_content(doc, "3.3 Exclusiones", sec3_3_content)

    # 5. Objetivos del Diseño de Red
    print("Redactando Sección 4: Objetivos del diseño...")
    sec4_content = [
        ("Normal", "De acuerdo con el enfoque por procesos de la norma ISO/IEC 27001:2022 y los requerimientos del perfil de egreso, se definen los siguientes objetivos técnicos medibles para el diseño de red:")
    ]
    replace_section_content(doc, "4. Objetivos del diseño de red", sec4_content)

    table_objetivos_data = [
        ["Segmentar el 100 % del tráfico por zonas", "VLANs y zonas de seguridad documentadas en SSOT", "100 % (18 VLANs)", "Abel Guevara (Redes)"],
        ["Eliminar puntos únicos de fallo en perímetro", "Tiempo de conmutación por falla CARP", "< 3 segundos", "Abel Guevara (Infraestructura)"],
        ["Establecer enlace híbrido seguro y de baja latencia", "Latencia RTT y pérdida de paquetes en túnel WireGuard", "< 40 ms / 0 % pérdidas", "Abel Guevara (Cloud & Red)"],
        ["Aislar interfaces de gestión y bases de datos", "Conexiones no autorizadas a VLAN 70 y VLAN 32", "0 accesos denegados", "Abel Guevara (Ciberseguridad)"],
        ["Implementar capacidades de detección preventiva", "Cobertura de inspección IDS/IPS y Honeypot perimetral", "100 % zonas críticas", "Abel Guevara (SOC / Seguridad)"]
    ]
    populate_table(doc.tables[2], table_objetivos_data)

    # 6. Topologías de Red (Diseño)
    print("Redactando Sección 5: Topologías de red...")
    sec5_intro = [
        ("Normal", "El diseño de red de Co-Logistic S.A.C. se fundamenta en un modelo jerárquico de tres capas (Núcleo, Distribución y Acceso) siguiendo las mejores prácticas de la arquitectura Enterprise Campus de Cisco, combinado con una segmentación estricta por zonas de seguridad según el principio Zero-Trust y la norma ISO/IEC 27002:2022 (control 8.22). A continuación se presentan las vistas especializadas del diseño.")
    ]
    replace_section_content(doc, "5. Topologías de red (diseño)", sec5_intro)

    sec5_1_content = [
        ("Normal", "La topología física general comprende la acometida de doble enlace WAN hacia el router de frontera Cisco C1111-4P, el cual entrega conectividad mediante enlaces troncales dedicados a los firewalls perimetrales pfSense (FW-CORE-01 y FW-CORE-02). Estos operan en alta disponibilidad con el protocolo CARP, conmutando el tráfico hacia el switch core redundante (SW1-CORE1 y SW2-CORE2) interconectados mediante EtherChannel / LACP a 10 Gbps. Desde el núcleo se extienden enlaces hacia los switches de distribución (SW3-DIST1 y SW4-DIST2) y switches Top-of-Rack (SW6-TOR2 y SW7-TOR1) en el centro de datos local.")
    ]
    replace_section_content(doc, "5.1 Topología general de infraestructura de red", sec5_1_content)

    diag_5_1 = """[ FIGURA 5.1: TOPOLOGÍA GENERAL DE INFRAESTRUCTURA DE RED — CO-LOGISTIC S.A.C. ]
                           +------------------------+
                           |     INTERNET / WAN     |
                           +-----------+------------+
                                       |
                   +-------------------+-------------------+
                   | (Fibra Óptica Dedicada)               | (Enlace Respaldo)
        +----------v-----------+               +-----------v----------+
        | ISP1: Telefónica     |               | ISP2: Claro Telecom  |
        +----------+-----------+               +-----------+----------+
                   |                                       |
                   +-------------------+-------------------+
                                       |
                         +-------------v--------------+
                         | Router Cisco C1111-4P      | (NAT / Borde WAN)
                         | Gi0/0/0: 168.121.48.246/26 |
                         +------+--------------+------+
                                |              |
        (VLAN 901/903 /30)      |              |      (VLAN 902/904 /30)
                 +--------------+              +--------------+
                 |                                            |
    +------------v------------+                  +------------v------------+
    | FW-CORE-01 (pfSense)    |<================>| FW-CORE-02 (pfSense)    |
    | Appliance Activo        |  VLAN 100 (Sync) | Appliance Standby       |
    | 10.10.x.2 (Master CARP) |   10.10.100.0/29 | 10.10.x.3 (Backup CARP) |
    +------------+------------+                  +------------+------------+
                 |                                            |
                 +---------------------+----------------------+
                                       | (Trunk 802.1Q - VIPs: 10.10.x.1)
                 +---------------------+----------------------+
                 |                                            |
    +------------v------------+                  +------------v------------+
    | SW1-CORE1               |<================>| SW2-CORE2               |
    | Cisco Catalyst 3850 10G |   LACP Trunk     | Cisco Catalyst 3850 10G |
    | IP Gestión: 10.10.70.11 |   (PortChannel)  | IP Gestión: 10.10.70.12 |
    +----+---------------+----+                  +----+---------------+----+
         |               |                            |               |
         |         +-----+----------------------------+-----+         |
         |         |                                        |         |
    +----v---------v----+                              +----v---------v----+
    | SW3-DIST1         |                              | SW4-DIST2         |
    | Cisco 2960X       |                              | Cisco 2960X       |
    | Nave Logística    |                              | Oficinas Admin    |
    | IP: 10.10.70.13   |                              | IP: 10.10.70.14   |
    +----+---------+----+                              +----+---------+----+
         |         |                                        |         |
    +----v----+ +--v-------+                           +----v----+ +--v-------+
    | AP-WIFI | | SW5-ACC  |                           | Telefon.| | Puestos  |
    | Ind. 90 | | Balanzas |                           | VoIP 50 | | Admin 10 |
    +---------+ +----------+                           +---------+ +----------+"""
    update_diagram_box(doc.tables[3], diag_5_1)

    # 5.2 Topología Lógica: VLANs y Subredes
    sec5_2_content = [
        ("Normal", "La segmentación lógica adopta el bloque IPv4 privado 10.10.0.0/16 asignado institucionalmente a la sede Juliaca. Se han diseñado 18 VLANs organizadas por criticidad, tipo de servicio y vector de riesgo. Cada subred cuenta con una Puerta de Enlace Virtual redundante (Virtual IP CARP) alojada en los firewalls pfSense, asegurando tolerancia total a fallos físicos sin necesidad de reconfigurar los clientes:")
    ]
    replace_section_content(doc, "5.2 Topología lógica de red — VLAN y subredes", sec5_2_content)

    table_vlans_data = [
        ["10", "ADMINISTRACION", "10.10.10.0/24", "Estaciones de trabajo de gerencia, contabilidad y RRHH"],
        ["20", "OPERACIONES_WMS", "10.10.20.0/23", "Terminales de almacén, pistolas RF Zebra, puestos de picking"],
        ["30", "INFRAESTRUCTURA", "10.10.30.0/24", "Servicios core: FreeIPA, DNS/DHCP, NTP, Step-CA, apt-cacher"],
        ["31", "APLICACIONES", "10.10.31.0/24", "Servidores de aplicación WMS Web Nginx, API REST y ERP Odoo"],
        ["32", "BASE_DATOS", "10.10.32.0/24", "Cluster de base de datos transaccional PostgreSQL 16 HA"],
        ["33", "DATA_WAREHOUSE", "10.10.33.0/24", "Servidor analítico PostgreSQL DW y plataforma Metabase BI"],
        ["34", "MONITOREO_SEGURIDAD", "10.10.34.0/24", "Servidores SIEM Wazuh, Zabbix Server, OpenVAS e ITSM GLPI"],
        ["35", "COMUNICACIONES", "10.10.35.0/24", "Central IP PBX Asterisk y relé de correo SMTP autenticado"],
        ["40", "CCTV", "10.10.40.0/23", "Videovigilancia: 32 cámaras IP RTSP y grabador digital NVR (D02)"],
        ["50", "VOZ_IP", "10.10.50.0/24", "Teléfonos IP físicos de escritorio en oficinas y almacén"],
        ["60", "INVITADOS_WIFI", "10.10.60.0/24", "Acceso a Internet para visitantes (aislado 100 % de la LAN)"],
        ["70", "GESTION_TI", "10.10.70.0/24", "Red de administración fuera de banda: Proxmox, switches, Guacamole"],
        ["80", "DMZ", "10.10.80.0/24", "Servicios públicos: Proxy WAF Nginx inverso y servidor SFTP B2B"],
        ["90", "WIFI_INDUSTRIAL", "10.10.90.0/23", "Access points industriales de alta densidad en nave logística"],
        ["100", "HA_SYNC", "10.10.100.0/29", "Enlace directo punto a punto para sincronización CARP y pfsync"],
        ["110", "IOT_CONTROL_ACCESO", "10.10.110.0/24", "Sensores de almacén, molinetes biométricos y control de puertas"],
        ["120", "BACKUP_STORAGE", "10.10.120.0/24", "Servidor de respaldos Bareos Director y almacenamiento ZFS NAS"],
        ["130", "HONEYPOT", "10.10.130.0/24", "Servidor señuelo trampa (Cowrie/Dionaea) para detección de intrusos"]
    ]
    populate_table(doc.tables[4], table_vlans_data)

    diag_5_2 = """[ FIGURA 5.2: TOPOLOGÍA LÓGICA DE RED — VLANs Y ENRUTAMIENTO pfSense ]
+---------------------------------------------------------------------------------------------------+
| GATEWAY CARP pfSense (VIPs: 10.10.x.1) — Filtrado Stateful e Inspección Suricata                 |
+----+--------+--------+--------+--------+--------+--------+--------+--------+--------+--------+----+
     |        |        |        |        |        |        |        |        |        |        |
     | .10.1  | .20.1  | .30.1  | .31.1  | .32.1  | .34.1  | .70.1  | .80.1  | .120.1 | .130.1 |
+----v---+ +--v-----+ +v-------+ +v-------+ +v-------+ +v-------+ +v-------+ +v-------+ +v-------+ +v-------+
|VLAN 10 | |VLAN 20 | |VLAN 30 | |VLAN 31 | |VLAN 32 | |VLAN 34 | |VLAN 70 | |VLAN 80 | |VLAN 120| |VLAN 130|
|ADMIN   | |OPS WMS | |CORE TI | |WMS APP | |DATA DB | |SOC MON | |GESTION | |DMZ     | |BACKUP  | |HONEYPOT|
|/24     | |/23     | |/24     | |/24     | |/24     | |/24     | |/24     | |/24     | |/24     | |/24     |
|45 PCs  | |60 PFRF | |FreeIPA | |Nginx   | |Postgres| |Wazuh   | |Proxmox | |WAF     | |Bareos  | |Cowrie  |
|Finanzas| |Zebra   | |DNS/NTP | |Docker  | |Master  | |Zabbix  | |Switches| |SFTP    | |ZFS NAS | |Dionaea |
+--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
     |         |          |          |          ^          ^         ^          ^         ^          |
     |         |          |          +----------+----------|---------|----------+         |          |
     |         +----------|---------------------+          |         |                    |          |
     |                    +--------------------------------+         |                    |          |
     +---------------------------------------------------------------+                    |          |
                                (Acceso exclusivo a través de Bastión Guacamole)          |          |
     =====================================================================================+          |
     AISLAMIENTO ESTRICTO: VLAN 130 (Honeypot) y VLAN 60 (Invitados) sin salida a la LAN <-----------+"""
    update_diagram_box(doc.tables[5], diag_5_2)

    # 5.3 Seguridad Perimetral y Zonas
    sec5_3_content = [
        ("Normal", "La arquitectura de seguridad perimetral segmenta la red institucional en 12 zonas funcionales con fronteras de confianza bien delimitadas. Todo el tráfico que atraviesa las fronteras entre zonas es sometido a tres niveles de control: inspección stateful en pfSense (Capa 3 y 4), análisis de firmas y anomalías con Suricata IDS/IPS (Capa 7) y reenvío de registros hacia el SIEM Wazuh.")
    ]
    replace_section_content(doc, "5.3 Diseño de seguridad perimetral y zonas", sec5_3_content)

    diag_5_3 = """[ FIGURA 5.3: TOPOLOGÍA DE SEGURIDAD PERIMETRAL Y ZONAS DE CONFIANZA ]
                                 [ INTERNET / WAN ]
                                         |
                                 +-------v-------+
                                 | Cisco C1111   | (Frontera WAN)
                                 +-------+-------+
                                         |
                         +---------------v---------------+
                         |     FIREWALL pfSense HA       |
                         |  (Stateful Inspection + CARP) |
                         +---------------+---------------+
                                         |
                        +----------------+----------------+
                        |                                 |
              [ INSPECCIÓN INLINE ]             [ ENLACE HÍBRIDO ]
              | Suricata IDS/IPS  |             | WireGuard VPN  |
              +---------+---------+             +--------+-------+
                        |                                |
       +----------------+----------------+      +--------v--------+
       |                |                |      | VPC GCP CHILE   |
+------v------+  +------v------+  +------v----+ | 10.20.0.0/24    |
| ZONA DMZ    |  | ZONA DATOS  |  | ZONA SOC  | | GCP-BORDE       |
| VLAN 80     |  | VLAN 32 DB  |  | VLAN 34   | | Cloud Storage   |
| WAF / SFTP  |  | Postgres HA |  | Wazuh/IDS | +-----------------+
+-------------+  +-------------+  +-----------+
       |                ^                ^
       v                |                |
+-------------+  +------+------+         |
| ZONA LAN    |  | ZONA CORE   |         |
| VLAN 10, 20 |  | VLAN 30, 31 |---------+
| Admin / WMS |  | FreeIPA/App |  (Logs & Telemetría)
+-------------+  +-------------+"""
    update_diagram_box(doc.tables[6], diag_5_3)

    # 5.4 Conectividad VPN Híbrida
    sec5_4_content = [
        ("Normal", "Para satisfacer las necesidades de respaldo inmutable fuera de sede y contingencia operativa ante desastres (DRP), se ha diseñado un túnel VPN sitio a sitio basado en WireGuard que conecta el clúster perimetral pfSense en Juliaca con la VPC de Google Cloud Platform en Santiago de Chile. WireGuard opera en el espacio de kernel de Linux, proporcionando mayor rendimiento y menor sobrecarga de encapsulación que IPsec clásico:")
    ]
    replace_section_content(doc, "5.4 Diseño de conectividad VPN híbrida", sec5_4_content)

    table_vpn_data = [
        ["Red anunciada", "10.10.0.0/16", "10.20.0.0/24"],
        ["Dispositivo de borde", "Cluster pfSense HA (FW-CORE-01/02)", "Instancia Compute Engine (GCP-BORDE)"],
        ["Dirección IP pública", "168.121.48.246 (Router Cisco NAT)", "34.176.121.24 (IP Externa GCP Chile)"],
        ["Interfaz de túnel", "wg0 (10.20.0.18/29)", "wg0 (10.20.0.17/29)"],
        ["Protocolo y Puerto", "UDP puerto 51820", "UDP puerto 51820"],
        ["Criptografía simétrica", "ChaCha20-Poly1305 (256 bits)", "ChaCha20-Poly1305 (256 bits)"],
        ["Intercambio de llaves", "Curva elíptica Curve25519 (ECDH)", "Curva elíptica Curve25519 (ECDH)"],
        ["Función hash y auth", "BLAKE2s", "BLAKE2s"],
        ["Enrutamiento de retorno", "Estático (Next-Hop: 10.20.0.17)", "VPC Route Table (10.10.0.0/16 -> 10.20.0.4)"]
    ]
    populate_table(doc.tables[7], table_vpn_data)

    diag_5_4 = """[ FIGURA 5.4: TOPOLOGÍA DE CONECTIVIDAD VPN HÍBRIDA (WIREGUARD) ]
DATACENTER LOCAL (JULIACA)                               GOOGLE CLOUD PLATFORM (SANTIAGO)
Red Local: 10.10.0.0/16                                  VPC: VPC-COLOGISTIC (10.20.0.0/24)
+-------------------------------+                       +-------------------------------+
| FW-CORE-01 / FW-CORE-02       |                       | GCP-BORDE (Compute Engine)    |
| pfSense HA Cluster            |                       | Debian 12 / WireGuard         |
| IP Pública: 168.121.48.246    |                       | IP Pública: 34.176.121.24     |
| Interfaz: wg0 (10.20.0.18/29) |                       | Interfaz: wg0 (10.20.0.17/29) |
+---------------+---------------+                       +---------------+---------------+
                |                                                       |
                +=================== TÚNEL CIFRADO =====================+
                        Protocolo: UDP 51820 · ChaCha20-Poly1305
                        Intercambio: Curve25519 (ECDH) · Hash: BLAKE2s
                        Latencia: ~38 ms RTT (Fibra Pacífico)
                                        |
+---------------------------------------v---------------------------------------+
| FLUJOS OPERATIVOS A TRAVÉS DEL TÚNEL:                                         |
| 1. BKP01 (10.10.120.11) -> Cloud Storage: Replicación de respaldos Bareos     |
| 2. MGMT01 (10.10.70.5)  -> GCP-BORDE (10.20.0.4): Gestión administrativa SSH  |
| 3. pfSense Monitoreo    -> GCP-BORDE: Verificación de estado keepalive ICMP   |
+-------------------------------------------------------------------------------+"""
    update_diagram_box(doc.tables[8], diag_5_4)

    # 5.5 Flujo de Información
    sec5_5_content = [
        ("Normal", "El diagrama de flujo de información establece las vías de comunicación autorizadas, protocolos, puertos y controles criptográficos entre los diferentes componentes del sistema:")
    ]
    replace_section_content(doc, "5.5 Diagrama de flujo de información planeado", sec5_5_content)

    table_flujos_data = [
        ["Operador Almacén (VLAN 20)", "HTTPS · 443 / WSS · 8443", "WMS Frontend / API Docker (VLAN 31)"],
        ["Servidor WMS (VLAN 31)", "TCP · 5432 (PostgreSQL SSL)", "Base de Datos DB01 (VLAN 32)"],
        ["Estación Admin (VLAN 10)", "HTTPS · 8443 (TLS 1.3)", "Bastión Guacamole MGMT01 (VLAN 70)"],
        ["Bastión MGMT01 (VLAN 70)", "SSH · 22 / HTTPS · 8006", "Hipervisores Proxmox y Switches (VLAN 70)"],
        ["Cliente Externo B2B (Internet)", "HTTPS · 443 / SFTP · 22", "Proxy WAF01 / SFTP01 (VLAN 80 DMZ)"],
        ["Proxy WAF01 (VLAN 80)", "HTTPS · 8443 (Inspeccionado)", "Servidor WMS API (VLAN 31)"],
        ["Servidor Bareos (VLAN 120)", "TCP · 9101-9103 (Cifrado TLS)", "Agentes Bareos en VMs (Todas las VLANs)"],
        ["Servidor Bareos (VLAN 120)", "HTTPS · 443 (Túnel WireGuard)", "GCP Cloud Storage (cologistic-respaldos)"],
        ["Clientes LAN y VMs (Todas)", "UDP · 53 (DNS) / UDP · 123", "Servidor Core INFRA01 (VLAN 30)"],
        ["Servidor SIEM (VLAN 34)", "UDP · 1514 (Wazuh) / UDP · 514", "Agentes en VMs y Syslog Switches"]
    ]
    populate_table(doc.tables[9], table_flujos_data)

    # 5.6 Matriz de Componentes de Red
    sec5_6_content = [
        ("Normal", "La totalidad de los equipos físicos y lógicos de conectividad que componen la infraestructura se consolidan en la siguiente matriz auditable:")
    ]
    replace_section_content(doc, "5.6 Matriz de componentes de red", sec5_6_content)

    table_componentes_data = [
        ["Router-Cisco (C1111-4P)", "168.121.48.246 / 10.255.x.x", "Frontera WAN", "Enrutamiento perimetral, NAT público y terminación ISP", "Crítica"],
        ["FW-CORE-01 (pfSense CE)", "10.10.x.2 (VIP: 10.10.x.1)", "Perímetro / Core", "Firewall stateful activo, router inter-VLAN y CARP master", "Crítica"],
        ["FW-CORE-02 (pfSense CE)", "10.10.x.3 (VIP: 10.10.x.1)", "Perímetro / Core", "Firewall stateful standby, sincronización pfsync/CARP backup", "Crítica"],
        ["SW1-CORE1 (Catalyst 3850)", "10.10.70.11", "Núcleo L2", "Conmutación central de alta velocidad, troncal 10G LACP", "Crítica"],
        ["SW2-CORE2 (Catalyst 3850)", "10.10.70.12", "Núcleo L2", "Conmutación central de alta velocidad redundante (LACP)", "Crítica"],
        ["SW3-DIST1 (Catalyst 2960X)", "10.10.70.13", "Distribución", "Agregación de enlaces de acceso en nave logística", "Alta"],
        ["SW4-DIST2 (Catalyst 2960X)", "10.10.70.14", "Distribución", "Agregación de enlaces de acceso en oficinas administrativas", "Alta"],
        ["SW5-ACCESO (Catalyst 2960)", "10.10.70.15", "Acceso", "Conexión de puestos administrativos y PCs locales", "Media"],
        ["SW6-TOR2 (Catalyst 3650)", "10.10.70.17", "Datacenter ToR", "Switch Top-of-Rack redundante para servidores (Lado B)", "Crítica"],
        ["SW7-TOR1 (Catalyst 3650)", "10.10.70.16", "Datacenter ToR", "Switch Top-of-Rack redundante para servidores (Lado A)", "Crítica"],
        ["GCP-BORDE (Compute Engine)", "34.176.121.24 / 10.20.0.4", "Nube Borde", "Terminación de túnel WireGuard y landing web DRP", "Alta"],
        ["AP-WIFI-01 / AP-WIFI-02", "10.10.70.21 / 10.10.70.22", "Acceso Wi-Fi", "Cobertura inalámbrica industrial en almacén (VLAN 90/60)", "Alta"]
    ]
    populate_table(doc.tables[10], table_componentes_data)

    # 7. Diseño de Conectividad Híbrida
    print("Redactando Sección 6: Conectividad híbrida...")
    sec6_content = [
        ("Normal", "La interconexión híbrida entre la sede Juliaca y Google Cloud Platform opera mediante el protocolo WireGuard sobre el puerto UDP 51820. Se ha establecido una configuración de Maximum Transmission Unit (MTU) de 1420 bytes en la interfaz wg0 para prevenir fragmentaciones de paquetes IP sobre el túnel WAN. El enrutamiento hacia la nube en el firewall pfSense se define como una ruta estática para el prefijo 10.20.0.0/24 a través de la IP de túnel del par remoto (10.20.0.17). En la nube, la tabla de rutas de la VPC direcciona el tráfico con destino al datacenter (10.10.0.0/16) utilizando la interfaz de la instancia GCP-BORDE (10.20.0.4) como salto siguiente (next-hop)."),
        ("Normal", "Para validar el comportamiento del enlace híbrido en el Semestre 2, se formula la siguiente matriz de pruebas controladas:")
    ]
    replace_section_content(doc, "6. Diseño de conectividad híbrida", sec6_content)

    table_pruebas_vpn_data = [
        ["Ping ICMP bidireccional entre Datacenter (10.10.30.15) y GCP-BORDE (10.20.0.4)", "PERMITIDO (RTT < 40 ms a través de túnel wg0)"],
        ["Tráfico Bareos Backup: BKP01 (10.10.120.11) a Cloud Storage Bucket (HTTPS)", "PERMITIDO (Tráfico cifrado mediante Service Account)"],
        ["Acceso SSH administrativo: MGMT01 (10.10.70.5) a GCP-BORDE (10.20.0.4:22)", "PERMITIDO (Autenticación exclusiva por llave pública Ed25519)"],
        ["Acceso SSH desde estación de Invitados (10.10.60.50) a GCP-BORDE (10.20.0.4)", "DENEGADO (Bloqueo inmediato por regla de firewall)"],
        ["Acceso Web contingencia: Cliente externo a IP pública GCP (34.176.121.24:80/443)", "PERMITIDO (Servicio web HTTP/HTTPS Nginx activo)"],
        ["Acceso directo desde Internet a IP privada de la VPC (10.20.0.4)", "DENEGADO (Dirección RFC 1918 no enrutable públicamente)"],
        ["Tráfico originado en Honeypot (10.10.130.10) con destino a la nube VPC", "DENEGADO (Aislamiento absoluto de la zona trampa)"],
        ["Sincronización NTP: Instancia Cloud sincroniza con INFRA01 (10.10.30.15:123)", "PERMITIDO (Mantenimiento de reloj unificado en todo el SGSI)"]
    ]
    populate_table(doc.tables[11], table_pruebas_vpn_data)

    # 8. Diseño de Seguridad Perimetral
    print("Redactando Sección 7: Seguridad perimetral...")
    sec7_1_content = [
        ("Normal", "El clúster de seguridad perimetral se basa en dos appliances pfSense Community Edition operando en alta disponibilidad en Capa 2 y 3 mediante Common Address Redundancy Protocol (CARP). Cada subred posee una IP virtual (VIP) que actúa como puerta de enlace predeterminada para los hosts. La sincronización de estados de conexión (pfsync) y de reglas de configuración (XMLRPC sync) se efectúa de manera aislada a través de la VLAN 100 (HA_SYNC) en una red dedicada /29."),
        ("Normal", "La política predeterminada de seguridad es Zero-Trust: denegación explícita por defecto (Default Deny Ingress / Default Deny Egress). Toda comunicación entre VLANs o hacia el exterior requiere una regla permitida explícita basada en el principio de mínimo privilegio (PoLP), registrando todo evento en el SIEM.")
    ]
    replace_section_content(doc, "7.1 Firewall", sec7_1_content)

    sec7_2_content = [
        ("Normal", "La Zona Desmilitarizada (DMZ) se aloja en la VLAN 80 (10.10.80.0/24) y hospeda exclusivamente dos servicios: el servidor proxy inverso WAF Nginx (WAF01, 10.10.80.10) y el servidor de intercambio seguro de archivos B2B (SFTP01, 10.10.80.20)."),
        ("Normal", "Regla de diseño inquebrantable de la DMZ: Ningún nodo situado en la DMZ tiene autorización para originar conexiones hacia la red interna de servidores (VLANs 30 a 35), bases de datos o red de gestión. Únicamente puede responder a peticiones provenientes del exterior o aceptar conexiones originadas desde servidores internos autorizados.")
    ]
    replace_section_content(doc, "7.2 DMZ", sec7_2_content)

    sec7_3_content = [
        ("Normal", "El comportamiento esperado de la segmentación inter-VLAN se formaliza en la siguiente matriz de reglas de tráfico que será validada en el Semestre 2:")
    ]
    replace_section_content(doc, "7.3 Segmentación planeada", sec7_3_content)

    table_seg_data = [
        ["Internet → DMZ (VLAN 80: WAF01)", "PERMITIDO (TCP 80, 443 tras inspección WAF e IDS)"],
        ["Internet → Red LAN / Datacenter interno", "DENEGADO (Bloqueo absoluto por regla por defecto)"],
        ["DMZ (VLAN 80) → Base de Datos (VLAN 32)", "DENEGADO (Acceso directo prohibido; solo vía API en VLAN 31)"],
        ["DMZ (VLAN 80) → Servidores Apps (VLAN 31)", "PERMITIDO RESTRINGIDO (Solo reenvío proxy a puerto 8443)"],
        ["Operaciones WMS (VLAN 20) → Apps WMS (VLAN 31)", "PERMITIDO (Acceso web WMS puerto 443 / API puerto 8443)"],
        ["Operaciones WMS (VLAN 20) → Base de Datos (VLAN 32)", "DENEGADO (Aislamiento de capa de datos; acceso solo vía API)"],
        ["Usuarios Admin (VLAN 10) → Gestión TI (VLAN 70)", "PERMITIDO RESTRINGIDO (Solo acceso web a Guacamole con 2FA)"],
        ["Gestión TI (VLAN 70) → Cualquier VLAN", "PERMITIDO (Administración técnica SSH/HTTPS y monitoreo)"],
        ["Invitados WiFi (VLAN 60) → Red Interna / DMZ", "DENEGADO (Aislamiento total; solo salida NAT a Internet)"],
        ["Honeypot (VLAN 130) → Red Interna / Nube", "DENEGADO (Aislamiento total en celda trampa; cero tráfico saliente)"],
        ["Servidores Core (VLAN 30) → Nube GCP (10.20.0.0/24)", "PERMITIDO (Tráfico cifrado VPN para respaldos y contingencia)"],
        ["Telefonía VoIP (VLAN 50) → Base de Datos / Gestión", "DENEGADO (Voz segregada de datos; solo comunicación con PBX01)"]
    ]
    populate_table(doc.tables[12], table_seg_data)

    # 9. Detección: IDS/IPS y Honeypot
    print("Redactando Sección 8: Detección IDS/IPS...")
    sec8_content = [
        ("Normal", "La estrategia de detección preventiva se formula bajo tres tecnologías complementarias articuladas con el SGSI:"),
        ("List Paragraph", "Sistema de Detección/Prevención de Intrusiones (IDS/IPS) Suricata: Integrado como servicio nativo en los firewalls pfSense. Opera en modo inline (bloqueo activo) en las interfaces WAN y DMZ, y en modo pasivo IDS sobre los troncales de servidores mediante puertos espejo (SPAN). Emplea el conjunto de firmas Emerging Threats (ET Open) con actualización diaria automatizada, orientado a la neutralización de ataques de inyección SQL, ejecución remota de comandos (RCE), escaneos de puertos y explotación de vulnerabilidades web."),
        ("List Paragraph", "Servidor Señuelo Honeypot (HONEY01): Alojado en la VLAN 130 (10.10.130.10), una red trampa estrictamente confinada. Ejecuta Cowrie para emular servicios vulnerables de SSH y Telnet (capturando intentos de autenticación por fuerza bruta, diccionarios y comandos ingresados por intrusos) y Dionaea para la captura de malware a través de puertos SMB, HTTP y FTP."),
        ("List Paragraph", "Sistema SIEM y Detección de Host (Wazuh HIDS): Desplegado en SIEM01 (VLAN 34, 10.10.34.20). Recopila eventos de seguridad de Suricata, logs de sistema de los switches Cisco vía Syslog, y telemetría de integridad de archivos (FIM) proveniente de los agentes Wazuh instalados en cada una de las 22 máquinas virtuales."),
        ("List Paragraph", "Plan de validación para el Semestre 2: En la etapa de implementación se ejecutarán pruebas controladas de intrusión utilizando Nmap (escaneo de puertos SYN y detección de versiones), sqlmap contra el proxy WAF y ataques simulados de diccionario Hydra contra el Honeypot, verificando la generación automática de alertas y activación de reglas de bloqueo en menos de 10 segundos.")
    ]
    replace_section_content(doc, "8. Diseño de detección — IDS/IPS y honeypot", sec8_content)

    # 10. Escalabilidad y Disponibilidad
    print("Redactando Sección 9: Escalabilidad y disponibilidad...")
    sec9_content = [
        ("Normal", "El diseño de red incorpora previsiones estructurales de crecimiento y tolerancia a desastres:"),
        ("List Paragraph", "Capacidad de Direccionamiento: El direccionamiento 10.10.0.0/16 ofrece una reserva de más del 70 % de direcciones libres en las subredes /24 y /23, permitiendo duplicar el número de terminales de radiofrecuencia en almacén (VLAN 20) y agregar nuevos microservicios en el centro de datos sin requerir renumeraciones."),
        ("List Paragraph", "Redundancia Física y Enlaces LACP: La troncal entre los switches de distribución y el núcleo opera con agregación de enlaces 802.3ad (LACP) a 10 Gbps, proporcionando balanceo de carga y tolerancia ante el corte de fibra en cualquier hilo. El protocolo Rapid Per-VLAN Spanning Tree Plus (PVRST+) garantiza tiempos de convergencia de bucle inferiores a 1 segundo."),
        ("List Paragraph", "Resiliencia Perimetral CARP: La conmutación de los firewalls pfSense ocurre de forma transparente en menos de 3 segundos ante una caída de hardware del nodo maestro, manteniendo activas las tablas de estados TCP mediante pfsync."),
        ("List Paragraph", "Modularidad Híbrida: La VPC de Google Cloud se estructura con subredes modulares (/28 y /29), lo que permite incorporar zonas de computación adicionales o expandir el entorno DRP sin impactar la configuración del túnel VPN central.")
    ]
    replace_section_content(doc, "9. Consideraciones de escalabilidad y disponibilidad", sec9_content)

    # 11. Conclusiones y Siguientes Pasos
    print("Redactando Sección 10: Conclusiones...")
    sec10_content = [
        ("Normal", "Conclusiones del diseño de red formulado:"),
        ("List Paragraph", "Se ha establecido una arquitectura de red carrier-grade que supera las deficiencias de la red plana previa, logrando una segmentación estricta en 18 VLANs y 12 zonas de seguridad alineadas a los controles de ISO/IEC 27001:2022."),
        ("List Paragraph", "El diseño elimina puntos únicos de falla mediante la combinación de enrutamiento WAN multihoming en Cisco C1111, clúster perimetral pfSense en alta disponibilidad (CARP) y troncales redundantes LACP a 10 Gbps."),
        ("List Paragraph", "La conectividad híbrida mediante WireGuard garantiza una interconexión costo-eficiente y de baja latencia (~38 ms) con Google Cloud Platform (Santiago de Chile), haciendo viable la política de respaldo inmutable offsite y contingencia DRP."),
        ("List Paragraph", "Hitos completados en Semestre 1: Especificación formal SSOT en código YAML, validación topológica automatizada con 18 pruebas unitarias superadas, y despliegue exitoso verificado en la nube pública de GCP."),
        ("List Paragraph", "Siguientes pasos para el Semestre 2 (Entregable S2_E2): Despliegue de plantillas de configuración en switches físicos Catalyst, configuración del par pfSense en hardware dedicado, ejecución de la matriz de pruebas de conectividad y segmentación, y afinamiento de reglas de detección en Suricata y Wazuh SIEM.")
    ]
    replace_section_content(doc, "10. Conclusiones del diseño y siguientes pasos", sec10_content)

    # 12. Referencias
    print("Redactando Sección 11: Referencias...")
    sec11_content = [
        ("Normal", "[1] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection — Information security management systems — Requirements,\" Geneva, Switzerland, Oct. 2022."),
        ("Normal", "[2] International Organization for Standardization, \"ISO/IEC 27002:2022 Information security, cybersecurity and privacy protection — Information security controls,\" Geneva, Switzerland, Feb. 2022."),
        ("Normal", "[3] Y. Rekhter, B. Moskowitz, D. Karrenberg, G. J. de Groot, and E. Lear, \"Address Allocation for Private Internets,\" RFC 1918, Internet Engineering Task Force (IETF), Feb. 1996."),
        ("Normal", "[4] J. A. Donenfeld, \"WireGuard: Next Generation Kernel Network Tunnel,\" in Proceedings of the Network and Distributed System Security Symposium (NDSS), San Diego, CA, USA, Feb. 2017."),
        ("Normal", "[5] Netgate, \"pfSense Documentation: High Availability with CARP and pfsync,\" Netgate Technical Library, Austin, TX, 2024. [Online]. Disponible: https://docs.netgate.com/pfsense/en/latest/highavailability/"),
        ("Normal", "[6] Cisco Systems, \"Enterprise Campus 3.0 Architecture: High Availability and Security Design Guide,\" Cisco Press, San Jose, CA, 2023."),
        ("Normal", "[7] Google Cloud, \"Virtual Private Cloud (VPC) Network Architecture and Best Practices,\" Google Cloud Architecture Center, Mountain View, CA, 2024. [Online]. Disponible: https://cloud.google.com/vpc/docs/"),
        ("Normal", "[8] Open Information Security Foundation (OISF), \"Suricata User Guide: Inline Mode and Emerging Threats Ruleset,\" Release 7.0, 2024. [Online]. Disponible: https://docs.suricata.io/")
    ]
    replace_section_content(doc, "11. Referencias", sec11_content)

    print(f"Guardando documento final en: {OUTPUT_PATH}")
    doc.save(OUTPUT_PATH)
    print("¡Entregable S1_E1 generado exitosamente!")

if __name__ == "__main__":
    main()
