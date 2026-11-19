"""
evidencias_datos.py — Qué demuestra cada captura de figuras/evidencias/ (texto que la acompaña en la sección del informe S2 que respalda).

Solo los entregables S2 (implementación) llevan estas capturas; los S1 son de diseño y su vínculo con lo implementado
ya está en la sección «Trazabilidad con el diseño (Semestre 1)» de cada S2.
"""

EXPLICA = {
    # ── S2_E1 · SGSI ────────────────────────────────────────────────────────────────────────────────────────────
    "s2_e1_sec07_01_glpi_ldap_rbac.png":
        "GLPI autentica contra el Active Directory de DC1 (10.10.30.11) y asigna el perfil según el grupo del directorio: "
        "GG_TI_Administradores recibe Super-Admin y GG_TI_Soporte recibe Technician, sin cuentas locales por persona.",
    "s2_e1_sec07_02_guacamole_totp_mfa.png":
        "El bastión Apache Guacamole pide un código TOTP después de la contraseña: ninguna sesión privilegiada se abre sin segundo factor.",
    "s2_e1_sec07_03_guacamole_14_conexiones.png":
        "Las 14 conexiones privilegiadas (7 switches Cisco y 5 nodos Proxmox por SSH, 2 controladores de dominio por RDP) están "
        "definidas como código y agrupadas por dominio, de modo que la administración pasa por un único punto controlado y registrado.",
    "s2_e1_sec07_04_vaultwarden_org_colecciones.png":
        "Las credenciales de TI están en la Organización Co-Logistic S.A.C., separadas en 8 colecciones por dominio técnico, "
        "que son la base para conceder acceso por rol.",
    "s2_e1_sec07_05_vaultwarden_miembros_2fa.png":
        "Cada miembro es una cuenta nominal con rol User y acceso solo a las colecciones de su función (por ejemplo, el equipo de "
        "software solo ve 07-Datos-y-WMS); la cuenta administradora tiene activo el doble factor con aplicación autenticadora y passkey.",
    "s2_e1_sec07_06_vaultwarden_items_organizacion.png":
        "Las credenciales figuran con propietario Co-Logistic S.A.C. y no en bóvedas personales, por lo que su acceso se gobierna desde la organización.",
    "s2_e1_sec08_01_glpi_ticket_inc001_top.png":
        "El incidente INC-2026-001 (prueba T24) quedó registrado en GLPI con su clasificación ISO/IEC 27001 (A.5.24 a A.5.28), "
        "el activo afectado WMS01 y la evidencia de Suricata y Wazuh que lo detectó.",
    "s2_e1_sec08_02_glpi_ticket_inc001_fases.png":
        "El mismo ticket documenta la contención, la erradicación y el cierre con lecciones aprendidas, y queda vinculado al problema H05.",
    "s2_e1_sec10_01_wazuh_vuln_sca.png":
        "Wazuh evalúa de forma continua las vulnerabilidades (CVE) de WMS01, DB01 y DB02; las 43 críticas y 499 altas detectadas "
        "son entrada para el tratamiento de riesgos y el plan de parches.",
    "s2_e1_sec10_02_proxmox_rol_terraformprov.png":
        "En Proxmox existe el rol personalizado TerraformProv, con solo los privilegios que necesita el aprovisionamiento por Terraform, "
        "en lugar de usar el rol Administrator (cierre del hallazgo H03).",
    # ── S2_E2 · Red ─────────────────────────────────────────────────────────────────────────────────────────────
    "s2_e2_sec03_01_pfsense_carp_services.png":
        "pfSense-MAIN es MASTER de todas las direcciones virtuales CARP de las VLAN (alta disponibilidad con FW-BACKUP) "
        "y tiene en ejecución sus servicios de red, entre ellos Suricata, el resolvedor DNS y el relé DHCP.",
    "s2_e2_sec03_02_gcp_vpc_rutas.png":
        "La VPC de Google Cloud tiene la ruta estática ruta-a-datacenter, que envía 10.10.0.0/16 por la VM de borde WireGuard: "
        "es el camino de vuelta del enrutamiento híbrido.",
    "s2_e2_sec04_01_pfsense_dashboard.png":
        "pfSense CE 2.9.0 en operación con todas las interfaces de VLAN levantadas a 1 Gbit/s, cada una con su dirección de puerta de enlace.",
    "s2_e2_sec04_02_pfsense_rules_vlan10.png":
        "La VLAN 10 (ADMINISTRACION) solo abre servicios concretos (directorio, DNS, archivos, WMS, BI, SIEM) y bloquea de forma "
        "explícita el acceso a servidores no autorizados, a la red de gestión (VLAN 70) y al almacenamiento de respaldos.",
    "s2_e2_sec04_03_pfsense_rules_dmz.png":
        "La DMZ solo llega a los servicios que necesita y tiene bloqueos hacia la base de datos y la red de gestión, cuyos contadores "
        "muestran intentos ya denegados y registrados.",
    "s2_e2_sec04_04_pfsense_rules_vlan70.png":
        "La VLAN 70 (GESTION_TI) acota la administración al bastión y a los servicios de soporte (AD, SIEM, NTP, inventario); "
        "la última fila es la regla por defecto de pfSense, que permite el resto del tráfico saliente de esta VLAN.",
    "s2_e2_sec05_01_pfsense_suricata_ids.png":
        "Suricata funciona en modo IDS sobre em0.31 (VLAN 31 APLICACIONES) y registra alertas, entre ellas la firma propia 9000001 de escaneo TCP.",
    "s2_e2_sec05_02_wazuh_alerta_t24.png":
        "La alerta de la prueba T24 llegó a Wazuh como regla 100120 (nivel 8), con el registro completo de Suricata y la técnica "
        "MITRE T1046 (descubrimiento de servicios de red).",
    "s2_e2_sec05_03_wazuh_tuning_100121.png":
        "Tras el ajuste de la regla 100121, el monitoreo legítimo de Zabbix (MON01 hacia el puerto 10050) ya no genera alertas 100120: "
        "cero resultados en 15 minutos, sin desactivar la detección de escaneos reales.",
    "s2_e2_sec06_01_wazuh_overview.png":
        "Wazuh 4.9.2 en SIEM01 tiene los 3 agentes activos y ninguno desconectado, y resume las alertas de las últimas 24 horas por severidad.",
    "s2_e2_sec06_02_oxidized_7_switches.png":
        "Oxidized respalda en Git la configuración de los 7 switches Cisco, todos con su último respaldo correcto.",
    "s2_e2_sec06_03_oxidized_remove_secret.png":
        "En la configuración respaldada de SW1-CORE1 las líneas de enable secret y del usuario aparecen como <secret hidden>: "
        "el respaldo no guarda credenciales.",
    # ── S2_E3 · Centro de datos ─────────────────────────────────────────────────────────────────────────────────
    "s2_e3_sec03_01_proxmox_cluster_5_nodos.png":
        "El clúster PVE-COLOGISTIC tiene quórum con los 5 nodos en línea y ejecuta 25 máquinas virtuales.",
    "s2_e3_sec03_02_wms_produccion_https.png":
        "La aplicación WMS está en operación y con sesión iniciada, mostrando indicadores reales de stock, recepciones, despachos y movimientos.",
    "s2_e3_sec03_03_metabase_bi_datos.png":
        "Metabase muestra datos del WMS cargados por el ETL (última extracción del 19/11/2026 a las 12:45), lo que prueba que el "
        "flujo WMS hacia el DataWarehouse funciona.",
    "s2_e3_sec03_04_metabase_dw_conexion.png":
        "Metabase se conecta al DataWarehouse por la IP virtual 10.10.33.10 del clúster Patroni con un usuario dedicado (dw_user); "
        "la contraseña queda fuera de la captura.",
    "s2_e3_sec04_01_gcp_vpc_subredes.png":
        "La VPC vpc-cologistic tiene las tres subredes del diseño en southamerica-west1: nube-borde (10.20.0.0/28), "
        "nube-tunel (10.20.0.16/29) y nube-privada (10.20.0.32/28).",
    "s2_e3_sec04_02_gcp_firewall_h02_cerrado.png":
        "La regla fw-permitir-wireguard solo admite UDP 51820 desde la IP pública del centro de datos (168.121.48.246/32) hacia gcp-borde, "
        "en vez de 0.0.0.0/0 (cierre del hallazgo H02).",
    "s2_e3_sec04_03_gcp_compute_vms.png":
        "gcp-borde está en ejecución y gcp-wms-drp está detenida, como pide la arquitectura Pilot Light: la VM de recuperación no genera "
        "costo de cómputo hasta que se necesita.",
    "s2_e3_sec05_01_gcp_iam_service_accounts.png":
        "Cada carga de trabajo usa su propia cuenta de servicio (sa-gcp-compute, sa-respaldo, sa-terraform, sa-logs, entre otras) "
        "en lugar de la cuenta por defecto, que tiene permisos amplios.",
    "s2_e3_sec06_01_glpi_aplicativos_cloud.png":
        "Los 6 recursos de Google Cloud están registrados en la CMDB de GLPI con su ubicación, clasificación C-I-D, criticidad y dependencias.",
    "s2_e3_sec07_01_gcp_bucket_respaldos.png":
        "El bucket de respaldos fuera del sitio no es público, tiene control de versiones y borrado no definitivo, y una regla de ciclo "
        "de vida que elimina los objetos a los 90 días.",
    "s2_e3_sec08_01_zabbix_31_hosts.png":
        "Zabbix tiene registrados los 31 hosts del inventario (VMs Linux, switches por SNMP y el clúster Proxmox). Al momento de la "
        "captura el agente respondía en DB01, DB02, WMS01 y el propio servidor; en el resto el indicador figura en rojo.",
    "s2_e3_sec08_02_zabbix_proxmox_agentless.png":
        "El host PVE-COLOGISTIC descubre sin agente, por la API de Proxmox, los 5 nodos (hv-main y hv1 a hv4) y sus máquinas, con 429 métricas.",
    "s2_e3_sec08_03_zabbix_triggers_capacidad.png":
        "Los triggers de capacidad del clúster usan umbrales de 80 % para memoria, disco raíz y almacenamiento, definidos como macros del host.",
    "s2_e3_sec08_04_wazuh_3_agentes.png":
        "Los agentes Wazuh de WMS01, DB01 y DB02 están activos y en la misma versión que el servidor (4.9.2).",
    "s2_e3_sec08_05_gcp_monitoring_4_alertas.png":
        "Cloud Monitoring tiene habilitadas las 4 políticas de alerta: disco raíz, memoria RAM, caída de disponibilidad y CPU de GCP-BORDE.",
    "s2_e3_sec08_06_gcp_monitoring_dashboard.png":
        "El panel Co-Logistic Cloud — Monitoreo Híbrido muestra en tiempo real la CPU, la RAM, el disco y el tráfico del túnel WireGuard de las VMs de Google Cloud.",
}
