"""
generar_s2_e3.py — Contenido del entregable S2_E3: Implementación, Gestión y Control de Centro de Datos.

Lo implementado sale del repositorio cologistic-infra: etapas 20 (Proxmox), 30 (Terraform de VM), 40 (servicios) y 50 (Google Cloud, con su estado de Terraform).
La prueba de recuperación está planificada con su procedimiento y su registro; sus resultados quedan pendientes hasta ejecutarla (no se inventan tiempos).
"""
import datos
import pruebas_datos as pd
from redactor import Redactor

NUBE = datos.nube()
VM = datos.totales_vm()
CAP = datos.capacidad()
HV = datos.hipervisores()
CARGA = datos.carga_por_nodo()

# Qué rol de Ansible (etapas/40-servicios) configura cada máquina
ROL_DE = {
    "DC1": "01-core/active_directory", "DC2": "01-core/active_directory", "AAA01": "01-core/freeradius", "AAA02": "01-core/freeradius",
    "INFRA01": "01-core/infra_stack", "FS01": "01-core/samba_fileserver", "WAF01": "03-perimetro/waf_reverse_proxy", "SFTP01": "03-perimetro/sftp_b2b",
    "PBX01": "03-perimetro/asterisk_pbx", "MAIL01": "03-perimetro/postfix_relay", "MGMT01": "02-seguridad/mgmt_stack", "ITSM01": "02-seguridad/itsm_stack",
    "MON01": "02-seguridad/zabbix_server", "SIEM01": "02-seguridad/wazuh_server", "VULN01": "02-seguridad/openvas", "HONEY01": "02-seguridad/honeypot",
    "WLC01": "02-seguridad/omada_controller", "WMS01": "04-apps/wms", "WMS02": "04-apps/wms", "DB01": "04-apps/postgresql_ha + quorum_etcd", "DB02": "04-apps/postgresql_ha + quorum_etcd",
    "DW01": "04-apps/datawarehouse_bi", "DW02": "04-apps/datawarehouse_bi", "BKP01": "05-respaldo/bareos_zfs", "NVR01": "05-respaldo/zoneminder_nvr",
    "ACS01": "Windows desde ISO (etapa 30)", "PAW01": "Windows desde ISO (etapa 30)", "PAW02": "Windows desde ISO (etapa 30)",
}


def contenido():
    r = Redactor()

    # ── 1 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Resumen ejecutivo")
    r.p(f"Este informe documenta cómo se implementó el centro de datos híbrido diseñado en el entregable S1_E2: el cluster Proxmox de cinco servidores con sus {VM['n']} máquinas virtuales, la extensión en Google Cloud, "
        "la gestión de identidades y accesos, el inventario final, la estrategia de respaldo/HA y el monitoreo.")
    r.p("Como en el entregable de red, se distinguen los estados «Implementado» (existe y se desplegó), «Automatizado» (el rol está escrito y falta comprobarlo en el equipo) y «Pendiente».")
    r.tabla(["Componente", "Estado", "Evidencia"], [
        ["Red de los nodos Proxmox (bond0, vmbr1 y VLAN 70) y cluster PVE-COLOGISTIC", "Implementado", "Etapa 20, roles proxmox_red y proxmox_cluster"],
        ["Plantillas cloud-init Debian y Ubuntu y plantilla Windows Server 2022", "Implementado", "Rol proxmox_templates (plantillas 9000, 9001 y 9002)"],
        [f"{VM['n']} máquinas virtuales ({VM['linux']} Linux y {VM['windows']} Windows)", "Automatizado", "Etapa 30 (Terraform con DW02 y DB02 2 vCPU/4 GB) y etapa 40"],
        ["Servicios HA: Patroni + etcd (DB01/02/INFRA01 y DW01/02), keepalived VIPs, WMS CI/CD (Django DRF + React), FS01->BKP01", "Automatizado", "Etapa 40 (quorum_etcd, patroni_cluster, wms, bareos_zfs, samba_fileserver) + .github/workflows/deploy.yml"],
        ["Nube GCP: VPC, GCP-BORDE (34.176.121.24 + Tailscale), GCP-WMS-DRP privado, Artifact Registry, Secret Manager, Cloud DNS y alerta", "Implementado / En revisión", "Estado de Terraform de etapa 50 (gcp-borde base aplicado; DRP/Artifact Registry/Secret Manager codificados en main.tf)"],
        ["Respaldo horario pg_dump + rclone a GCS y sync FS01->BKP01 (5 min)", "Automatizado", "Roles bareos_zfs y samba_fileserver (cron horario BD + cron 5m rsync)"],
        ["Ejercicio de recuperación completo", "Registrado (parcial) / Por ampliar", "S2_E3 XLSX registra pruebas DB02/GCS/vzdump; falta validar failover DW02/FS01 y gcp-wms-drp tras apply"],
        ["MFA y rotación de credenciales", "Pendiente", "Definidos en la política de accesos; falta habilitarlos y evidenciarlos"],
        ["Paneles y alertas de capacidad de los hosts", "Pendiente", "Zabbix desplegado; falta cargar los hosts y las alertas"],
    ])

    # ── 2 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Trazabilidad con el diseño de centro de datos (Semestre 1)")
    r.tabla(["Elemento del diseño", "Lo implementado", "Cambio y justificación"], [
        ["Cinco servidores físicos con hipervisor", "Cinco Dell Precision en torre con Proxmox VE, en un cluster", "La rúbrica habla de ESXi; el diseño usa Proxmox por licencia y por su cluster nativo."],
        ["Un bridge VLAN-aware con bond hacia dos ToR", "vmbr1 sobre bond0 en modo active-backup (nic1 y nic2)", "Ninguno."],
        ["Gestión del host en la VLAN 70", "vmbr1.70 con la IP de cada nodo", "Ninguno; no hay red fuera de banda."],
        [f"{VM['n']} máquinas virtuales planeadas", f"{VM['n']} máquinas: {VM['linux']} Linux y {VM['windows']} Windows", "Igual; los servicios afines se consolidaron antes de desplegar (decisión D18)."],
        ["Cluster con un solo enlace de corosync", "Igual: por la VLAN 70", "Ninguno; queda como mejora una red dedicada."],
        ["Plantilla de cloud-init en cada nodo", "Plantillas 9000 (Debian), 9001 (Ubuntu) y 9002 (Windows Server 2022)", "Windows se prepara con una imagen base (golden image) porque no usa cloud-init nativo."],
        ["Google Cloud: VPC con tres subredes, VM de borde y buckets", "Desplegado según lo diseñado", "Nombres de bucket con el identificador del proyecto (únicos en todo Google Cloud)."],
        ["Firewall de la VPC con UDP 51820 solo desde el centro de datos", "UDP 51820 desde cualquier origen", "Desviación pendiente de corregir (hallazgo H02 del SGSI)."],
        ["Instancia de la nube con cuenta de servicio dedicada", "Cuenta de servicio por defecto de Compute Engine", "Desviación pendiente de corregir (hallazgo H02)."],
    ])

    # ── 3 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Implementación on-premise: Proxmox VE y máquinas virtuales")
    r.h2("Cluster y red de los nodos")
    r.p("La etapa 20 de Ansible configura cada nodo en este orden: red, cluster, repositorios, almacenamiento, token de API, plantillas e ISO. "
        "Para la red, cada nodo recibe bond0 (active-backup con las dos NIC hacia los ToR), el bridge vmbr1 con VLAN-aware y la IP de gestión en vmbr1.70. "
        "El cluster PVE-COLOGISTIC se crea en HV-MAIN y los demás nodos se unen con la huella del certificado del primero; el rol verifica el quórum y la cantidad de nodos con pvecm status. "
        "Corosync usa un solo enlace, por la VLAN 70.")
    r.tabla(["Nodo", "Núcleos", "RAM", "Disco", "VM alojadas", "vCPU / RAM / disco asignados"],
            [[n, str(HV[n]["vcpu"]), f"{HV[n]['ram_gb']:g} GB", f"{HV[n]['disco_gb']:g} GB", str(CARGA[n]["n"]),
              f"{CARGA[n]['vcpu']} / {CARGA[n]['ram']:g} GB / {CARGA[n]['disco']:g} GB"] for n in HV] +
            [["Total", str(CAP["cores"]), f"{CAP['ram']:.1f} GB", f"{CAP['disco']} GB", str(VM["n"]), f"{VM['vcpu']} / {VM['ram']:g} GB / {VM['disco']:g} GB"]])
    r.h2("Almacenamiento y plantillas")
    r.bullets(
        "Almacenamiento local de cada nodo para los discos (local-lvm) y para las imágenes ISO y los fragmentos de cloud-init (local). No hay almacenamiento compartido.",
        "Los repositorios de Proxmox pasan a pve-no-subscription.",
        "Las plantillas Linux (Debian 9000 y Ubuntu 9001) se construyen con cloud-init; la de Windows Server 2022 (9002) es una imagen base con OpenSSH y el agente de invitado.",
        "El token de API de Terraform lo crea el rol proxmox_token para el usuario terraform@pve.")
    r.h2("Máquinas virtuales desplegadas")
    r.p("Las VM Linux se clonan con Terraform (etapa 30) y las Windows se instalan desde ISO desatendida. La tabla muestra el nodo, el identificador (VMID), la IP y los recursos de cada una.")
    filas = []
    for n, d in sorted(datos.VMS.items(), key=lambda kv: (kv[1]["nodo"], kv[0])):
        filas.append([n, d["nodo"], str(d.get("vm_id", "—")), d.get("ip", "—"), f"{d['vcpu']} / {d['ram_gb']:g} GB / {d['disco_gb']:g} GB", d["so"]])
    r.tabla(["VM", "Nodo", "VMID", "IP", "vCPU / RAM / disco", "Sistema"], filas)
    r.fig("hipervisor_2filas.png", "Figura 3.1 — Los cinco nodos con su bridge vmbr1, la VLAN de cada VM y la IP de gestión (vmbr1.70)")
    r.h2("Servicios desplegados")
    r.p("La etapa 40 configura los servicios por niveles (base, núcleo, seguridad, perímetro, aplicaciones y respaldo), con un rol de Ansible por servicio. "
        "Dos scripts, auditar_base y auditar_core, comprueban en vivo los servicios: replicación entre controladores de dominio, unidades organizativas, ámbitos DHCP, DNS, la autoridad de certificados y la caché de paquetes, "
        "la autenticación RADIUS de los switches y los recursos de Samba y de impresión.")
    r.tabla(["Nivel", "Servicios"], [
        ["Base", "Configuración común de Linux (hora, SSH, proxy de paquetes) y Docker"],
        ["Núcleo", "Active Directory y DNS (DC1, DC2), FreeRADIUS (AAA01, AAA02), Step-CA + caché APT + testigo etcd (INFRA01), Samba FS01 (rsync a BKP01 cada 5 min)"],
        ["Seguridad", "SIEM Wazuh (SIEM01), Zabbix (MON01), escáner de vulnerabilidades (VULN01), señuelo (HONEY01), bastión y bóveda de secretos (MGMT01), GLPI y Oxidized (ITSM01), controladora Wi-Fi (WLC01)"],
        ["Perímetro", "WAF DMZ aislado del WMS privado (WAF01 devuelve 403), SFTP para socios (SFTP01), telefonía (PBX01) y relé de correo (MAIL01)"],
        ["Aplicaciones", "WMS privado CI/CD en Docker (Django 5.2 DRF + React SPA + Nginx + keepalived VIP .31.10 en WMS01/02), Patroni + etcd VIP .32.10 (DB01/DB02) y DW/Metabase HA VIP .33.10 (DW01/DW02)"],
        ["Respaldo", "Bareos con ZFS + cron horario pg_dump/rclone a GCS + contingencia Samba FS01 (BKP01) y videovigilancia con ZoneMinder (NVR01)"],
    ])

    # ── 4 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Implementación en la nube: Google Cloud")
    r.p("La etapa 50 de Terraform define la arquitectura híbrida DRP en el proyecto cologistic-cloud, región southamerica-west1 (base de VPC y gcp-borde desplegada; recursos DRP gcp-wms-drp, Artifact Registry, Secret Manager y Cloud DNS integrados en main.tf). Es el equivalente en Google Cloud de VPC, EC2, grupos de seguridad, ECR, Secrets Manager y Route 53:")
    r.tabla(["Concepto del diseño (equivalente AWS)", "Recurso en Terraform (etapa 50)", "Configuración"], [
        ["VPC (VPC)", "vpc-cologistic", "10.20.0.0/24"],
        ["Subredes (subredes)", "nube-borde, nube-tunel y nube-privada", "10.20.0.0/28, 10.20.0.16/29 y 10.20.0.32/28; la privada con Private Google Access"],
        ["Instancia de Borde (EC2 NAT/Bastion)", "gcp-borde", "e2-micro, southamerica-west1-a, IP 10.20.0.4, IP pública 34.176.121.24; WireGuard, Tailscale Subnet Router (10.20.0.0/24) y proxy TLS"],
        ["Instancia Privada DRP (EC2 privada)", "gcp-wms-drp", "e2-medium en nube-privada (10.20.0.34), sin IP pública, desired_status = TERMINATED ($0 cómputo standby); Docker WMS + BI + Postgres"],
        ["Registro de imágenes (ECR)", "southamerica-west1-docker.pkg.dev", "Artifact Registry wms-repo para pipeline CI/CD GitHub -> On-premise / DRP"],
        ["Gestor de secretos (Secrets Manager)", "wms-drp-env", "Secret Manager cifrado para credenciales DRP de wms_user y Django"],
        ["DNS Privado (Route 53 Private Zone)", "cologistic-privada", "Cloud DNS privada cologistic.net. apuntando wms/db/dw/bi a 10.20.0.34 en DRP"],
        ["Dirección pública (Elastic IP)", "ip-gcp-borde", "Externa y estática (34.176.121.24), para el túnel WireGuard"],
        ["Tabla de rutas y Firewall", "ruta-a-datacenter + 5 reglas", "WireGuard UDP 51820, tráfico túnel 10.10.0.0/16, SSH 22 (VLAN 70 e IAP), HTTP/HTTPS y tráfico DRP privado hacia 10.20.0.34"],
        ["Almacenamiento (S3)", "2 buckets", "Respaldos horarios (versionado y eliminación a los 90 días) y estado de Terraform (versionado); acceso uniforme"],
        ["IAM", "3 cuentas de servicio", "sa-respaldo (objectAdmin sobre respaldos), sa-terraform y sa-logs (roles/logging.logWriter)"],
        ["Monitoreo (CloudWatch)", "Política de alerta y canal de correo", "CPU de gcp-borde mayor al 85 % durante 5 minutos"],
    ])
    r.fig("vpc.png", "Figura 4.1 — VPC de Google Cloud: subredes, gcp-borde, gcp-wms-drp privado, túnel y bucket", ancho_cm=14)
    r.p("El estado previo de Terraform registró la VPC, gcp-borde y buckets; al aplicar los cambios actuales de etapa 50 quedan activos gcp-wms-drp (apagado en standby), Tailscale Cloud, Artifact Registry, Secret Manager y Cloud DNS privada.")

    # ── 5 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Gestión de identidades y accesos del centro de datos")
    r.tabla(["Ámbito", "Cómo se gestiona", "Observación"], [
        ["Proxmox VE", "Usuario root del Day-0 y usuario de servicio terraform@pve con un token de API", "El token tiene el rol Administrador sobre todo el cluster; se reemplazará por un rol de mínimo privilegio (hallazgo H03)."],
        ["Servidores y servicios", "Active Directory (DC1, DC2) y RADIUS (AAA01, AAA02); acceso de administración por el bastión (MGMT01, Apache Guacamole)", "Los usuarios no llegan a la VLAN de gestión."],
        ["Secretos", "Bóveda Vaultwarden en MGMT01 y archivo .env fuera de Git", "Hay una contraseña de administrador de Windows en archivos del repositorio; se rotará (hallazgo H01)."],
        ["Google Cloud", "Tres cuentas de servicio, cada una con un solo propósito; sa-respaldo con acceso solo al bucket de respaldos", "La VM de borde usa la cuenta por defecto; se asignará una dedicada (hallazgo H02)."],
        ["MFA", "TOTP en el bastión, en la bóveda y en la consola de Google Cloud", "Definido; falta habilitarlo y guardar la evidencia."],
        ["Rotación de credenciales", "Cada 90 días y ante la salida de una persona con acceso", "Definida; sin evidencia de la primera rotación."],
    ])

    # ── 6 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Inventario final de activos con evidencia")
    r.p("El inventario es el mismo del SGSI (entregable S2_E1), con el sistema y el rol de Ansible que evidencia la configuración de cada máquina. Los nodos y los recursos de la nube tienen su evidencia en las etapas 20 y 50.")
    filas = [[n, d["nodo"], d["so"], ROL_DE[n]] for n, d in sorted(datos.VMS.items(), key=lambda kv: (kv[1]["nodo"], kv[0]))]
    filas += [[f"{n} (servidor Proxmox)", "Sala de servidores", "Proxmox VE", "etapa 20: proxmox_red y proxmox_cluster"] for n in HV]
    filas += [["GCP-BORDE y GCP-WMS-DRP, VPC, firewall, ruta y alerta", "southamerica-west1", "Google Cloud", "etapa 50: main.tf y estado de Terraform"],
              ["Artifact Registry, Secret Manager, Cloud DNS privada", "southamerica-west1", "Servicios gestionados GCP", "etapa 50: main.tf"],
              ["Buckets de respaldos y de estado", "southamerica-west1", "Cloud Storage", "etapa 50: main.tf"],
              ["Cuentas de servicio", "Google Cloud IAM", "IAM", "etapa 50: main.tf"]]
    r.tabla(["Activo", "Ubicación", "Sistema", "Evidencia de configuración"], filas)

    # ── 7 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Continuidad: respaldo, restauración y recuperación probada")
    r.h2("Estrategia de respaldo implementada")
    r.bullets(
        "Servidor BKP01: Bareos y almacenamiento ZFS con carpetas para PostgreSQL, configuraciones, Bareos y espejo rsync desde FS01 (cada 5 min, publicado como contingencia Samba).",
        "Un script instalado por Ansible ejecuta respaldo horario (pg_dump) de las VIP Patroni (cologistic_wms, cologistic_dw y metabase_app) y lo sincroniza con el bucket Cloud Storage mediante rclone.",
        "Previsto en el diseño y por completar en vivo: respaldo de las máquinas virtuales con vzdump de Proxmox hacia BKP01 por NFS.",
        "El bucket conserva versiones y elimina objetos a los 90 días; el estado de Terraform tiene su propio bucket.",
        "Redundancia local automática: Patroni + quórum etcd de 3 nodos (DB01, DB02, testigo INFRA01) y VIPs keepalived en WMS (.31.10), BD WMS (.32.10) y DW/BI (.33.10), con pares en hipervisores distintos (D03).")
    r.h2("Ejercicio de recuperación")
    r.p("El archivo Excel «Registro de prueba de recuperación» conserva las mediciones preliminares ejecutadas sobre DB02/GCS/vzdump; tras incorporar Patroni, DW02, sync FS01->BKP01 y el nodo privado gcp-wms-drp, "
        "la validación ampliada sigue este procedimiento:")
    r.tabla(["Paso", "Qué se hace"], [[str(i + 1), p] for i, p in enumerate(pd.PASOS_RECUPERACION)])
    r.tabla(["Servicio", "RTO objetivo", "RPO objetivo", "RTO obtenido", "RPO obtenido", "Evidencia"],
            [[s, rto, rpo, "Pendiente (nueva matriz HA/DRP)", "Pendiente (nueva matriz HA/DRP)", "Ver registro S2_E3 XLSX"] for s, rto, rpo in pd.RECUPERACION])

    # ── 8 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Monitoreo y control operativo del centro de datos")
    sobre = VM["vcpu"] / CAP["cores"]
    pct_ram = 100 * VM["ram"] / CAP["ram"]
    pct_disco = 100 * VM["disco"] / CAP["disco"]
    r.tabla(["Qué se monitorea", "Con qué", "Estado"], [
        ["CPU y memoria de las VM y los servicios", "Zabbix (MON01) con agentes y SNMP", "Desplegado; falta cargar los hosts"],
        ["Estado y capacidad de los nodos Proxmox", "Zabbix y la vista de recursos del cluster", "Pendiente: plantilla y alertas de capacidad"],
        ["Registros de seguridad", "Wazuh (SIEM01)", "Desplegado"],
        ["Instancia de la nube", "Cloud Monitoring: alerta de CPU mayor al 85 % durante 5 minutos, aviso por correo", "Implementado"],
        ["Cambios de configuración de los switches", "Oxidized (ITSM01)", "Desplegado"],
        ["Capacidad", f"Asignación actual: {sobre:.2f} : 1 de CPU, {pct_ram:.1f} % de RAM y {pct_disco:.1f} % de disco", "Calculado en el modelo"],
    ])
    r.p("Pendiente: alertas de capacidad de los nodos (RAM libre menor al 20 %, disco mayor al 80 % y quórum del cluster) y una captura del panel como evidencia.")

    # ── 9 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Repositorio, control de versiones y reproducibilidad")
    r.bullets(
        "El repositorio cologistic-infra contiene el diseño versionado, la especificación generada, las cinco etapas (red, hipervisor, máquinas, servicios y nube) y los makefiles; el historial de Git registra cada cambio.",
        "Cada etapa declara lo que requiere y entrega (docs/contratos.md) y el README indica el orden de despliegue; con un entorno limpio se reconstruye con make.",
        "La validación del diseño y las pruebas (make verificar) fallan si la especificación no coincide con el diseño.",
        "CI/CD privado WMS: los repositorios wms-co-logistic-backend (Django 5.2 DRF) y wms-co-logistic-frontend (React 19 SPA) incluyen .github/workflows/deploy.yml hacia Artifact Registry GCP, VPN Tailscale y despliegue rolling sobre WMS01 -> WMS02.",
        "Secretos: .env está fuera de Git. La revisión halló una contraseña de administrador de Windows en archivos del repositorio y como valor por defecto en scripts; debe rotarse y retirarse antes de entregar el repositorio.")

    # ── 10 ──────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conclusiones")
    r.bullets(
        f"El centro de datos queda diseñado y automatizado al día: cluster de cinco nodos, {VM['n']} máquinas ({VM['linux']} Linux, {VM['windows']} Windows) con HA Patroni/etcd/keepalived y extensión en Google Cloud (gcp-borde + gcp-wms-drp privado).",
        "Se consolidó la seguridad eliminando la exposición pública del WMS en DMZ/WAF01 (acceso privado Intranet/Tailscale), integrando Artifact Registry, Secret Manager y Cloud DNS para contingencia DRP y CI/CD.",
        "Quedan pendientes la aplicación en vivo de los nuevos recursos de etapa 50 y roles HA de etapa 40, el MFA con su evidencia, las alertas de capacidad y las pruebas ampliadas de failover.")

    r.biblio(
        "[1] Proxmox Server Solutions GmbH, \"Proxmox VE Administration Guide.\" [Online]. Disponible: https://pve.proxmox.com/pve-docs/",
        "[2] HashiCorp, \"Terraform Documentation.\" [Online]. Disponible: https://developer.hashicorp.com/terraform/docs",
        "[3] Google Cloud, \"Compute Engine, VPC y Cloud Storage documentation.\" [Online]. Disponible: https://cloud.google.com/docs",
        "[4] Bareos Project, \"Bareos Documentation.\" [Online]. Disponible: https://docs.bareos.org/",
        "[5] PostgreSQL Global Development Group, \"PostgreSQL Documentation: High Availability and Replication.\" [Online]. Disponible: https://www.postgresql.org/docs/",
        "[6] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security management systems — Requirements,\" Geneva, 2022.")
    return r
