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
    "WLC01": "02-seguridad/omada_controller", "WMS01": "04-apps/wms", "WMS02": "04-apps/wms", "DB01": "04-apps/postgresql_ha", "DB02": "04-apps/postgresql_ha",
    "DW01": "04-apps/datawarehouse_bi", "BKP01": "05-respaldo/bareos_zfs", "NVR01": "05-respaldo/zoneminder_nvr",
    "ACS01": "Windows desde ISO (etapa 30)", "PAW01": "Windows desde ISO (etapa 30)", "PAW02": "Windows desde ISO (etapa 30)",
}


def contenido():
    r = Redactor()

    # ── 1 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Resumen ejecutivo")
    r.p("Este informe documenta cómo se implementó el centro de datos híbrido diseñado en el entregable S1_E2: el cluster Proxmox de cinco servidores con sus 27 máquinas virtuales, la extensión en Google Cloud, "
        "la gestión de identidades y accesos, el inventario final, la estrategia de respaldo y el monitoreo.")
    r.p("Como en el entregable de red, se distinguen los estados «Implementado» (existe y se desplegó), «Automatizado» (el rol está escrito y falta comprobarlo en el equipo) y «Pendiente».")
    r.tabla(["Componente", "Estado", "Evidencia"], [
        ["Red de los nodos Proxmox (bond0, vmbr1 y VLAN 70) y cluster PVE-COLOGISTIC", "Implementado", "Etapa 20, roles proxmox_red y proxmox_cluster"],
        ["Plantillas cloud-init Debian y Ubuntu y plantilla Windows Server 2022", "Implementado", "Rol proxmox_templates (plantillas 9000, 9001 y 9002)"],
        [f"{VM['n']} máquinas virtuales ({VM['linux']} Linux y {VM['windows']} Windows)", "Implementado", "Etapa 30 (Terraform) y etapa 40 (roles de servicios)"],
        ["Servicios: directorio, RADIUS, WMS, bases de datos, respaldo, monitoreo, telefonía, correo, videovigilancia", "Implementado", "Etapa 40; auditorías auditar_base y auditar_core"],
        ["VPC, VM de borde, firewall, ruta, buckets, cuentas de servicio y alerta en Google Cloud", "Implementado", "Estado de Terraform de la etapa 50 (19 recursos)"],
        ["Respaldo diario cifrado de PostgreSQL y copia al bucket", "Automatizado", "Rol bareos_zfs (tarea programada a las 02:00)"],
        ["Ejercicio de recuperación completo", "Pendiente", "Procedimiento y registro listos; sin ejecutar"],
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
        ["Núcleo", "Active Directory y DNS (DC1, DC2), FreeRADIUS (AAA01, AAA02), caché de paquetes y autoridad de certificados (INFRA01), archivos e impresión (FS01)"],
        ["Seguridad", "SIEM Wazuh (SIEM01), Zabbix (MON01), escáner de vulnerabilidades (VULN01), señuelo (HONEY01), bastión y bóveda de secretos (MGMT01), GLPI y Oxidized (ITSM01), controladora Wi-Fi (WLC01)"],
        ["Perímetro", "Proxy WAF (WAF01), SFTP para socios (SFTP01), telefonía (PBX01) y relé de correo (MAIL01)"],
        ["Aplicaciones", "WMS en Docker (WMS01, WMS02), PostgreSQL con réplica en flujo (DB01, DB02), almacén de datos y tableros (DW01)"],
        ["Respaldo", "Bareos con almacenamiento ZFS (BKP01) y videovigilancia con ZoneMinder (NVR01)"],
    ])

    # ── 4 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Implementación en la nube: Google Cloud")
    r.p("La etapa 50 de Terraform aplicó 19 recursos en el proyecto cologistic-cloud, región southamerica-west1. Es el equivalente en Google Cloud de la VPC, EC2, grupos de seguridad y reglas de red que pide la rúbrica de AWS.")
    r.tabla(["Concepto del diseño (equivalente AWS)", "Recurso desplegado", "Configuración"], [
        ["VPC (VPC)", "vpc-cologistic", "10.20.0.0/24"],
        ["Subredes (subredes)", "nube-borde, nube-tunel y nube-privada", "10.20.0.0/28, 10.20.0.16/29 y 10.20.0.32/28; la privada con acceso privado a las API de Google"],
        ["Instancia (EC2)", "gcp-borde", "e2-micro, southamerica-west1-a, IP 10.20.0.4, reenvío de IP; WireGuard y Nginx instalados al arrancar"],
        ["Dirección pública (Elastic IP)", "ip-gcp-borde", "Externa y estática, para el túnel"],
        ["Tabla de rutas", "ruta-a-datacenter", "10.20.0.x hacia 10.10.0.0/16 por la VM de borde"],
        ["Grupos de seguridad y ACL", "4 reglas de firewall", "WireGuard UDP 51820; todo el tráfico desde 10.10.0.0/16; SSH TCP 22 desde 10.10.70.0/24 y desde Google IAP; web TCP 80 y 443"],
        ["Almacenamiento (S3)", "2 buckets", "Respaldos (versionado y eliminación a los 90 días) y estado de Terraform (versionado); acceso uniforme"],
        ["IAM", "3 cuentas de servicio", "sa-respaldo (objectAdmin sobre el bucket de respaldos), sa-terraform y sa-logs"],
        ["Monitoreo (CloudWatch)", "Política de alerta y canal de correo", "CPU de gcp-borde mayor al 85 % durante 5 minutos"],
    ])
    r.fig("vpc.png", "Figura 4.1 — VPC de Google Cloud: subredes, VM de borde, túnel y bucket", ancho_cm=14)
    r.p("El estado de Terraform registra 22 aplicaciones sobre el proyecto (serie 22), que es la evidencia de los despliegues. El bucket del estado, distinto del de respaldos y con versionado, está creado para pasar a un backend remoto.")

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
    filas += [["GCP-BORDE, VPC, firewall, ruta y alerta", "southamerica-west1", "Google Cloud", "etapa 50: main.tf y estado de Terraform"],
              ["Buckets de respaldos y de estado", "southamerica-west1", "Cloud Storage", "etapa 50: main.tf"],
              ["Cuentas de servicio", "Google Cloud IAM", "IAM", "etapa 50: main.tf"]]
    r.tabla(["Activo", "Ubicación", "Sistema", "Evidencia de configuración"], filas)

    # ── 7 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Continuidad: respaldo, restauración y recuperación probada")
    r.h2("Estrategia de respaldo implementada")
    r.bullets(
        "Servidor BKP01: Bareos y almacenamiento ZFS con carpetas para PostgreSQL, configuraciones y Bareos; exporta el almacén por NFS a la gestión y a los servidores.",
        "Un script instalado por Ansible hace el respaldo cifrado de PostgreSQL (DB01) cada día a las 02:00 y lo sincroniza con el bucket de Google Cloud mediante rclone.",
        "Previsto en el diseño y por completar: respaldo de las máquinas virtuales con vzdump de Proxmox hacia el almacén de BKP01 por NFS.",
        "El bucket conserva versiones y elimina objetos a los 90 días; el estado de Terraform tiene su propio bucket.",
        "Redundancia local: réplica de PostgreSQL en flujo (DB02) y los pares de servicio en nodos distintos (D03).")
    r.h2("Ejercicio de recuperación")
    r.p("El ejercicio todavía no se ha ejecutado, así que los tiempos obtenidos están pendientes. Se ejecutará en una ventana acordada con este procedimiento, y sus resultados se anotarán en el registro del archivo Excel «Registro de prueba de recuperación».")
    r.tabla(["Paso", "Qué se hace"], [[str(i + 1), p] for i, p in enumerate(pd.PASOS_RECUPERACION)])
    r.tabla(["Servicio", "RTO objetivo", "RPO objetivo", "RTO obtenido", "RPO obtenido", "Evidencia"],
            [[s, rto, rpo, "Pendiente", "Pendiente", "Por adjuntar"] for s, rto, rpo in pd.RECUPERACION])

    # ── 8 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Monitoreo y control operativo del centro de datos")
    r.tabla(["Qué se monitorea", "Con qué", "Estado"], [
        ["CPU y memoria de las VM y los servicios", "Zabbix (MON01) con agentes y SNMP", "Desplegado; falta cargar los hosts"],
        ["Estado y capacidad de los nodos Proxmox", "Zabbix y la vista de recursos del cluster", "Pendiente: plantilla y alertas de capacidad"],
        ["Registros de seguridad", "Wazuh (SIEM01)", "Desplegado"],
        ["Instancia de la nube", "Cloud Monitoring: alerta de CPU mayor al 85 % durante 5 minutos, aviso por correo", "Implementado"],
        ["Cambios de configuración de los switches", "Oxidized (ITSM01)", "Desplegado"],
        ["Capacidad", "Asignación actual: 1,53 : 1 de CPU, 41,5 % de RAM y 39 % de disco", "Calculado en el modelo"],
    ])
    r.p("Pendiente: alertas de capacidad de los nodos (RAM libre menor al 20 %, disco mayor al 80 % y quórum del cluster) y una captura del panel como evidencia.")

    # ── 9 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Repositorio, control de versiones y reproducibilidad")
    r.bullets(
        "El repositorio cologistic-infra contiene el diseño versionado, la especificación generada, las cinco etapas (red, hipervisor, máquinas, servicios y nube) y los makefiles; el historial de Git registra cada cambio.",
        "Cada etapa declara lo que requiere y entrega (docs/contratos.md) y el README indica el orden de despliegue; con un entorno limpio se reconstruye con make.",
        "La validación del diseño y las pruebas (make verificar) fallan si la especificación no coincide con el diseño.",
        "Secretos: .env está fuera de Git. La revisión halló una contraseña de administrador de Windows en archivos del repositorio y como valor por defecto en scripts; debe rotarse y retirarse antes de entregar el repositorio.")

    # ── 10 ──────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conclusiones")
    r.bullets(
        f"El centro de datos está implementado según el diseño: cluster de cinco nodos, {VM['n']} máquinas con sus servicios y la extensión en Google Cloud con 19 recursos desplegados.",
        "Los cambios respecto al diseño están justificados; hay dos desviaciones de seguridad en la nube y una en Proxmox que tienen acción correctiva asignada.",
        "Quedan pendientes el ejercicio de recuperación, el MFA con su evidencia y las alertas de capacidad. No se declaran como hechos mientras no haya evidencia.")

    r.biblio(
        "[1] Proxmox Server Solutions GmbH, \"Proxmox VE Administration Guide.\" [Online]. Disponible: https://pve.proxmox.com/pve-docs/",
        "[2] HashiCorp, \"Terraform Documentation.\" [Online]. Disponible: https://developer.hashicorp.com/terraform/docs",
        "[3] Google Cloud, \"Compute Engine, VPC y Cloud Storage documentation.\" [Online]. Disponible: https://cloud.google.com/docs",
        "[4] Bareos Project, \"Bareos Documentation.\" [Online]. Disponible: https://docs.bareos.org/",
        "[5] PostgreSQL Global Development Group, \"PostgreSQL Documentation: High Availability and Replication.\" [Online]. Disponible: https://www.postgresql.org/docs/",
        "[6] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security management systems — Requirements,\" Geneva, 2022.")
    return r
