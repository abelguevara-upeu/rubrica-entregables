#!/usr/bin/env python3
"""
generar_s1_e1.py — Entregable S1_E1: Análisis y Diseño de Red.

Toma la plantilla de la rúbrica y la llena con los datos REALES del diseño (cologistic-infra: especificacion/, reglas de
pfSense y topologia.html). Las tablas salen de datos.py; las figuras, de ../figuras (scripts/capturar_figuras.js).
Solo usa los estilos del documento (sin fuentes, colores ni tamaños manuales).

    python3 scripts/generar_s1_e1.py
"""
import docx

import datos
from comun import cambiar_texto_que_contiene, llenar_tabla, mitad_superior, poner_figura, reemplazar_seccion

RAIZ = datos.Path(__file__).resolve().parents[1]
PLANTILLA = RAIZ / "templates/s1_e1_analisis_y_diseno_de_red_nlcwgpwptr.docx"
SALIDA = RAIZ / "entregables/s1_e1_analisis_y_diseno_de_red.docx"

N = "Normal"
L = "List Paragraph"
NUBE = datos.nube()
TUNEL = NUBE["tuneles"]["wireguard-nube"]
REGLAS = datos.resumen_reglas()
SW = datos.switches()
VM = datos.totales_vm()
N_VLAN = len(datos.vlans())
ZONAS = datos.zonas()
ZONAS_INTERNAS = [z for z in ZONAS.values() if not z["externa"]]


def portada(doc):
    cambiar_texto_que_contiene(doc, "On-Premise", "On-Premise (Proxmox VE sobre KVM) + Cloud (Google Cloud Platform)")
    cambiar_texto_que_contiene(doc, "Preparado por:", "Preparado por: Abel Guevara")
    cambiar_texto_que_contiene(doc, "Organización:", "Organización: Co-Logistic S.A.C.  |  Año: 2026")


def main():
    doc = docx.Document(str(PLANTILLA))
    portada(doc)
    T = list(doc.tables)          # se fijan al inicio: al reemplazar una tabla por una figura, los índices de doc.tables se corren

    # ── 1. Resumen ejecutivo ────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "1. Resumen ejecutivo del diseño de red", [
        (N, "Este informe presenta el diseño de la red de Co-Logistic S.A.C., una empresa de logística con un sistema de gestión de almacenes (WMS) como "
            "servicio central. El diseño reemplaza una red plana por una red segmentada en capas, con un firewall en alta disponibilidad que es el único "
            "punto de paso entre segmentos, un túnel cifrado hacia Google Cloud para los respaldos fuera de sitio y una capa de detección de intrusiones. "
            "Todo el diseño vive como datos en un repositorio (cologistic-nettop-datos); de ahí se generan las configuraciones, las figuras y las tablas "
            "de este documento, de modo que lo dibujado, lo documentado y lo que se configurará en el Semestre 2 no pueden diferir."),
        (N, "Dimensiones del diseño:"),
        (L, f"Topología: tres capas. Núcleo de dos switches Cisco C9300L ({SW['SW1-CORE1']['ip']} y {SW['SW2-CORE2']['ip']}), distribución de dos C9200L, un switch de acceso "
            "y dos switches Top-of-Rack (C1000) que reciben a los cinco servidores. Doce port-channels LACP de dos cables cada uno unen los siete switches. "
            "El núcleo trabaja solo en capa 2: todo el enrutamiento entre VLAN lo hace pfSense (decisión de diseño D01)."),
        (L, "Perímetro: dos firewalls pfSense CE 2.8.1 en hardware dedicado (FW-MAIN y FW-BACKUP), en alta disponibilidad activo-pasivo con CARP, "
            "sincronización de estados (pfsync) y de configuración por la VLAN 100. Cada VLAN tiene una IP virtual compartida (.1) como puerta de enlace."),
        (L, f"Segmentación: {N_VLAN} VLAN de servicio, cuatro VLAN de tránsito hacia los proveedores de Internet (901 a 904) y la VLAN 999 como nativa de los troncales, "
            f"agrupadas en {len(ZONAS_INTERNAS)} zonas internas y 4 externas (Internet y tres redes de la nube). El firewall aplica {REGLAS['total']} reglas "
            f"({REGLAS['pass']} de paso y {REGLAS['block']} de bloqueo explícito) además de la denegación por defecto."),
        (L, f"Conectividad híbrida: túnel WireGuard (UDP 51820) entre los dos pfSense y una VM de borde en la VPC de Google Cloud ({NUBE['vpc']['rango']}, región {NUBE['region']}). "
            "Lo inicia el centro de datos, por lo que no se abre ningún puerto de entrada tras el NAT."),
        (L, "Detección: IDS/IPS en los firewalls, SIEM Wazuh (SIEM01) que recibe los eventos de pfSense, switches y servidores, y un servidor señuelo (HONEY01) en una VLAN propia."),
        (L, "Trazabilidad: cada elemento de las figuras sale del mismo modelo que genera las tablas, de modo que la matriz de componentes cubre el 100 % de lo dibujado."),
    ])
    poner_figura(doc, T[0], "enlace.png")

    # ── 2. Organización ─────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "2.1 Descripción general", [
        (N, "Co-Logistic S.A.C. presta servicios de logística: recepción, custodia, preparación de pedidos y despacho. La operación depende del WMS, una aplicación web "
            "con su API y una base de datos PostgreSQL, que usan tanto las oficinas como los terminales de mano y vehiculares del almacén. Por eso la red debe ser "
            "continua, segmentada y fácil de reconstruir."),
        (N, "El diseño dimensiona la red para 417 dispositivos de usuario y de operación, repartidos así: 70 PC y 10 laptops, 13 impresoras (5 de oficina y 8 de etiquetas), "
            "60 terminales de mano y 12 vehiculares, 60 teléfonos IP, 48 cámaras IP, 12 lectores de acceso y 20 sensores, 12 puntos de acceso y hasta 100 invitados. "
            "Todos tienen un rango DHCP reservado en su subred."),
        (L, "Servicios de TI: 27 máquinas virtuales (22 Linux y 5 Windows) en cinco servidores Proxmox: directorio activo, RADIUS, WMS, bases de datos, respaldo, "
            "SIEM, monitoreo, telefonía, correo, control de acceso y videovigilancia."),
        (L, "Infraestructura local y nube: el procesamiento está en el centro de datos local. La nube de Google aloja únicamente la VM de borde del túnel y el bucket de respaldos "
            "fuera de sitio, que sirve de base para la recuperación ante desastre."),
        (L, "Conectividad a Internet: dos proveedores independientes, cada uno con un enlace hacia cada pfSense (cuatro enlaces en total). En el laboratorio un router Cisco C1111-4P "
            "emula esos cuatro enlaces (VLAN 901 a 904) a partir de una sola salida; en producción cada proveedor llegaría directo a una tarjeta WAN de los firewalls."),
    ])
    reemplazar_seccion(doc, "2.2 Servicios y procesos críticos dependientes de la red", [
        (N, "Cada proceso del negocio se asocia al servicio de TI que lo sostiene y a la criticidad de que la red esté disponible:"),
    ])
    llenar_tabla(T[1], [
        ["Recepción, picking y despacho", "WMS: interfaz web y API (WMS01 activo, WMS02 en espera)", "Crítica"],
        ["Control de stock y ubicaciones", "PostgreSQL con réplica en flujo (DB01 y DB02)", "Crítica"],
        ["Identificación de personas y equipos", "Active Directory y DNS (DC1, DC2); RADIUS (AAA01, AAA02)", "Crítica"],
        ["Intercambio con socios", "Proxy inverso con WAF (WAF01) y SFTP (SFTP01) en la DMZ", "Alta"],
        ["Reportes e inteligencia de negocio", "Almacén de datos y tableros (DW01)", "Media"],
        ["Seguridad patrimonial", "Videovigilancia (NVR01) y control de acceso (ACS01)", "Alta"],
        ["Comunicación operativa", "Central telefónica (PBX01) y relé de correo (MAIL01)", "Media"],
        ["Auditoría y monitoreo de seguridad", "SIEM Wazuh (SIEM01), Zabbix (MON01), escáner de vulnerabilidades (VULN01)", "Alta"],
        ["Continuidad y recuperación", "Respaldo Bareos (BKP01) y bucket en Google Cloud", "Alta"],
    ])
    reemplazar_seccion(doc, "2.3 Partes interesadas relevantes a la red", [
        (N, "Las partes interesadas se identifican según ISO/IEC 27001:2022 (cláusula 4.2) y lo que esperan de la red:"),
        (L, "Clientes y socios logísticos: disponibilidad del inventario y un canal de intercambio de archivos (SFTP y portal) que no exponga el resto de la red."),
        (L, "Personal de almacén y de oficina: acceso estable al WMS, impresión de etiquetas y telefonía, sin ver las bases de datos ni la gestión."),
        (L, "Dirección: continuidad de la operación ante fallas o ransomware, y evidencia para auditorías."),
        (L, "Equipo de TI y seguridad: administración solo desde la VLAN 70 y a través de un bastión, registros centralizados en el SIEM y detección temprana."),
        (L, "Proveedores de Internet y de nube (Google Cloud): interfaces de entrega normalizadas, rangos que no se solapen con 10.10.0.0/16 y reglas de entrada mínimas."),
        (L, "Invitados y visitantes: acceso a Internet sin alcanzar ninguna red interna."),
    ])

    # ── 3. Alcance ──────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "3.1 Declaración de alcance", [
        (N, "El alcance comprende el diseño de las capas 1 a 3 del centro de datos y su conexión a la nube: cableado y equipos de red, VLAN, subredes y direccionamiento IPv4 "
            "dentro de 10.10.0.0/16, enrutamiento y filtrado en el cluster pfSense, el túnel WireGuard hacia Google Cloud y la planificación de la detección de intrusiones. "
            "No incluye la implementación ni la puesta en marcha, que corresponden al Semestre 2."),
    ])
    reemplazar_seccion(doc, "3.2 Límites", [
        (N, "Los límites se definen en tres dimensiones:"),
        (L, "Físicos: un gabinete de 24U (R1) con el router, los siete switches y la sala de servidores contigua con cinco servidores Dell Precision en torre y los dos firewalls, también en torre."),
        (L, "Tecnológicos: switches Cisco Catalyst C9300L, C9200L y C1000; router Cisco C1111-4P; firewalls pfSense CE 2.8.1; hipervisores Proxmox VE; "
            "túnel WireGuard; VPC de Google Cloud con una VM de borde y un bucket."),
        (L, "Organizacionales: la administración de red es del equipo de TI. Se accede únicamente desde la VLAN de gestión, a través del bastión de la VLAN 70."),
    ])
    reemplazar_seccion(doc, "3.3 Exclusiones", [
        (N, "Quedan fuera, con su justificación:"),
        (L, "Dispositivos personales: solo disponen de la red de invitados (VLAN 60), que únicamente sale a Internet."),
        (L, "Redes de los proveedores de Internet y de Google Cloud: son responsabilidad de cada proveedor; el diseño solo define los puntos de entrega."),
        (L, "El código de la aplicación WMS: el documento trata su aprovisionamiento, conectividad y aislamiento, no su desarrollo."),
        (L, "Alta disponibilidad de las máquinas virtuales por almacenamiento compartido: no hay almacenamiento compartido; la redundancia es por servicio (decisión D03) y se describe en el entregable S1_E2."),
    ])

    # ── 4. Objetivos ────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "4. Objetivos del diseño de red", [
        (N, "Objetivos medibles del diseño, con el indicador con que se verificarán en el Semestre 2:"),
    ])
    llenar_tabla(T[2], [
        ["Segmentar la red por zonas de seguridad", "VLAN con subred, puerta de enlace y zona declaradas en el modelo", f"100 % ({N_VLAN} VLAN)", "Redes"],
        ["Eliminar el punto único de falla del perímetro", "Tiempo de conmutación de CARP al apagar FW-MAIN", "Por medir en el Semestre 2", "Infraestructura"],
        ["Cifrar el enlace con la nube", "Túnel WireGuard activo entre ambos pfSense y GCP-BORDE", "Túnel arriba y ping al otro extremo", "Redes"],
        ["Aislar gestión, datos y respaldos de los usuarios", "Reglas de bloqueo explícito de usuarios hacia VLAN 70, 32 y 120", "Intentos bloqueados y registrados", "Ciberseguridad"],
        ["Detectar intrusiones en las zonas críticas", "IDS/IPS sobre WAN, servidores, DMZ y señuelo; alertas en el SIEM", "Cada prueba genera una alerta", "Ciberseguridad"],
    ])

    # ── 5. Topologías ───────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "5. Topologías de red (diseño)", [
        (N, "El diseño sigue un modelo jerárquico de tres capas (núcleo, distribución y acceso), con la segmentación por zonas de la norma ISO/IEC 27002:2022 (control 8.22). "
            "Las cuatro vistas siguientes se generan del mismo modelo: física, lógica, de zonas y de la conexión híbrida."),
    ])
    reemplazar_seccion(doc, "5.1 Topología general de infraestructura de red", [
        (N, "La capa física une, de arriba abajo: la salida a Internet, el router Cisco C1111-4P (emulación del proveedor), los dos firewalls, el núcleo SW1-CORE1 y SW2-CORE2, "
            "la distribución SW3-DIST1 y SW4-DIST2, y los switches SW5-ACCESO, SW6-TOR2 y SW7-TOR1. Cada firewall se conecta a un núcleo por el puerto 23. Todo cable entre "
            "switches es un par de enlaces agrupados con LACP. Los cinco servidores tienen un cable a cada ToR y los unen en un bond active-backup, ya que no hay MLAG entre "
            "los dos ToR. Los puertos se muestran en cada extremo de la figura."),
    ])
    poner_figura(doc, T[3], "fisica.png")

    reemplazar_seccion(doc, "5.2 Topología lógica de red — VLAN y subredes", [
        (N, f"El direccionamiento usa el bloque privado 10.10.0.0/16 (RFC 1918). Las {N_VLAN} VLAN de servicio llevan una subred, una IP virtual CARP como puerta de enlace (.1) y una IP propia de cada "
            "firewall (.2 en FW-MAIN y .3 en FW-BACKUP). La VLAN 100 es solo para la sincronización de los firewalls y no tiene gateway. Las VLAN 901 a 904 (10.255.x.x /30) "
            "son los enlaces de tránsito hacia el router de borde, y la 999 es la nativa de los troncales y de los puertos sin uso. La figura 5.2 muestra cada subred y qué tiene IP en ella."),
    ])
    llenar_tabla(T[4], datos.tabla_vlans())
    poner_figura(doc, T[5], "red.png")

    reemplazar_seccion(doc, "5.3 Diseño de seguridad perimetral y zonas", [
        (N, f"La red se divide en {len(ZONAS_INTERNAS)} zonas internas (usuarios, invitados, operación y dispositivos, servidores, datos, seguridad y monitoreo, respaldo, señuelo, DMZ, gestión, HA y WAN) "
            "y 4 externas (Internet y las tres subredes de la VPC). Todo tráfico entre zonas pasa por pfSense, que filtra con estado y registra en el SIEM. "
            "La única excepción justificada es la VLAN 40: las cámaras y su grabador comparten esa VLAN para no enrutar el video por el firewall (D02); se protege con IP Source Guard y reservas DHCP por MAC. "
            "La figura 5.3 muestra la parte superior de la vista de red: la nube, el router, los enlaces WAN, el cluster de firewalls y las primeras zonas."),
    ])
    poner_figura(doc, T[6], mitad_superior("zonas_completa.png", "zonas.png"))

    reemplazar_seccion(doc, "5.4 Diseño de conectividad VPN híbrida", [
        (N, "Para respaldar fuera de sitio y contar con una base de recuperación, el centro de datos se conecta a Google Cloud con un túnel WireGuard sitio a sitio. "
            "Lo inician los pfSense, de modo que la nube no necesita alcanzar la red local y no se abre ningún puerto de entrada tras el NAT. "
            "Los dos firewalls tienen un extremo del túnel (wg0), de modo que el enlace subsiste si cae uno."),
    ])
    llenar_tabla(T[7], [
        ["Redes anunciadas", "10.10.0.0/16 (todo el centro de datos)", f"{NUBE['vpc']['rango']} (VPC-COLOGISTIC)"],
        ["Dispositivo de borde", "FW-MAIN y FW-BACKUP (pfSense CE)", f"GCP-BORDE (Compute Engine e2-micro, {NUBE['region']})"],
        ["Interfaz y dirección del túnel", f"wg0: {TUNEL['extremos']['FW-MAIN']['ip']} (MAIN) y {TUNEL['extremos']['FW-BACKUP']['ip']} (BACKUP)", f"wg0: {TUNEL['extremos']['GCP-BORDE']['ip']}"],
        ["Subred del túnel", f"NUBE-TUNEL {NUBE['subredes']['NUBE-TUNEL']}", f"NUBE-TUNEL {NUBE['subredes']['NUBE-TUNEL']}"],
        ["Protocolo y puerto", "WireGuard, UDP 51820", "WireGuard, UDP 51820"],
        ["Quién inicia la conexión", "El centro de datos", "Solo responde"],
        ["Cifrado", "ChaCha20-Poly1305", "ChaCha20-Poly1305"],
        ["Intercambio de claves", "Curve25519 (ECDH)", "Curve25519 (ECDH)"],
        ["Ruta hacia la otra red", "10.20.0.0/24 por el túnel", "10.10.0.0/16 por el túnel (ruta de la VPC)"],
    ], encabezado=["Parámetro", "Extremo on-premise", "Extremo nube (Google Cloud)"])
    poner_figura(doc, T[8], "vpn.png", ancho_cm=9.5)

    reemplazar_seccion(doc, "5.5 Diagrama de flujo de información planeado", [
        (N, "Los flujos autorizados salen de las reglas de pfSense (vars/reglas.yml). La tabla recoge los principales, con su protocolo y puerto:"),
    ])
    llenar_tabla(T[9], [
        ["Terminales del almacén (VLAN 20 y 90)", "TCP 443", "WMS (WMS01 y WMS02, VLAN 31)"],
        ["WMS (VLAN 31)", "TCP 5432", "PostgreSQL (DB01 y DB02, VLAN 32)"],
        ["PostgreSQL DB01", "TCP 5432 (replicación en flujo)", "DB02 y almacén de datos DW01 (VLAN 33)"],
        ["Oficinas (VLAN 10)", "TCP 88, 389, 445, 636 y UDP 53", "Active Directory (DC1 y DC2, VLAN 30)"],
        ["Internet (NAT en WAN1 y WAN2)", "TCP 443 y 22", "Proxy WAF01 y SFTP01 (VLAN 80, DMZ)"],
        ["Proxy WAF01 (DMZ)", "TCP 443", "WMS (VLAN 31)"],
        ["Bastión MGMT01 (VLAN 70)", "TCP 22, 443, 3389 y 8006", "Servidores, switches e hipervisores"],
        ["Todas las VLAN", "TCP 1514, 1515 y UDP 514", "SIEM01 (Wazuh, VLAN 34)"],
        ["BKP01 (VLAN 120)", "TCP 9102 y 9103", "Servidores y almacenamiento de respaldo"],
        ["BKP01 (VLAN 120)", "TCP 443 por el túnel WireGuard", f"Bucket {NUBE['respaldo']['bucket_respaldos']}"],
        ["Zabbix MON01 (VLAN 34)", "TCP 10050 y UDP 161 (SNMPv3)", "Servidores, switches e hipervisores"],
    ])

    reemplazar_seccion(doc, "5.6 Matriz de componentes de red", [
        (N, "La matriz cubre todo lo que muestran las figuras: 17 equipos físicos y las dos piezas de la nube. Las máquinas virtuales están en la matriz del entregable S1_E2."),
    ])
    filas = [["Router-Cisco (C1111-4P)", "168.121.48.246 y VLAN 901 a 904", "Borde / WAN", "NAT y emulación de los enlaces de los proveedores", "Crítica"],
             ["FW-MAIN (pfSense CE)", "10.10.70.2 · VIP .1 en cada VLAN", "Perímetro", "Firewall activo, enrutamiento entre VLAN, CARP y túnel WireGuard", "Crítica"],
             ["FW-BACKUP (pfSense CE)", "10.10.70.3 · VIP .1 en cada VLAN", "Perímetro", "Firewall pasivo (CARP); toma el control si cae FW-MAIN", "Crítica"]]
    for n, s in SW.items():
        filas.append([f"{n} ({s['modelo']})", s["ip"], {"core": "Núcleo L2", "distribucion": "Distribución", "acceso": "Acceso", "tor": "ToR de servidores"}[s["rol"]],
                      {"core": "Conmutación central; prioridad STP " + str(s["stp_prioridad"]), "distribucion": "Agregación hacia el núcleo y los ToR",
                       "acceso": "Acceso de usuarios y punto de acceso", "tor": "Conecta los servidores Proxmox (un cable a cada ToR)"}[s["rol"]],
                      "Crítica" if s["rol"] in ("core", "tor") else "Alta"])
    filas += [["AP1-WIFI", "10.10.70.21", "Acceso Wi-Fi", "Cobertura inalámbrica (SSID en las VLAN 60 y 90)", "Media"],
              ["HV-MAIN, HV1, HV2, HV3 y HV4 (Proxmox)", "10.10.70.41 y 10.10.70.44 a .47", "Hipervisores", "Alojan las 27 VM; bond hacia ambos ToR; forman el cluster PVE-COLOGISTIC", "Crítica"],
              ["GCP-BORDE (Compute Engine)", f"{NUBE['recursos']['GCP-BORDE']['interfaces']['nic0']} y wg0 {TUNEL['extremos']['GCP-BORDE']['ip']}", "Nube · borde", "Extremo del túnel WireGuard; aloja la landing de contingencia", "Alta"],
              ["GCP-BUCKET (Cloud Storage)", "Sin IP (API de Cloud Storage)", "Nube", "Copia fuera de sitio de respaldos de PostgreSQL y configuraciones", "Alta"]]
    llenar_tabla(T[10], filas)

    # ── 6. Conectividad híbrida ─────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "6. Diseño de conectividad híbrida", [
        (N, f"La VPC-COLOGISTIC ({NUBE['vpc']['rango']}) tiene tres subredes: NUBE-BORDE ({NUBE['subredes']['NUBE-BORDE']}, pública, con GCP-BORDE), NUBE-TUNEL ({NUBE['subredes']['NUBE-TUNEL']}, privada) y "
            f"NUBE-PRIVADA ({NUBE['subredes']['NUBE-PRIVADA']}, privada, para contingencia). Las rutas son dos: 10.10.0.0/16 por el túnel y 0.0.0.0/0 por Internet. "
            "El firewall de la VPC solo admite UDP 51820 desde la IP pública del centro de datos y SSH desde la VLAN 70. Cuentas de servicio separadas (respaldo, Terraform y registros) "
            "tienen únicamente los permisos de su función."),
        (N, "En los pfSense, la ruta hacia 10.20.0.0/24 apunta al túnel. Las pruebas planeadas para validar este enlace en el Semestre 2 son:"),
    ])
    llenar_tabla(T[11], [
        ["Ping desde FW-MAIN y FW-BACKUP a GCP-BORDE (10.20.0.17)", "Responde por wg0"],
        ["Ping desde un servidor de la VLAN 30 a GCP-BORDE por el túnel", "Permitido por la regla hacia la nube"],
        ["BKP01 (VLAN 120) escribe en el bucket cologistic-respaldos-sa-west1 por HTTPS", "Permitido; la copia llega a Cloud Storage"],
        ["SSH desde MGMT01 (VLAN 70) a GCP-BORDE", "Permitido (regla de la VPC desde 10.10.70.0/24)"],
        ["SSH desde un equipo de la VLAN 10 o 60 a GCP-BORDE", "Denegado (no es VLAN 70)"],
        ["UDP 51820 a GCP-BORDE desde una IP distinta a la del centro de datos", "Descartado por el firewall de la VPC"],
        ["Intento de entrar a 10.20.0.4 desde Internet", "Sin respuesta (IP privada)"],
        ["Apagar FW-MAIN con el túnel activo", "FW-BACKUP retoma el túnel; se registra el tiempo"],
    ], encabezado=["Prueba de conectividad planeada", "Resultado esperado"])

    # ── 7. Seguridad perimetral ─────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "7.1 Firewall", [
        (N, "El perímetro lo forman dos pfSense CE 2.8.1 en equipos dedicados, en alta disponibilidad activo-pasivo con CARP. La IP virtual de cada VLAN actúa como puerta de enlace. "
            "pfsync copia la tabla de conexiones y XMLRPC replica la configuración por la VLAN 100 (10.10.100.0/29), una red exclusiva de los dos firewalls. "
            "FW-MAIN es el maestro (skew 0) y FW-BACKUP el respaldo (skew 100)."),
        (N, f"La política por defecto es denegar todo lo que no se permite. Cada VLAN tiene reglas de paso con origen, destino y puerto concretos, y reglas de bloqueo explícito "
            f"para los destinos sensibles, de modo que el intento quede registrado. En total son {REGLAS['total']} reglas ({REGLAS['pass']} de paso y {REGLAS['block']} de bloqueo). "
            "Los destinos se expresan como alias (servicios, puertos y redes), así que cambiar una máquina de lugar no obliga a reescribir reglas."),
    ])
    reemplazar_seccion(doc, "7.2 DMZ", [
        (N, "La DMZ es la VLAN 80 (10.10.80.0/24) y aloja dos servidores: el proxy inverso con WAF (WAF01, 10.10.80.10) y el SFTP para socios (SFTP01, 10.10.80.20). "
            "Desde Internet solo se publican dos puertos en cada enlace WAN: 443 hacia WAF01 y 22 hacia SFTP01."),
        (N, "Desde la DMZ solo se permite que WAF01 llegue al WMS por el puerto 443 y que ambos servidores usen los servicios comunes (DNS, SIEM, parches, certificados y respaldo). "
            "Las reglas bloquean y registran todo intento hacia la base de datos y hacia la red de gestión."),
    ])
    reemplazar_seccion(doc, "7.3 Segmentación planeada", [
        (N, "La matriz resume lo que permiten y deniegan las reglas por pares de zonas (las del archivo reglas.yml del rol pfsense_base). Cada fila se probará en el Semestre 2:"),
    ])
    llenar_tabla(T[12], [
        ["Internet → DMZ (WAF01 y SFTP01)", "PERMITIDO solo TCP 443 y 22 por NAT"],
        ["Internet → red interna", "DENEGADO (política por defecto)"],
        ["DMZ → base de datos (VLAN 32)", "DENEGADO y registrado"],
        ["DMZ → gestión (VLAN 70)", "DENEGADO y registrado"],
        ["WAF01 (DMZ) → WMS (VLAN 31)", "PERMITIDO solo TCP 443"],
        ["Terminales y oficinas (VLAN 10, 20, 90) → WMS", "PERMITIDO TCP 443"],
        ["Terminales (VLAN 20 y 90) → base de datos (VLAN 32)", "DENEGADO (solo el WMS llega a PostgreSQL)"],
        ["Usuarios → gestión (VLAN 70) y respaldos (VLAN 120)", "DENEGADO"],
        ["Bastión MGMT01 (VLAN 70) → servidores, switches y cámaras", "PERMITIDO por SSH, HTTPS, RDP y 8006"],
        ["Invitados (VLAN 60) → red interna", "DENEGADO; solo sale a Internet por TCP 80 y 443"],
        ["Cámaras (VLAN 40) y dispositivos IoT (VLAN 110) → servidores, gestión y usuarios", "DENEGADO"],
        ["Señuelo (VLAN 130) → red interna", "DENEGADO; solo puede enviar sus alertas al SIEM"],
        ["Servidores y aplicaciones → señuelo (VLAN 130)", "PERMITIDO y registrado (cualquier acceso es una alerta)"],
        ["BKP01 (VLAN 120) → nube", "PERMITIDO TCP 443 por el túnel"],
    ])

    # ── 8. Detección ────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "8. Diseño de detección — IDS/IPS y honeypot", [
        (N, "La detección combina tres elementos y se valida en el Semestre 2:"),
        (L, "IDS/IPS en los firewalls: el paquete IDS/IPS de pfSense inspecciona la WAN y las zonas de servidores, DMZ y señuelo. Se ubica ahí porque todo el tráfico entre zonas pasa por pfSense (D01). "
            "Enviará sus alertas al SIEM. Queda por decidir si se usa Suricata o Snort; la elección no cambia la topología."),
        (L, "Servidor señuelo (HONEY01, VLAN 130, 10.10.130.10): sin uso real. Expone SSH, SMB y HTTP (22, 445 y 80). Cualquier conexión hacia él es una alerta, y desde él no sale tráfico hacia la red interna. "
            "Los servidores y aplicaciones pueden alcanzarlo con registro, para que un equipo comprometido que escanee la red se delate."),
        (L, "SIEM (SIEM01, VLAN 34, 10.10.34.20): Wazuh recibe los agentes (TCP 1514 y 1515) y el syslog (UDP 514) de pfSense, switches e hipervisores. Correlaciona las alertas del IDS y del señuelo."),
        (L, "Complementos: Zabbix (MON01) vigila disponibilidad por SNMPv3 y agentes; VULN01 (Greenbone) escanea vulnerabilidades en servidores, switches e hipervisores; Oxidized (ITSM01) guarda cada cambio de configuración de los switches."),
        (L, "Validación en el Semestre 2: escaneo de puertos (Nmap) desde un equipo de la VLAN 10 hacia servidores, intento de conexión al señuelo y ataque web contra WAF01, y verificar que cada prueba produce una alerta en SIEM01."),
    ])

    # ── 9. Escalabilidad y disponibilidad ───────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "9. Consideraciones de escalabilidad y disponibilidad", [
        (N, "El diseño prevé crecimiento y fallas:"),
        (L, "Direccionamiento: de los 10.10.0.0/16 se usan 18 subredes /23, /24 y /29; queda espacio para nuevas VLAN. Las subredes de usuarios y dispositivos tienen un rango DHCP reservado y "
            "holgura sobre el número de equipos dimensionado."),
        (L, "Capa 2: doce port-channels LACP de dos cables unen los switches y los servidores tienen un cable a cada ToR en un bond active-backup. Rapid-PVST con raíz fijada en SW2-CORE2 (prioridad 4096) "
            "y SW1-CORE1 como respaldo (8192); distribución en 16384 y los demás en 32768, para que un switch de acceso nunca sea raíz."),
        (L, "Perímetro: pares de firewalls con CARP y pfsync; dos proveedores de Internet con enlace de conmutación entre ambos en pfSense (el ISP2 toma el relevo cuando el ISP1 falla)."),
        (L, "Nube: la VPC tiene subredes separadas para el borde, el túnel y la carga privada, lo que permite agregar recursos de contingencia sin tocar el túnel."),
        (L, "Límite conocido: el cluster Proxmox no tiene almacenamiento compartido; las VM no se reinician solas en otro nodo. La redundancia está en los servicios, cada par en hipervisores distintos (D03)."),
    ])

    # ── 10. Conclusiones ────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "10. Conclusiones del diseño y siguientes pasos", [
        (N, "Conclusiones:"),
        (L, f"Se diseñó una red jerárquica segmentada en {N_VLAN} VLAN y {len(ZONAS_INTERNAS)} zonas internas, con un único punto de enrutamiento y filtrado (pfSense en alta disponibilidad)."),
        (L, "La conexión híbrida por WireGuard hacia Google Cloud permite respaldar fuera de sitio sin abrir puertos de entrada en el centro de datos."),
        (L, "La detección (IDS/IPS, SIEM y señuelo) está ubicada donde pasa el tráfico entre zonas, y cada elemento tiene una prueba planeada."),
        (L, "Todo el diseño está en un repositorio y se valida automáticamente; las figuras y tablas de este informe se generan de él."),
        (N, "Siguientes pasos (Semestre 2): configurar los switches (Day-0 y Ansible), instalar Proxmox y formar el cluster, desplegar pfSense con CARP, levantar el túnel y ejecutar las matrices de pruebas de las secciones 6 y 7.3."),
    ])

    # ── 11. Referencias ─────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "11. Referencias", [
        (N, "[1] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security, cybersecurity and privacy protection — Information security management systems — Requirements,\" Geneva, 2022."),
        (N, "[2] International Organization for Standardization, \"ISO/IEC 27002:2022 Information security controls,\" Geneva, 2022."),
        (N, "[3] Y. Rekhter et al., \"Address Allocation for Private Internets,\" RFC 1918, IETF, Feb. 1996."),
        (N, "[4] J. A. Donenfeld, \"WireGuard: Next Generation Kernel Network Tunnel,\" in Proc. NDSS, San Diego, CA, USA, 2017."),
        (N, "[5] Netgate, \"pfSense Documentation: High Availability,\" Netgate Docs. [Online]. Disponible: https://docs.netgate.com/pfsense/en/latest/highavailability/"),
        (N, "[6] Cisco Systems, \"Catalyst 9300 Series Switches Configuration Guides,\" Cisco. [Online]. Disponible: https://www.cisco.com/"),
        (N, "[7] Google Cloud, \"VPC network overview,\" Google Cloud Documentation. [Online]. Disponible: https://cloud.google.com/vpc/docs/overview"),
        (N, "[8] Wazuh Inc., \"Wazuh Documentation,\" 2024. [Online]. Disponible: https://documentation.wazuh.com/"),
    ])

    SALIDA.parent.mkdir(exist_ok=True)
    doc.save(str(SALIDA))
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
