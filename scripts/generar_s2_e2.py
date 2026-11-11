"""
generar_s2_e2.py — Contenido del entregable S2_E2: Implementación, Testing y Monitoreo de Red.

Describe lo que el repositorio cologistic-infra implementa (roles de Ansible, estado de Terraform, commits) y las reglas de pfSense reales.
Los resultados de las pruebas NO se inventan: el plan está completo y el resultado obtenido queda pendiente hasta ejecutar cada caso en el laboratorio.
"""
import datos
import pruebas_datos as pd
from redactor import Redactor

NUBE = datos.nube()
REGLAS = datos.resumen_reglas()


def reglas_por_zona():
    filas = []
    for interfaz, reglas in datos.reglas_por_interfaz().items():
        paso = sum(x["action"] == "pass" for x in reglas)
        bloqueo = sum(x["action"] == "block" for x in reglas)
        filas.append([interfaz, str(paso), str(bloqueo), str(len(reglas))])
    return filas


def contenido():
    r = Redactor()

    # ── 1 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Resumen ejecutivo")
    r.p("Este informe documenta cómo se implementó la red diseñada en el entregable S1_E1: la configuración de los switches y el router, el firewall pfSense con sus zonas y reglas, el túnel hacia Google Cloud, "
        "la detección (señuelo, SIEM e IDS/IPS) y el monitoreo. También incluye el plan de pruebas de permitido y denegado que valida el diseño.")
    r.p("El informe distingue tres estados y los usa sin exagerar: «Implementado» (existe y se desplegó), «Automatizado» (el rol está escrito en el repositorio y falta comprobarlo en el equipo) y "
        "«Pendiente» (no existe todavía).")
    r.tabla(["Componente", "Estado", "Evidencia"], [
        ["Switches Cisco (7) con VLAN, STP, port-channels y puertos sin uso", "Implementado", "Roles cisco_switching; tablero de laboratorio; docs/switches.md"],
        ["Router Cisco C1111-4P (borde, NAT, VLAN 901 a 904)", "Implementado", "Rol cisco_edge; verificado en el equipo"],
        ["Firewall pfSense: sistema, VLAN, WAN, alta disponibilidad, alias, NAT, reglas, DHCP y registros", "Automatizado", f"10 playbooks y el rol pfsense_base; {REGLAS['total']} reglas"],
        ["VPC de Google Cloud, GCP-BORDE, firewall, ruta, buckets, GCP-WMS-DRP, Artifact Registry, Secret Manager, Cloud DNS y alerta", "En revisión (IaC completa en main.tf)", "Etapa 50 (Terraform): gcp-borde desplegado; recursos DRP y Tailscale codificados pendientes de apply"],
        ["Túnel WireGuard: extremo en la nube", "Implementado", "VM de borde con WireGuard + Tailscale Subnet Router (10.20.0.0/24)"],
        ["Túnel WireGuard y Tailscale: extremo en pfSense", "Automatizado", "Playbooks nube_tunel.yml y pfsense_10_acceso_remoto.yml (Subnet Router 10.10.0.0/16); pendiente aplicar en vivo"],
        ["Señuelo OpenCanary (HONEY01)", "Automatizado", "Rol honeypot; despliegue en los commits de noviembre"],
        ["SIEM Wazuh (SIEM01) y syslog remoto", "Automatizado", "Rol wazuh_server; envío de syslog desde pfSense"],
        ["Monitoreo Zabbix (MON01)", "Automatizado", "Rol zabbix_server (Docker)"],
        ["IDS/IPS en pfSense", "Pendiente", "Sin rol en el repositorio; decisión Suricata o Snort pendiente"],
        [f"Pruebas de permitido y denegado ({len(pd.PRUEBAS_RED)} casos)", "Pendiente", "Plan completo; resultados por obtener"],
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
        ["Señuelo con SSH, SMB y HTTP", "OpenCanary con HTTP 80, SMB 445 y FTP 21; el rol prevé mover el SSH real de administración al puerto 2222", "Para que el puerto 22 del señuelo no se confunda con el acceso real de gestión; a confirmar en el equipo."],
        ["Túnel entre pfSense y GCP-BORDE", "Automatizado en nube_tunel.yml + acceso_remoto.yml (Tailscale)", "Falta ejecutar/verificar en hardware pfSense; además añade acceso directo 10.20.0.0/24 si caen los routers locales."],
        ["Exposición pública del WMS vía WAF01", "WMS privado (Intranet + Tailscale); WAF01 devuelve 403", "Decisión D19: sin NAT 443 público al WMS; WAF01 queda aislado para futuros portales externos."],
        ["Firewall de la VPC: UDP 51820 solo desde la IP del centro de datos", "UDP 51820 permitido desde cualquier origen", "Desviación (hallazgo H02 del SGSI): se restringirá cuando se conozca la IP pública del centro de datos."],
        ["IDS/IPS en pfSense", "No implementado", "Pendiente; el paquete se instalará y configurará (hallazgo H05)."],
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
    r.p("La automatización de ambos accesos híbridos ya existe en el repositorio (etapas/50-nube/playbooks/nube_tunel.yml para WireGuard wg0 10.20.0.18/19 y etapas/10-red/roles/pfsense_base/tasks/acceso_remoto.yml para Tailscale Subnet Router 10.10.0.0/16). "
        "Queda pendiente aplicar ambos playbooks en los firewalls físicos con las claves reales en .env para ejecutar las pruebas T01, T02, T29 y T30.")
    r.fig("vpn.png", "Figura 3.1 — Conexión híbrida: firewalls, router y VPC de Google Cloud con el túnel WireGuard", ancho_cm=9.5)
    r.h2("Enrutamiento")
    r.bullets(
        "Del centro de datos a la nube: ruta estática hacia 10.20.0.0/24 por la interfaz wg0 de pfSense.",
        "De la nube al centro de datos: la ruta ruta-a-datacenter de la VPC envía 10.10.0.0/16 a GCP-BORDE, que reenvía por wg0.",
        "Cifrado: WireGuard usa ChaCha20-Poly1305 y Curve25519. La prueba T03 verifica en la WAN que no sale tráfico en claro.")

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
    r.p("El rol honeypot instala OpenCanary en un entorno virtual de Python en HONEY01 (VLAN 130, 10.10.130.10). Simula HTTP (puerto 80, con la cabecera de Apache), SMB (445, con auditoría de acceso) y FTP (21), "
        "y envía cada evento por syslog a SIEM01. El rol prevé mover el SSH real de administración al puerto 2222 (a confirmar en el equipo). Las reglas de pfSense permiten que servidores y aplicaciones alcancen el señuelo con registro, "
        "y bloquean todo tráfico que sale de él hacia la red interna, salvo el envío de sus alertas al SIEM, DNS y parches.")
    r.h2("IDS/IPS")
    r.p("El IDS/IPS en pfSense no está implementado todavía. Está ubicado en el diseño sobre la WAN y las zonas de servidores, DMZ y señuelo, y sus alertas irán a SIEM01. Pendientes: elegir Suricata o Snort, instalar el paquete, "
        "habilitar los conjuntos de reglas y documentar los eventos. Hasta entonces la prueba T24 no se puede ejecutar.")
    r.h2("SIEM")
    r.p("SIEM01 corre Wazuh con el instalador todo-en-uno (Manager, Indexer y Dashboard) y recibe syslog remoto por UDP 514 de pfSense y del señuelo. Los agentes de Wazuh de los servidores se permiten en las reglas de cada VLAN "
        "(TCP 1514 y 1515). Las alertas del señuelo y del IDS se correlacionarán en el panel.")

    # ── 6 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Monitoreo, registros y visibilidad de red")
    r.tabla(["Componente", "Qué hace", "Estado"], [
        ["Wazuh (SIEM01)", "Centraliza los registros y los eventos de seguridad; panel de consulta", "Automatizado"],
        ["Syslog de pfSense", "Envía todos los registros a 10.10.34.20:514 desde la VLAN 70", "Automatizado"],
        ["Syslog de los switches", "Debe enviar sus eventos al SIEM", "Pendiente (H08)"],
        ["Zabbix (MON01)", "Disponibilidad y rendimiento por SNMPv3 y agentes; reglas hacia la VLAN 70 y los servidores", "Automatizado; falta cargar los equipos y las alertas"],
        ["Oxidized (ITSM01)", "Guarda cada cambio de configuración de los switches", "Automatizado"],
        ["Cloud Monitoring (nube)", "Alerta de CPU de GCP-BORDE con aviso por correo", "Implementado"],
    ])
    r.p("Pendiente: construir los paneles de red (tráfico por VLAN, bloqueos de firewall por zona y alertas del señuelo) y conservar una captura de cada uno como evidencia.")

    # ── 7 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Plan y resultados de pruebas técnicas")
    r.p(f"El plan tiene {len(pd.PRUEBAS_RED)} casos, positivos (debe pasar) y negativos (debe bloquearse o detectarse). Cada caso indica objetivo, precondición, pasos y resultado esperado. "
        "El criterio de aceptación es que el resultado obtenido coincida con el esperado y que haya evidencia. Todos los casos están pendientes de ejecución; el archivo Excel «Plan y resultados de pruebas» "
        "tiene las columnas para el resultado obtenido, la evidencia y el estado.")
    r.tabla(["ID", "Objetivo", "Pasos", "Resultado esperado", "Obtenido", "Estado"],
            [[t[0], f"{t[1]} ({t[5]})", t[3], t[4], "—", "Pendiente"] for t in pd.PRUEBAS_RED])
    r.p("Criterio de aceptación global: todos los casos negativos bloqueados, todos los positivos permitidos, y una alerta en SIEM01 por cada prueba de detección.")

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
        "Se sigue la regla de no exponer secretos: las claves van en .env, que no se versiona. La revisión del repositorio encontró una contraseña de administrador de Windows escrita en archivos del repositorio; "
        "se rotará y se retirará del historial antes de entregar el repositorio al docente (hallazgo H01 del SGSI).")

    # ── 9 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conclusiones")
    r.bullets(
        "La red diseñada está automatizada en switches, router y firewalls (incluidos acceso remoto Tailscale y reglas de WMS privado).",
        "Quedan pendientes de aplicar y validar en el equipamiento físico el extremo del túnel WireGuard/Tailscale, las reglas DRP en GCP y el módulo IDS/IPS.",
        f"El plan de {len(pd.PRUEBAS_RED)} pruebas cubre el túnel, Tailscale Cloud, el bloqueo DMZ->WMS, la segmentación, Patroni HA y el monitoreo, y está listo para ejecutarse.",
        "Los resultados de las pruebas no se declaran hasta contar con la evidencia de su ejecución.")

    r.biblio(
        "[1] Netgate, \"pfSense Documentation.\" [Online]. Disponible: https://docs.netgate.com/pfsense/en/latest/",
        "[2] J. A. Donenfeld, \"WireGuard: Next Generation Kernel Network Tunnel,\" in Proc. NDSS, San Diego, CA, USA, 2017.",
        "[3] Wazuh Inc., \"Wazuh Documentation.\" [Online]. Disponible: https://documentation.wazuh.com/",
        "[4] Thinkst Applied Research, \"OpenCanary Documentation.\" [Online]. Disponible: https://opencanary.readthedocs.io/",
        "[5] Google Cloud, \"VPC firewall rules\" y \"Cloud Monitoring alerting.\" [Online]. Disponible: https://cloud.google.com/docs",
        "[6] International Organization for Standardization, \"ISO/IEC 27002:2022 Information security controls,\" Geneva, 2022.")
    return r
