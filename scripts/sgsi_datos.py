"""
sgsi_datos.py — Inventario de activos, matriz de riesgos (ISO/IEC 27005) y Declaración de Aplicabilidad (ISO/IEC 27001:2022, Anexo A)
de Co-Logistic S.A.C. El inventario sale de los datos reales del diseño (datos.py); riesgos y SoA son el análisis del equipo.

Estados de implementación de la SoA (según la evidencia del repositorio cologistic-infra, a la fecha del informe):
  Implementado  existe en el repositorio y se desplegó (commits, tfstate, scripts de auditoría)
  Parcial       existe una parte; falta otra (se dice cuál)
  Planificado   diseñado, sin implementar
  No aplica     excluido con justificación
"""
import datos

NIVELES = [(20, "Crítico"), (13, "Alto"), (7, "Medio"), (1, "Bajo")]


def nivel(impacto, probabilidad):
    valor = impacto * probabilidad
    return valor, next(n for umbral, n in NIVELES if valor >= umbral)


# ── Inventario de activos ────────────────────────────────────────────────────────────────────────────────────────
# (C, I, D) en escala 1 a 3 (bajo, medio, alto); la clasificación sale del mayor
CLASIFICACION = {3: "Confidencial", 2: "Interna", 1: "Pública"}

PROPIETARIO = {"infra": "Responsable de Infraestructura", "apps": "Responsable de Aplicaciones", "seg": "Responsable de Seguridad",
               "datos": "Responsable de Datos", "red": "Responsable de Redes", "ti": "Jefatura de TI"}

INFORMACION = [
    ("Datos transaccionales del WMS (stock, ubicaciones, pedidos)", "datos", "DB01 y DB02 (HV4 y HV-MAIN)", 3, 3, 3),
    ("Identidades y credenciales (Active Directory, RADIUS, bóveda de secretos)", "seg", "DC1, DC2, AAA01, AAA02, MGMT01", 3, 3, 3),
    ("Copias de respaldo (locales y en la nube)", "datos", "BKP01 y bucket de Cloud Storage", 3, 2, 3),
    ("Registros y eventos de seguridad", "seg", "SIEM01 (Wazuh), MON01 (Zabbix)", 2, 3, 2),
    ("Configuración de la red y la infraestructura como código", "red", "Repositorio Git, Oxidized (ITSM01)", 3, 3, 2),
    ("Video de vigilancia", "seg", "NVR01", 2, 2, 2),
    ("Archivos de usuarios y documentos de oficina", "apps", "FS01", 2, 2, 2),
    ("Datos analíticos y reportes", "datos", "DW01", 2, 2, 1),
    ("Secretos de operación (.env, claves de servicio, claves del túnel)", "seg", "Estaciones PAW01/02, Vaultwarden, repositorio", 3, 3, 2),
]

# VM: (propietario, C, I, D)
VM_CID = {
    "DC1": ("seg", 3, 3, 3), "DC2": ("seg", 3, 3, 3), "AAA01": ("seg", 3, 3, 2), "AAA02": ("seg", 3, 3, 2),
    "WMS01": ("apps", 2, 3, 3), "WMS02": ("apps", 2, 3, 3), "DB01": ("datos", 3, 3, 3), "DB02": ("datos", 3, 3, 3),
    "DW01": ("datos", 2, 2, 1), "BKP01": ("datos", 3, 2, 3), "WAF01": ("seg", 2, 2, 2), "SFTP01": ("apps", 3, 2, 2),
    "SIEM01": ("seg", 2, 3, 2), "VULN01": ("seg", 2, 2, 1), "MON01": ("infra", 1, 2, 2), "ITSM01": ("infra", 2, 2, 1),
    "INFRA01": ("infra", 2, 3, 2), "FS01": ("apps", 2, 2, 2), "MGMT01": ("seg", 3, 3, 2), "PBX01": ("apps", 1, 2, 2),
    "MAIL01": ("apps", 2, 2, 1), "NVR01": ("seg", 2, 2, 2), "WLC01": ("red", 1, 2, 2), "ACS01": ("seg", 2, 3, 2),
    "HONEY01": ("seg", 1, 2, 1), "PAW01": ("ti", 3, 3, 1), "PAW02": ("ti", 3, 3, 1),
}

EQUIPOS = [
    ("Router-Cisco (C1111-4P)", "red", "Rack R1 · U21", 2, 3, 3),
    ("FW-MAIN y FW-BACKUP (pfSense CE)", "red", "Sala de servidores (torres)", 3, 3, 3),
    ("SW1-CORE1 y SW2-CORE2 (C9300L)", "red", "Rack R1 · U1 y U2", 2, 3, 3),
    ("SW3-DIST1 y SW4-DIST2 (C9200L)", "red", "Rack R1 · U3 y U4", 2, 3, 3),
    ("SW5-ACCESO (C1000)", "red", "Rack R1 · U5", 1, 2, 2),
    ("SW6-TOR2 y SW7-TOR1 (C1000)", "red", "Rack R1 · U6 y U7", 2, 3, 3),
    ("AP1-WIFI (Cisco AIR-SAP1602I)", "red", "Techo de la sala", 1, 2, 2),
]


def inventario():
    """[(ID, activo, tipo, propietario, ubicación, criticidad, C, I, D, clasificación)]"""
    filas, n = [], 0

    def agregar(activo, tipo, dueno, ubic, c, i, d):
        nonlocal n
        n += 1
        mayor = max(c, i, d)
        crit = {3: "Crítica", 2: "Alta", 1: "Media"}[mayor]
        filas.append((f"A{n:02d}", activo, tipo, PROPIETARIO[dueno], ubic, crit, c, i, d, CLASIFICACION[max(c, 1)]))

    for activo, dueno, ubic, c, i, d in INFORMACION:
        agregar(activo, "Información", dueno, ubic, c, i, d)
    for activo, dueno, ubic, c, i, d in EQUIPOS:
        agregar(activo, "Equipo de red", dueno, ubic, c, i, d)
    for nodo, r in datos.hipervisores().items():
        agregar(f"{nodo} (Proxmox VE, Dell Precision)", "Servidor físico", "infra", "Sala de servidores (torre)", 2, 3, 3)
    for nombre, d in sorted(datos.VMS.items(), key=lambda kv: (kv[1]["nodo"], kv[0])):
        dueno, c, i, dd = VM_CID[nombre]
        agregar(f"{nombre} ({d.get('rol') or '—'})", "VM Windows" if "Windows" in d["so"] else "VM Linux", dueno, f"{d['nodo']} · {d.get('ip', '—')}", c, i, dd)
    agregar("VPC-COLOGISTIC y GCP-BORDE (Google Cloud)", "Servicio en la nube", "infra", "southamerica-west1", 2, 3, 2)
    agregar("Bucket de respaldos (Cloud Storage)", "Servicio en la nube", "datos", "southamerica-west1", 3, 2, 3)
    agregar("Bucket del estado de Terraform", "Servicio en la nube", "infra", "southamerica-west1", 3, 3, 2)
    agregar("Cuentas de servicio de Google Cloud (respaldo, Terraform, registros)", "Identidad", "seg", "Google Cloud IAM", 3, 3, 2)
    return filas


# ── Matriz de riesgos ────────────────────────────────────────────────────────────────────────────────────────────
# (ID, activo, amenaza, vulnerabilidad, impacto 1-5, probabilidad 1-5, tratamiento, controles, impacto residual, probabilidad residual)
RIESGOS = [
    ("R01", "FS01, DB01 y estaciones", "Ransomware que cifra archivos y bases de datos", "Usuarios con salida web amplia; sin protección de punto final en el diseño", 5, 3,
     "Mitigar", "A.8.22, A.8.13, A.8.16, A.8.7", 5, 2),
    ("R02", "FW-MAIN", "Falla del firewall principal", "Un solo punto de paso entre zonas hasta validar CARP", 5, 2, "Mitigar", "A.8.14", 5, 1),
    ("R03", "HV-MAIN, HV1 a HV4", "Falla de un servidor Proxmox", "Sin almacenamiento compartido: las VM no se reinician solas", 4, 3, "Mitigar", "A.8.14, A.8.13, A.5.30", 3, 2),
    ("R04", "Secretos de operación", "Uso indebido de credenciales de administración", "Contraseña de administrador escrita en archivos del repositorio y en scripts; .env en texto plano", 5, 4,
     "Mitigar", "A.5.17, A.8.5, A.8.2", 5, 2),
    ("R05", "WAF01 y SFTP01", "Ataque desde Internet a los servicios publicados", "Servicios expuestos en la DMZ; certificado TLS autofirmado", 4, 3, "Mitigar", "A.8.20, A.8.22, A.8.8", 4, 2),
    ("R06", "Red de usuarios", "Movimiento lateral hacia servidores y bases de datos", "Equipos de usuario en la misma red que los servidores si no hay segmentación", 5, 3, "Mitigar", "A.8.22, A.8.20", 5, 1),
    ("R07", "VLAN 70 y bastión MGMT01", "Acceso no autorizado a la administración", "Una sola puerta de administración; el MFA depende de configurarlo", 5, 2, "Mitigar", "A.5.15, A.8.2, A.8.5", 5, 1),
    ("R08", "Túnel WireGuard", "Interceptación o suplantación del túnel", "Claves estáticas de larga duración", 4, 2, "Mitigar", "A.8.24, A.5.23", 4, 1),
    ("R09", "GCP-BORDE", "Ataque directo a la VM de borde", "UDP 51820 abierto a cualquier origen y cuenta de servicio por defecto en la instancia", 4, 3, "Mitigar", "A.5.23, A.8.20, A.8.2", 4, 1),
    ("R10", "BKP01 y bucket de respaldos", "Respaldo dañado o imposible de restaurar", "Restauración no probada todavía", 5, 3, "Mitigar", "A.8.13, A.5.30", 5, 2),
    ("R11", "Sede completa", "Desastre físico (incendio, inundación, robo)", "Todos los servidores en una sola sala", 5, 2, "Mitigar", "A.5.29, A.5.30, A.7.5", 4, 1),
    ("R12", "Enlaces a Internet", "Corte de un proveedor", "Dependencia de la salida a Internet", 3, 3, "Mitigar", "A.8.14, A.8.21", 3, 1),
    ("R13", "Toda la red", "Intrusión sin detectar", "IDS/IPS aún sin implementar; registros solo si los equipos los envían", 4, 3, "Mitigar", "A.8.15, A.8.16, A.5.7", 4, 2),
    ("R14", "Sala de servidores", "Acceso físico no autorizado", "Torres sin gabinete cerrado; control de acceso por definir", 4, 2, "Mitigar", "A.7.1, A.7.2, A.7.4", 4, 1),
    ("R15", "VLAN 60, 40 y 110", "Dispositivos de invitados o IoT comprometidos", "Dispositivos con poco control del fabricante", 3, 3, "Mitigar", "A.8.22", 3, 1),
    ("R16", "Switches C1000", "Ataque al acceso SSH", "Solo ofrece algoritmos SSH antiguos", 3, 2, "Aceptar", "A.8.5, A.8.22", 3, 2),
    ("R17", "Toda la infraestructura", "Cambio de configuración sin control", "Cambios manuales en equipos", 4, 3, "Mitigar", "A.8.9, A.8.32", 4, 2),
    ("R18", "DB01 y SFTP01", "Fuga de datos personales o comerciales", "Datos de socios y de clientes en la base y el intercambio de archivos", 4, 2, "Mitigar", "A.5.34, A.8.24, A.8.3", 4, 1),
    ("R19", "Sala de servidores", "Corte de energía o falla de climatización", "El diseño no incluye UPS ni climatización de precisión", 4, 2, "Mitigar", "A.7.11, A.7.5", 3, 1),
    ("R20", "Terraform y Ansible", "Token de API con más permisos de los necesarios", "El token de Terraform en Proxmox tiene el rol Administrador sobre todo el cluster", 4, 3, "Mitigar", "A.8.2, A.5.15", 4, 1),
]


def riesgos():
    filas = []
    for rid, activo, amenaza, vuln, i, p, trat, ctrl, ri, rp in RIESGOS:
        v, n = nivel(i, p)
        vr, nr = nivel(ri, rp)
        filas.append((rid, activo, amenaza, vuln, i, p, v, n, trat, ctrl, ri, rp, vr, nr))
    return filas


# ── Declaración de Aplicabilidad (SoA) ───────────────────────────────────────────────────────────────────────────
I, P, PL, NA = "Implementado", "Parcial", "Planificado", "No aplica"
# (código, control, estado, justificación y evidencia)
SOA = [
    ("A.5.1", "Políticas de seguridad de la información", PL, "Política general del SGSI redactada en este informe; falta su aprobación formal por la dirección."),
    ("A.5.2", "Roles y responsabilidades de seguridad de la información", PL, "Roles definidos en este informe; falta asignar personas."),
    ("A.5.3", "Segregación de funciones", P, "Administración desde bastión y cuentas separadas por herramienta; falta la matriz de aprobaciones."),
    ("A.5.4", "Responsabilidades de la dirección", PL, "Revisión por la dirección planificada (sección de monitoreo)."),
    ("A.5.5", "Contacto con las autoridades", PL, "Lista de contactos del procedimiento de incidentes."),
    ("A.5.6", "Contacto con grupos de interés especial", NA, "Excluido: el proyecto no participa en grupos sectoriales."),
    ("A.5.7", "Inteligencia de amenazas", PL, "Wazuh y las reglas del IDS recibirán fuentes de amenazas al implementar el IDS."),
    ("A.5.8", "Seguridad de la información en la gestión de proyectos", I, "Cada etapa del repositorio declara lo que requiere y entrega (docs/contratos.md)."),
    ("A.5.9", "Inventario de información y otros activos asociados", I, "Inventario de activos de este informe, generado desde el modelo (diseno/ y especificacion/)."),
    ("A.5.10", "Uso aceptable de la información y otros activos", PL, "Política de uso aceptable de este informe."),
    ("A.5.11", "Devolución de activos", NA, "Excluido: no hay personal que devuelva activos en el alcance del proyecto."),
    ("A.5.12", "Clasificación de la información", I, "Clasificación Confidencial, Interna o Pública en el inventario."),
    ("A.5.13", "Etiquetado de la información", PL, "Se etiquetarán los documentos con su clasificación."),
    ("A.5.14", "Transferencia de información", P, "SFTP enjaulado por socio y túnel cifrado a la nube; falta el acuerdo con socios."),
    ("A.5.15", "Control de acceso", P, "146 reglas de pfSense por zona (rol pfsense_base); reglas escritas, pruebas de permitido y denegado pendientes."),
    ("A.5.16", "Gestión de identidades", I, "Active Directory (DC1, DC2) con unidades organizativas; scripts de auditoría de AD."),
    ("A.5.17", "Información de autenticación", P, "Bóveda de secretos (Vaultwarden); pero hay una contraseña de administrador en archivos del repositorio (ver hallazgo H01)."),
    ("A.5.18", "Derechos de acceso", P, "Matriz de accesos por rol definida; falta revisarla periódicamente."),
    ("A.5.19", "Seguridad de la información en las relaciones con proveedores", PL, "Política de proveedores y nube de este informe."),
    ("A.5.20", "Tratamiento de la seguridad en los acuerdos con proveedores", PL, "Revisar los términos de Google Cloud y de los proveedores de Internet."),
    ("A.5.21", "Gestión de la seguridad en la cadena de suministro de las TIC", P, "Paquetes por proxy local con caché (apt-cacher-ng); imágenes de Docker por revisar."),
    ("A.5.22", "Seguimiento, revisión y gestión de cambios de los servicios de proveedores", PL, "Se revisarán las alertas de Google Cloud cada trimestre."),
    ("A.5.23", "Seguridad de la información para el uso de servicios en la nube", I, "VPC con rutas y firewall, cuentas de servicio con permisos acotados, buckets con versionado (Terraform, etapa 50)."),
    ("A.5.24", "Planificación y preparación de la gestión de incidentes de seguridad", PL, "Procedimiento de incidentes de este informe."),
    ("A.5.25", "Evaluación y decisión sobre eventos de seguridad", PL, "Criterios de severidad en el procedimiento de incidentes; los eventos llegan a SIEM01."),
    ("A.5.26", "Respuesta a incidentes de seguridad", PL, "Procedimiento de incidentes."),
    ("A.5.27", "Aprendizaje de los incidentes de seguridad", PL, "Revisión posterior a cada incidente."),
    ("A.5.28", "Recopilación de evidencias", P, "Registros centralizados en SIEM01; falta el procedimiento de custodia."),
    ("A.5.29", "Seguridad de la información durante una interrupción", PL, "Plan de continuidad con RTO y RPO por servicio."),
    ("A.5.30", "Preparación de las TIC para la continuidad del negocio", P, "Respaldo diario a las 02:00 con copia cifrada al bucket; recuperación sin probar."),
    ("A.5.31", "Requisitos legales, estatutarios, regulatorios y contractuales", PL, "Ley N.° 29733 de protección de datos personales y su reglamento."),
    ("A.5.32", "Derechos de propiedad intelectual", PL, "Uso de software con licencia o de código abierto (Proxmox sin suscripción, Debian, Windows con licencia)."),
    ("A.5.33", "Protección de registros", P, "Respaldo versionado y retención de 90 días en el bucket; falta la política de retención de los registros."),
    ("A.5.34", "Privacidad y protección de datos personales (DCP)", PL, "Política de ética y manejo de datos de este informe."),
    ("A.5.35", "Revisión independiente de la seguridad de la información", PL, "Auditoría interna de este informe; auditoría externa por decidir."),
    ("A.5.36", "Cumplimiento de políticas, reglas y normas de seguridad", I, "Validación automática del diseño (make verificar) y pruebas del repositorio."),
    ("A.5.37", "Procedimientos operativos documentados", I, "docs/despliegue.md, docs/contratos.md y guías en guias/."),
    ("A.6.1", "Selección de personal", NA, "Excluido: el proyecto no gestiona la contratación."),
    ("A.6.2", "Términos y condiciones de empleo", NA, "Excluido por la misma razón que A.6.1."),
    ("A.6.3", "Concienciación, educación y formación en seguridad", PL, "Plan de concienciación para usuarios y para el equipo de TI."),
    ("A.6.4", "Proceso disciplinario", NA, "Excluido: lo define la organización, no el proyecto."),
    ("A.6.5", "Responsabilidades después del cese o cambio de empleo", PL, "Baja de cuentas en Active Directory, Vaultwarden y bastión (política de accesos)."),
    ("A.6.6", "Acuerdos de confidencialidad o no divulgación", PL, "Declaración ética firmada por el equipo."),
    ("A.6.7", "Trabajo remoto", P, "Acceso remoto de administración por Tailscale y VPN de pfSense; falta la política de trabajo remoto."),
    ("A.6.8", "Notificación de eventos de seguridad de la información", PL, "Canal y formato del procedimiento de incidentes."),
    ("A.7.1", "Perímetros de seguridad física", PL, "Sala de servidores con acceso restringido; falta el gabinete para las torres."),
    ("A.7.2", "Entrada física", PL, "Control de acceso con lectores (ACS01); falta instalarlos."),
    ("A.7.3", "Seguridad de oficinas, despachos e instalaciones", NA, "Excluido: oficinas fuera del alcance técnico."),
    ("A.7.4", "Monitoreo de seguridad física", PL, "Cámaras y grabador NVR01 (ZoneMinder)."),
    ("A.7.5", "Protección contra amenazas físicas y ambientales", PL, "Pendiente: extintor, climatización y detección de agua."),
    ("A.7.6", "Trabajo en áreas seguras", PL, "Se incluye en la política de uso aceptable."),
    ("A.7.7", "Escritorio y pantalla limpios", PL, "Se incluye en la política de uso aceptable."),
    ("A.7.8", "Emplazamiento y protección de los equipos", P, "Rack de 24U con 16 U libres; los servidores en torre quedan fuera de rack."),
    ("A.7.9", "Seguridad de los activos fuera de las instalaciones", I, "Los activos fuera de la sede son los de la nube (control A.5.23)."),
    ("A.7.10", "Medios de almacenamiento", PL, "Se incluye la eliminación segura en la política de proveedores."),
    ("A.7.11", "Servicios de suministro", PL, "Pendiente: UPS (ver riesgo R19)."),
    ("A.7.12", "Seguridad del cableado", I, "12 port-channels LACP cableados, cada puerto etiquetado con el equipo del otro extremo."),
    ("A.7.13", "Mantenimiento de los equipos", P, "Actualizaciones de Proxmox por repositorio; los switches con versiones distintas de IOS."),
    ("A.7.14", "Eliminación o reutilización segura de los equipos", PL, "Borrado seguro antes de reutilizar (write erase y reinstalación)."),
    ("A.8.1", "Dispositivos de punto final del usuario", P, "Estaciones de administración (PAW01 y PAW02) y dominio; sin EDR."),
    ("A.8.2", "Derechos de acceso privilegiado", P, "Administración por bastión; el token de Terraform tiene el rol Administrador (hallazgo H03)."),
    ("A.8.3", "Restricción del acceso a la información", I, "Reglas de bloqueo explícito de usuarios hacia datos, gestión y respaldos."),
    ("A.8.4", "Acceso al código fuente", I, "Repositorios privados con control de versiones."),
    ("A.8.5", "Autenticación segura", P, "AD y RADIUS (802.1X) con acceso a switches; los C1000 solo ofrecen algoritmos SSH antiguos."),
    ("A.8.6", "Gestión de la capacidad", P, "Dimensionamiento del entregable S1_E2 (1,53 : 1 de CPU) y alerta de CPU en Google Cloud; Zabbix desplegado, con sus alertas por configurar."),
    ("A.8.7", "Protección contra el malware", PL, "Sin protección de punto final gestionada (EDR); el WAF filtra el tráfico web con ModSecurity."),
    ("A.8.8", "Gestión de las vulnerabilidades técnicas", P, "Escáner Greenbone (VULN01) desplegado; falta la rutina de escaneo y parcheo."),
    ("A.8.9", "Gestión de la configuración", I, "diseno/, especificacion/ y etapas/ en Git; Oxidized guarda las configuraciones de los switches."),
    ("A.8.10", "Eliminación de la información", PL, "Retención de 90 días en el bucket de respaldos."),
    ("A.8.11", "Enmascaramiento de datos", NA, "Excluido: no hay desarrollo con datos reales."),
    ("A.8.12", "Prevención de fuga de datos", P, "Segmentación y bloqueo de salida; sin herramienta de prevención de fuga."),
    ("A.8.13", "Copia de seguridad de la información", P, "Bareos y vzdump; copia diaria cifrada de PostgreSQL al bucket; recuperación sin probar."),
    ("A.8.14", "Redundancia de las instalaciones de procesamiento", P, "Doble ToR, 12 port-channels, pares de servicios en hipervisores distintos, cluster Proxmox; CARP pendiente."),
    ("A.8.15", "Registro", P, "SIEM01 recibe syslog (UDP 514); pfSense y OpenCanary tienen configurado el envío. Falta configurarlo en los switches."),
    ("A.8.16", "Actividades de seguimiento", P, "Wazuh (SIEM01) y Zabbix (MON01) desplegados; faltan los paneles y las alertas."),
    ("A.8.17", "Sincronización de relojes", I, "Las reglas de pfSense permiten NTP hacia los controladores de dominio."),
    ("A.8.18", "Uso de programas de utilidad privilegiados", PL, "Se incluye en la política de accesos."),
    ("A.8.19", "Instalación de software en sistemas operativos", I, "El software se instala con roles de Ansible, desde la caché local de paquetes (apt-cacher-ng)."),
    ("A.8.20", "Seguridad de las redes", P, "Switches configurados y verificados; firewall escrito, pruebas pendientes."),
    ("A.8.21", "Seguridad de los servicios de red", P, "Doble proveedor de Internet y conmutación en pfSense."),
    ("A.8.22", "Segregación de las redes", I, "18 VLAN en 12 zonas, nativa 999, puertos sin uso apagados; reglas por zona."),
    ("A.8.23", "Filtrado web", NA, "Excluido: salida web permitida por puerto a los usuarios; sin proxy."),
    ("A.8.24", "Uso de la criptografía", P, "SSH v2, WireGuard hacia la nube, TLS en los servicios; certificados autofirmados por reemplazar con step-ca."),
    ("A.8.25", "Ciclo de vida de desarrollo seguro", NA, "Excluido: el WMS lo desarrolla Ingeniería de Software."),
    ("A.8.26", "Requisitos de seguridad de las aplicaciones", P, "El WMS se publica detrás de un WAF con reglas OWASP CRS."),
    ("A.8.27", "Arquitectura de sistemas seguros y principios de ingeniería", I, "Mínimo privilegio, defensa en profundidad y denegación por defecto (entregable S1_E1)."),
    ("A.8.28", "Codificación segura", NA, "Excluido: el proyecto no desarrolla aplicaciones."),
    ("A.8.29", "Pruebas de seguridad en el desarrollo y la aceptación", P, "Plan de pruebas del entregable S2_E2; sin ejecutar todavía."),
    ("A.8.30", "Desarrollo externalizado", NA, "Excluido: sin desarrollo externalizado."),
    ("A.8.31", "Separación de los entornos de desarrollo, prueba y producción", P, "Pruebas con Terraform plan y Ansible --check antes de aplicar."),
    ("A.8.32", "Gestión de cambios", I, "Cambios por Git y revisión; validación automática antes de aplicar."),
    ("A.8.33", "Información de prueba", NA, "Excluido: sin datos reales en pruebas."),
    ("A.8.34", "Protección de los sistemas de información durante las pruebas de auditoría", PL, "Las pruebas se hacen en ventana acordada y con alcance ético."),
]


def soa():
    return SOA


def resumen_soa():
    cuenta = {}
    for _, _, e, _ in SOA:
        cuenta[e] = cuenta.get(e, 0) + 1
    return cuenta


if __name__ == "__main__":
    print(len(inventario()), "activos;", len(riesgos()), "riesgos;", len(SOA), "controles", resumen_soa())
    for r in riesgos():
        print(r[0], r[6], r[7], "->", r[12], r[13])
