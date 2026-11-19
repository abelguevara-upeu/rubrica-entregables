"""
generar_s2_e2.py — Contenido del entregable S2_E2: Implementación, Testing y Monitoreo de Red.

Describe lo que el repositorio cologistic-infra implementa (roles de Ansible, estado de Terraform, commits), las reglas de pfSense reales
y los resultados verificados en el laboratorio registrados en pruebas_datos.RESULTADOS_PRUEBAS_RED.
"""
import datos
import pruebas_datos as pd
from redactor import Redactor

NUBE = datos.nube()
REGLAS = datos.resumen_reglas()
RESULTADOS = getattr(pd, "RESULTADOS_PRUEBAS_RED", {})


def conteo_pruebas():
    estados = [RESULTADOS.get(t[0], ("", "", "Pendiente"))[2] for t in pd.PRUEBAS_RED]
    return {
        "aprobadas": estados.count("Aprobada"),
        "bloqueadas": estados.count("Bloqueada"),
        "pendientes": estados.count("Pendiente"),
        "fallidas": estados.count("Fallida"),
    }


def reglas_por_zona():
    filas = []
    for interfaz, reglas in datos.reglas_por_interfaz().items():
        paso = sum(x["action"] == "pass" for x in reglas)
        bloqueo = sum(x["action"] == "block" for x in reglas)
        filas.append([interfaz, str(paso), str(bloqueo), str(len(reglas))])
    return filas


def contenido():
    r = Redactor()
    c = conteo_pruebas()

    # ── 1 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Resumen ejecutivo")
    r.p("Este informe documenta cómo se implementó la red diseñada en el entregable S1_E1: la configuración de los switches y el router, el firewall pfSense con sus zonas y reglas, el túnel hacia Google Cloud, "
        "la detección (señuelo, SIEM e IDS Suricata) y el monitoreo. También incluye la ejecución en laboratorio del plan de pruebas de permitido y denegado.")
    r.p("El informe distingue tres estados reales observados: «Implementado» (verificado en ejecución en el laboratorio), «Parcial» (desplegado con pendiente operativo puntual) y "
        "«Pendiente / Bloqueada» (no completado o restringido por entorno).")
    r.tabla(["Componente", "Estado", "Evidencia"], [
        ["Switches Cisco (7) con VLAN, STP, port-channels y puertos sin uso", "Implementado", "Roles cisco_switching; tablero de laboratorio; docs/switches.md"],
        ["Router Cisco C1111-4P (borde, NAT, VLAN 901 a 904)", "Implementado", "Rol cisco_edge; verificado en el equipo"],
        ["Firewall pfSense: sistema, VLAN, WAN, CARP HA, alias, NAT, reglas, DHCP y registros", "Implementado", f"FW-MAIN/FW-BACKUP activos ({REGLAS['total']} reglas); CARP failover/failback verificado (T22)"],
        ["VPC de Google Cloud, GCP-BORDE, firewall, ruta, buckets, GCP-WMS-DRP, Artifact Registry, Secret Manager, Cloud DNS y alerta", "Implementado", "gcp-borde y gcp-wms-drp desplegados; DRP Cloud validado (T30) y alerta Cloud Monitoring habilitada (T28)"],
        ["Túnel WireGuard: extremo en la nube", "Implementado", "VM de borde con WireGuard + Tailscale Subnet Router (10.20.0.0/24)"],
        ["Túnel WireGuard y Tailscale: extremo en pfSense", "Implementado", "wg0 (10.20.0.17) y Tailscale Subnet Router (10.10.0.0/16) verificados en vivo (T01-T05, T30)"],
        ["Señuelo OpenCanary (HONEY01)", "Implementado", "HTTP 80, SMB 445 y FTP 21 activos; eventos JSON recibidos y alertados en SIEM01 (T23)"],
        ["SIEM Wazuh (SIEM01) y syslog remoto", "Implementado", "Wazuh 4.9.2 recibiendo UDP 514; reglas activas para OpenCanary (100100), filterlog (100110) y Suricata (100120)"],
        ["Monitoreo Zabbix (MON01)", "Parcial", "4 contenedores Docker arriba en MON01 y regla 161/udp; falta alta de switches y respuesta SNMP (T27)"],
        ["IDS/IPS Suricata en pfSense", "Implementado", "pfSense-pkg-suricata 7.0.10 (Suricata 8.0.7) activo en em0.31; SID 9000001 probado hacia SIEM01 (H05 cerrado, T24)"],
        [f"Pruebas de permitido y denegado ({len(pd.PRUEBAS_RED)} casos)", "Ejecutado en laboratorio", f"{c['aprobadas']} Aprobadas, {c['bloqueadas']} Bloqueada (H02) y {c['pendientes']} Pendientes (T26-T28)"],
    ])

    # ── 2 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Trazabilidad con el diseño de red (Semestre 1)")
    r.p("Cada elemento del diseño del entregable S1_E1 se compara con lo implementado. Los cambios están justificados.")
    r.tabla(["Elemento del diseño", "Lo implementado", "Cambio y justificación"], [
        ["Siete switches en tres capas, con 12 port-channels LACP", "Igual", "Ninguno."],
        ["Núcleo solo en capa 2; pfSense enruta entre VLAN (D01)", "Igual", "Ninguno."],
        ["18 VLAN de servicio, 4 de tránsito y la 999", "Igual: VLAN creadas en los switches y en pfSense", "Ninguno."],
        ["Router de borde con dos proveedores de Internet", "Router Cisco C1111-4P que emula los cuatro enlaces", "El laboratorio tiene una sola salida; en producción cada proveedor llegaría a los firewalls (decisión D09)."],
        ["Red de gestión en la VLAN 70 sin red fuera de banda", "Igual", "Ninguno; se retiró la red de laboratorio con el Router Cisco como alternativa."],
        ["Cluster Proxmox de cinco nodos", "Igual, con renombrado de nodos (HV-MAIN y HV1 a HV4)", "Decisión D15, para distinguir el servidor de respaldo."],
        ["Señuelo con SSH, SMB y HTTP", "OpenCanary con HTTP 80, SMB 445 y FTP 21; alertas JSON enviadas por syslog 514 a SIEM01", "Verificado en vivo mediante intento FTP y regla Wazuh 100100 (T23); el SSH real permanece accesible solo por bastión."],
        ["Túnel entre pfSense y GCP-BORDE", "WireGuard wg0 + Tailscale Subnet Router operando en pfSense y gcp-borde", "Verificado en hardware real (T01-T05, T30); además provee contingencia directa 10.20.0.0/24 si caen los routers locales."],
        ["Exposición pública del WMS vía WAF01", "WMS privado (Intranet + Tailscale); WAF01 devuelve 403", "Decisión D19: sin NAT 443 público al WMS; WAF01 queda aislado para futuros portales externos (T07, T12)."],
        ["Firewall de la VPC: UDP 51820 solo desde la IP del centro de datos", "UDP 51820 permitido desde 0.0.0.0/0", "Desviación abierta (hallazgo H02 del SGSI, T06 Bloqueada): se restringirá cuando se cuente con IP pública fija."],
        ["IDS/IPS en pfSense", "Suricata 8.0.7 (pfSense-pkg-suricata 7.0.10) activo en em0.31 en modo IDS", "Hallazgo H05 cerrado; alertas EVE JSON por syslog enviadas a SIEM01 y validadas en T24."],
        ["VPC con tres subredes", "Igual: NUBE-BORDE, NUBE-TUNEL y NUBE-PRIVADA", "NUBE-PRIVADA se agregó el 3 de noviembre para la recuperación ante desastre."],
        ["Nombres de buckets cologistic-respaldos-sa-west1", "cologistic-respaldos-cologistic-cloud y cologistic-tfstate-cologistic-cloud", "Los nombres de bucket son únicos en todo Google Cloud; se usó el identificador del proyecto."],
    ])

    # ── 3 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conectividad híbrida implementada: VPN y enrutamiento")
    r.h2("Lado Google Cloud")
    r.p("La etapa 50 de Terraform define la VPC vpc-cologistic, la puerta de borde gcp-borde (34.176.121.24), el nodo privado gcp-wms-drp (TERMINATED en standby) y los servicios nativos de contingencia y CI/CD:")
    r.tabla(["Recurso", "Configuración"], [
        ["VPC y subredes", "vpc-cologistic 10.20.0.0/24; nube-borde 10.20.0.0/28, nube-tunel 10.20.0.16/29 y nube-privada 10.20.0.32/28 (con acceso privado a las API de Google)"],
        ["Gateway de borde", "gcp-borde, e2-micro en southamerica-west1-a, IP interna 10.20.0.4, IP pública estática 34.176.121.24; ejecuta WireGuard, Tailscale Subnet Router (10.20.0.0/24) y proxy TLS"],
        ["Nodo privado DRP", "gcp-wms-drp, e2-medium en NUBE-PRIVADA (10.20.0.34), sin IP pública, desired_status = TERMINATED ($0 cómputo standby); Docker WMS + BI + Postgres"],
        ["Servicios gestionados GCP", "Artifact Registry (wms-repo CI/CD), Secret Manager (wms-drp-env), Cloud DNS privada (cologistic.net.) y Cloud Logging (sa-logs)"],
        ["Ruta", "ruta-a-datacenter: 10.10.0.0/16 con salto en gcp-borde"],
        ["Firewall", "fw-permitir-wireguard (UDP 51820); fw-permitir-trafico-tunel (10.10.0.0/16); fw-permitir-ssh-seguro (TCP 22 desde 10.10.70.0/24 e IAP); fw-permitir-web-contingencia (TCP 80 y 443); fw-permitir-drp-privado (hacia gcp-wms-drp)"],
        ["Almacenamiento", "Bucket de respaldos horarios (versionado y eliminación a los 90 días) y bucket del estado de Terraform (versionado), ambos con acceso uniforme"],
        ["Identidades", "Cuentas de servicio sa-respaldo, sa-terraform y sa-logs (con roles/logging.logWriter)"],
        ["Monitoreo", "Alerta de CPU de GCP-BORDE mayor al 85 % durante 5 minutos, con canal de notificación por correo"],
    ])
    r.h2("Lado pfSense")
    r.p("Ambos accesos híbridos están desplegados y validados en FW-MAIN (10.10.70.2): WireGuard wg0 (10.20.0.17/18/19, peer 34.176.121.24:51820 según nube_tunel.yml) "
        "y Tailscale Subnet Router (10.10.0.0/16 según acceso_remoto.yml). Las pruebas en vivo confirmaron túnel cifrado UDP 51820, enrutamiento hacia 10.20.0.4, acceso SSH solo desde VLAN 70 y contingencia DRP (T01-T05, T30).")
    r.fig("vpn.png", "Figura 3.1 — Conexión híbrida: firewalls, router y VPC de Google Cloud con el túnel WireGuard", ancho_cm=9.5)
    r.h2("Enrutamiento")
    r.bullets(
        "Del centro de datos a la nube: ruta estática hacia 10.20.0.0/24 por la interfaz wg0 de pfSense (verificado desde INFRA01 en T02).",
        "De la nube al centro de datos: la ruta ruta-a-datacenter de la VPC envía 10.10.0.0/16 a GCP-BORDE, que reenvía por wg0.",
        "Cifrado: WireGuard usa ChaCha20-Poly1305 y Curve25519; la captura tcpdump en igb0 (T03) comprobó únicamente tráfico UDP 51820 cifrado.")

    # ── 4 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Seguridad perimetral implementada: firewall, DMZ y segmentación")
    r.h2("Firewall pfSense")
    r.p("El rol pfsense_base configura los dos firewalls en 10 pasos, cada uno con su playbook y su objetivo de make:")
    r.tabla(["Paso", "Qué configura"], [
        ["Sistema", "Configuración base del firewall"],
        ["VLAN", "Una interfaz por VLAN sobre la NIC troncal"],
        ["WAN", "Los dos enlaces de proveedor, con conmutación por falla del ISP1 al ISP2"],
        ["Alta disponibilidad", "IP virtual CARP (.1) en cada VLAN y sincronización pfsync y XMLRPC por la VLAN 100"],
        ["Alias", "Servicios, puertos y redes (por ejemplo SRV_WMS, PTO_AD y NET_SERVIDORES)"],
        ["NAT", "Publicación del puerto 22 hacia SFTP01 en ambos enlaces; NAT 443 hacia WMS eliminado (estado absent; servicio privado)"],
        ["Reglas", f"{REGLAS['total']} reglas por interfaz (incluye VIPs HA .31.10/.32.10/.33.10, etcd 2379-2380 y rsync 873)"],
        ["DHCP", "Retransmisión del DHCP de las VLAN de usuarios hacia los controladores de dominio"],
        ["Registros", "Envío de syslog a SIEM01 (10.10.34.20) desde la VLAN de gestión"],
        ["Acceso remoto", "VPN administrativa de acceso a la VLAN 70"],
    ])
    r.p(f"La política es la mínima necesaria: se deniega por defecto y cada interfaz tiene reglas de paso con origen, destino y puerto concretos, más reglas de bloqueo explícito para los destinos sensibles. "
        f"En total son {REGLAS['total']} reglas, {REGLAS['pass']} de paso y {REGLAS['block']} de bloqueo. Cada regla tiene una descripción que explica su propósito.")
    r.h2("Segmentación por zonas")
    r.tabla(["Interfaz (VLAN)", "Reglas de paso", "Reglas de bloqueo", "Total"], reglas_por_zona())
    r.fig("zonas.png", "Figura 4.1 — Parte superior de la vista de red: nube, router, enlaces de proveedor, firewalls y primeras zonas")
    r.h2("DMZ")
    r.p("La DMZ es la VLAN 80, con WAF01 y SFTP01 (SFTP enjaulado por socio). Por decisión arquitectónica D19, el sistema WMS es 100 % privado (Intranet + VPN Tailscale vía VIP 10.10.31.10), "
        "por lo que desde Internet solo se publica TCP 22 hacia SFTP01; WAF01 devuelve HTTP 403 ante tráfico externo al WMS y las reglas DMZ → SRV_WMS, VLAN 32 y VLAN 70 están bloqueadas y registradas.")

    # ── 5 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("IDS/IPS, honeypot y detección implementados")
    r.h2("Señuelo (HONEY01)")
    r.p("HONEY01 (VLAN 130, 10.10.130.10) ejecuta OpenCanary con HTTP (puerto 80, cabecera Apache), SMB (445) y FTP (21) activos, y reenvía eventos JSON por syslog UDP 514 a SIEM01. "
        "Las reglas de pfSense bloquean y registran cualquier intento saliente del señuelo hacia subredes internas salvo el envío de alertas al SIEM y puertos de gestión/agentes. "
        "Un intento de autenticación FTP desde INFRA01 (10.10.30.15) generó en SIEM01 la alerta Wazuh 100100 (nivel 10, T23).")
    r.h2("IDS/IPS (Suricata en pfSense)")
    r.p("El paquete pfSense-pkg-suricata 7.0.10 (motor Suricata 8.0.7) está instalado y activo en modo IDS sobre la interfaz opt5 (em0.31, APLICACIONES), "
        "enviando alertas EVE JSON por syslog UDP 514 hacia SIEM01. Con esto se cierra el hallazgo H05. El barrido TCP de 20 puertos hacia 10.10.31.11 disparó la firma SID 9000001 "
        "y generó la alerta correlacionada 100120 (nivel 8) en SIEM01 (prueba T24).")
    r.h2("SIEM (Wazuh)")
    r.p("SIEM01 (10.10.34.20) ejecuta Wazuh 4.9.2 (Manager, Indexer y Dashboard) recibiendo syslog remoto en UDP 514 de pfSense, Suricata y OpenCanary, "
        "con decodificadores locales (local_decoder.xml) y reglas activas 100100 (OpenCanary), 100110 (bloqueos filterlog de pfSense), 100120 (Suricata IDS) y 100200-100202 (enlaces Cisco).")

    # ── 6 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Monitoreo, registros y visibilidad de red")
    r.tabla(["Componente", "Qué hace", "Estado"], [
        ["Wazuh (SIEM01)", "Centraliza syslog (UDP 514) y agentes; correlación OpenCanary (100100), filterlog (100110) y Suricata (100120)", "Implementado"],
        ["Syslog de pfSense", "Envía eventos filterlog y sistema desde FW-MAIN/FW-BACKUP a 10.10.34.20:514", "Implementado (T25)"],
        ["IDS Suricata (FW-MAIN)", "Inspección de tráfico en em0.31 y envío EVE JSON por syslog a SIEM01", "Implementado (H05 / T24)"],
        ["Syslog de los switches", "Envía eventos de enlaces/puertos hacia SIEM01 (reglas 100200-100202 ya cargadas)", "Pendiente en equipos (H08 / T26)"],
        ["Zabbix (MON01)", "Docker stack activo en 10.10.34.10 y regla pfSense 161/udp; falta alta de switches y respuesta SNMP", "Parcial (T27 pendiente)"],
        ["Oxidized (ITSM01)", "Guarda cada cambio de configuración de los switches", "Automatizado"],
        ["Cloud Monitoring (nube)", "Alerta de CPU de GCP-BORDE (> 85 % por 5 min) verificada habilitada vía API", "Habilitado (falta stress live T28)"],
    ])
    r.p("Pendiente operativo puntual: finalizar la carga de switches SW1-CORE1 por SNMPv3 en Zabbix (T27), validar el envío de syslog desde los switches (H08 / T26) y ejecutar la carga stress de 6 minutos en GCP-BORDE (T28).")

    # ── 7 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Plan y resultados de pruebas técnicas")
    r.p(f"El plan tiene {len(pd.PRUEBAS_RED)} casos, positivos (debe pasar) y negativos (debe bloquearse o detectarse). En la ejecución en laboratorio se obtuvieron "
        f"{c['aprobadas']} casos Aprobados, {c['bloqueadas']} Bloqueado por el entorno (H02: IP WAN dinámica en GCP) y {c['pendientes']} Pendientes (T26-T28). "
        "El archivo Excel «S2_E2_plan_y_resultados_de_pruebas.xlsx» conserva el detalle completo con resultado obtenido, evidencia y estado.")
    r.tabla(["ID", "Objetivo", "Pasos", "Resultado esperado", "Obtenido", "Estado"],
            [[t[0], f"{t[1]} ({t[5]})", t[3], t[4], RESULTADOS.get(t[0], ("—", "", "Pendiente"))[0], RESULTADOS.get(t[0], ("—", "", "Pendiente"))[2]] for t in pd.PRUEBAS_RED])
    r.p("Criterio de aceptación observado: todos los aislamientos entre zonas verificados en vivo bloquearon el acceso no autorizado, los flujos permitidos (WMS, BD Patroni, SSH desde bastión y túnel híbrido) respondieron y SIEM01 alertó ante eventos de señuelo, firewall e IDS Suricata.")

    # ── 8 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Evidencias técnicas y repositorio")
    r.h2("Evidencias por componente")
    r.tabla(["Componente", "Qué capturar", "Dónde está la configuración"], [
        ["pfSense", "Reglas por interfaz, alias, NAT y estado de CARP", "etapas/10-red/roles/pfsense_base y vars/reglas.yml"],
        ["Switches", "show running-config (sin secretos), show etherchannel summary y show spanning-tree", "etapas/10-red/roles/cisco_switching; configs exportadas con Oxidized"],
        ["VPN", "wg show en pfSense y en GCP-BORDE; ruta de la VPC", "etapas/50-nube/main.tf"],
        ["Señuelo", "Una alerta de OpenCanary en Wazuh", "etapas/40-servicios/roles/02-seguridad/honeypot"],
        ["SIEM y monitoreo", "Panel de Wazuh y de Zabbix, y correo de la alerta de la nube", "roles wazuh_server y zabbix_server; main.tf"],
    ])
    r.h2("Repositorio técnico de red")
    r.p("El repositorio cologistic-infra contiene las configuraciones como código (Ansible y Terraform), el diseño versionado y los makefiles de cada etapa. El README describe cómo reconstruir cada capa. "
        "Se sigue la regla de no exponer secretos: las claves van en .env, que no se versiona, y las contraseñas en archivos de instalación desatendida fueron reemplazadas por variables inyectadas desde .env (hallazgo H01 cerrado en código).")

    # ── 9 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conclusiones")
    r.bullets(
        f"La red diseñada está implementada y validada en laboratorio: de los {len(pd.PRUEBAS_RED)} casos técnicos, {c['aprobadas']} fueron aprobados en vivo sobre FW-MAIN, FW-BACKUP, SIEM01, HONEY01, DMZ, Patroni HA y GCP.",
        "Se cerró el hallazgo H05 instalando pfSense-pkg-suricata 7.0.10 (Suricata 8.0.7) en em0.31 y validando la detección hacia SIEM01 (reglas Wazuh 100100, 100110 y 100120).",
        "Los 4 casos restantes documentan brechas reales identificadas sin maquillar resultados: T06 bloqueado por IP pública dinámica del laboratorio (H02: 0.0.0.0/0 en GCP), T26 (syslog en switches H08), T27 (alta SNMP de switches en Zabbix) y T28 (prueba de estrés CPU en vivo).",
        "Cada resultado aprobado cuenta con evidencia técnica trazable en firewall, capturas tcpdump, registros de SIEM01 o respuestas de APIs.")

    r.biblio(
        "[1] Netgate, \"pfSense Documentation.\" [Online]. Disponible: https://docs.netgate.com/pfsense/en/latest/",
        "[2] J. A. Donenfeld, \"WireGuard: Next Generation Kernel Network Tunnel,\" in Proc. NDSS, San Diego, CA, USA, 2017.",
        "[3] Wazuh Inc., \"Wazuh Documentation.\" [Online]. Disponible: https://documentation.wazuh.com/",
        "[4] Thinkst Applied Research, \"OpenCanary Documentation.\" [Online]. Disponible: https://opencanary.readthedocs.io/",
        "[5] Google Cloud, \"VPC firewall rules\" y \"Cloud Monitoring alerting.\" [Online]. Disponible: https://cloud.google.com/docs",
        "[6] International Organization for Standardization, \"ISO/IEC 27002:2022 Information security controls,\" Geneva, 2022.")
    return r
