"""
pruebas_datos.py — Plan de pruebas de red (S2_E2) y registro de la prueba de recuperación (S2_E3), compartidos por el informe y por los XLSX.

El plan sale del diseño: cada caso positivo o negativo corresponde a una regla de pfSense, al túnel o a un control de detección.
La columna «Resultado obtenido» queda vacía y el estado en «Pendiente» hasta que se ejecute la prueba en el laboratorio: no se inventan resultados.
"""

# (ID, objetivo, precondición, pasos, resultado esperado, tipo)
PRUEBAS_RED = [
    ("T01", "El túnel WireGuard está arriba", "pfSense y GCP-BORDE con las claves intercambiadas", "En FW-MAIN: wg show; hacer ping a 10.20.0.17", "Último handshake reciente y respuesta de GCP-BORDE", "Positiva · VPN"),
    ("T02", "La ruta hacia la nube usa el túnel", "Túnel arriba", "Desde un servidor de la VLAN 30: traceroute a 10.20.0.4", "El salto pasa por el firewall y el túnel (10.20.0.x)", "Positiva · VPN"),
    ("T03", "El tráfico del túnel va cifrado", "Túnel arriba", "Capturar en la WAN de pfSense durante un ping a la nube", "Solo paquetes UDP 51820 cifrados; no aparece ICMP en claro", "Positiva · VPN"),
    ("T04", "Administración de la nube desde la VLAN 70", "Túnel y regla de la VPC", "Desde MGMT01: ssh a GCP-BORDE (10.20.0.4)", "Conexión permitida", "Positiva · VPN"),
    ("T05", "La administración de la nube desde otra VLAN se bloquea", "Túnel arriba", "Desde un equipo de la VLAN 10: ssh a 10.20.0.4", "Conexión denegada", "Negativa · VPN"),
    ("T06", "El puerto del túnel solo acepta el origen del centro de datos", "Regla de la VPC ajustada (hallazgo H02)", "Desde otra IP pública: enviar UDP 51820 a la IP de GCP-BORDE", "Descartado por el firewall de la VPC", "Negativa · VPN"),
    ("T07", "Internet bloqueado hacia el WMS privado", "WAF01 sin forwarding WMS y NAT 443 desactivado (Decisión D19)", "Desde fuera: curl -k https://IP-WAN o https://waf01.cologistic.net", "Conexión rechazada o HTTP 403 (WMS inaccesible desde Internet)", "Negativa · DMZ"),
    ("T08", "Internet llega al SFTP de socios", "NAT 22 hacia SFTP01", "Desde fuera: sftp con la cuenta de un socio de prueba", "Conexión permitida y enjaulada", "Positiva · DMZ"),
    ("T09", "Internet no llega a la red interna", "Política por defecto", "Desde fuera: nmap a una IP de servidor interno (por ejemplo 10.10.32.11)", "Sin respuesta", "Negativa · perímetro"),
    ("T10", "La DMZ no alcanza la base de datos", "Regla de bloqueo DMZ → BD", "Desde WAF01: nc -zv 10.10.32.10 5432", "Conexión denegada y registro en pfSense", "Negativa · DMZ"),
    ("T11", "La DMZ no alcanza la gestión", "Regla de bloqueo DMZ → VLAN 70", "Desde WAF01: ssh a 10.10.70.5", "Conexión denegada y registro", "Negativa · DMZ"),
    ("T12", "La DMZ (WAF01) no alcanza el WMS privado", "Regla WAF01 → SRV_WMS en state: absent", "Desde WAF01: curl -k https://10.10.31.10", "Conexión denegada por firewall (aislamiento DMZ → Apps)", "Negativa · DMZ"),
    ("T13", "Los terminales del almacén y Tailscale llegan a la VIP del WMS", "Regla VLAN 20 / Tailscale → VIP WMS (10.10.31.10)", "Desde la VLAN 20 o cliente Tailscale: curl -ks https://10.10.31.10/api/health/", "HTTP 200 JSON {\"status\": \"ok\", \"service\": \"wms-api\"}", "Positiva · segmentación"),
    ("T14", "Los terminales no llegan a la base de datos", "Regla de bloqueo VLAN 20 → BD", "Desde la VLAN 20: nc -zv 10.10.32.10 5432", "Conexión denegada", "Negativa · segmentación"),
    ("T15", "Solo el WMS llega a la VIP PostgreSQL HA (Patroni)", "Regla WMS → VIP BD (10.10.32.10)", "Desde WMS01/WMS02: nc -zv 10.10.32.10 5432", "Conexión permitida hacia el nodo primario Patroni activo", "Positiva · segmentación"),
    ("T16", "Los usuarios no llegan a la gestión", "Regla de bloqueo VLAN 10 → VLAN 70", "Desde la VLAN 10: ping y ssh a 10.10.70.5", "Sin respuesta y registro", "Negativa · segmentación"),
    ("T17", "Los usuarios no llegan a los respaldos", "Regla de bloqueo VLAN 10 → VLAN 120", "Desde la VLAN 10: nc -zv 10.10.120.11 9102", "Conexión denegada", "Negativa · segmentación"),
    ("T18", "Los invitados solo salen a Internet", "Regla VLAN 60", "Desde la VLAN 60: ping 10.10.10.10; curl https://ejemplo.com", "La red interna no responde; el sitio de Internet sí", "Negativa · segmentación"),
    ("T19", "Las cámaras no llegan a los servidores", "Regla de bloqueo VLAN 40", "Desde la VLAN 40: nc -zv 10.10.30.11 445", "Conexión denegada", "Negativa · segmentación"),
    ("T20", "El señuelo no llega a la red interna", "Regla HONEYPOT → internas", "Desde HONEY01: ping 10.10.30.11", "Sin respuesta; solo puede enviar al SIEM", "Negativa · segmentación"),
    ("T21", "El bastión administra los servidores", "Regla MGMT01 → servidores", "Desde MGMT01: ssh a DB01", "Conexión permitida", "Positiva · gestión"),
    ("T22", "Conmutación de los firewalls", "CARP activo", "Apagar FW-MAIN con un ping continuo hacia el gateway .1", "FW-BACKUP asume las IP virtuales; se mide el tiempo", "Positiva · alta disponibilidad"),
    ("T23", "El señuelo detecta una conexión", "OpenCanary en HONEY01, envío de syslog al SIEM", "Desde un servidor: curl http://10.10.130.10 y smbclient -L", "Alerta de OpenCanary visible en SIEM01", "Positiva · detección"),
    ("T24", "Un escaneo de puertos genera una alerta", "IDS/IPS implementado (pendiente, hallazgo H05)", "Desde la VLAN 10: nmap -sS a la VLAN 31", "Alerta del IDS en SIEM01", "Positiva · detección"),
    ("T25", "Los registros de pfSense llegan al SIEM", "Configuración de syslog hacia 10.10.34.20:514", "Generar un bloqueo (T14) y buscarlo en Wazuh", "El evento aparece con su origen y destino", "Positiva · registros"),
    ("T26", "Los switches envían su registro", "Syslog configurado en los switches (hallazgo H08)", "Cambiar una descripción de puerto y buscarla en Wazuh", "El evento aparece", "Positiva · registros"),
    ("T27", "Zabbix mide los switches", "SNMPv3 y regla MON01 → VLAN 70", "En Zabbix: ver las métricas de SW1-CORE1", "Se muestran utilización y estado de los puertos", "Positiva · monitoreo"),
    ("T28", "La nube avisa de saturación", "Alerta de CPU de Cloud Monitoring (CPU mayor a 85 % por 5 minutos)", "Generar carga en GCP-BORDE (stress) durante 6 minutos", "Llega un correo al canal de notificación", "Positiva · monitoreo"),
    ("T29", "Conmutación automática de PostgreSQL HA (Patroni + etcd)", "Patroni en DB01/DB02 + testigo etcd en INFRA01 + VIP 10.10.32.10", "Detener PostgreSQL/VM DB01 mientras se consulta db.cologistic.net:5432", "DB02 asume rol Primary automáticamente y conserva VIP 10.10.32.10", "Positiva · alta disponibilidad"),
    ("T30", "Acceso remoto resiliente vía Tailscale Cloud (gcp-borde)", "Subnet Router 10.20.0.0/24 en gcp-borde y 10.10.0.0/16 en pfSense", "Simular caída de pfSense/ISP local y acceder por Tailscale a 10.20.0.34", "Conectividad SSH/HTTPS hacia gcp-wms-drp operativa sin routers locales", "Positiva · nube DRP"),
]

# Registro de la prueba de recuperación (S2_E3): (servicio, RTO objetivo, RPO objetivo)
RECUPERACION = [
    ("PostgreSQL HA (Patroni DB01 -> DB02, VIP 10.10.32.10)", "15 minutos", "Segundos"),
    ("PostgreSQL + WMS en nube privada DRP (gcp-wms-drp desde GCS)", "4 horas", "1 hora (dump horario)"),
    ("DataWarehouse / Metabase HA (Patroni DW02 -> DW01, VIP 10.10.33.10)", "15 minutos", "Segundos"),
    ("Archivos compartidos FS01 (contingencia Samba en BKP01 vía rsync)", "15 minutos", "5 minutos"),
    ("Una VM sin par (por ejemplo MON01) desde vzdump", "8 horas", "24 horas"),
]

# Resultados reales medidos en el laboratorio (S2_E3 XLSX y DOCX):
# (fecha_hora_falla, restablecido_a_las, rto_obtenido, rpo_obtenido, estado)
RECUPERACION_EJECUCION = [
    ("2026-11-17 20:05:59", "2026-11-17 20:06:06", "6.96 s (Leader TL 6 + VIP .32.10)", "0 s (Lag = 0 MB)", "Cumple el objetivo"),
    ("2026-11-17 20:26:34", "2026-11-17 20:26:51", "17 s (restore + Docker + HTTP 200)", "<= 1 h (5,816 líneas SQL GCS)", "Cumple el objetivo"),
    ("2026-11-17 20:13:44", "2026-11-17 20:13:51", "7.23 s (Leader TL 11 + Metabase 200)", "0 s (Lag = 0 MB)", "Cumple el objetivo"),
    ("2026-11-17 20:19:55", "2026-11-17 20:20:05", "< 1 min (recurso BKP01 activo)", "<= 5 min (cron rsync c/5 min)", "Cumple el objetivo"),
    ("2026-11-04 09:00:00", "2026-11-04 10:15:20", "1 h 15 min 20 s (qmrestore BKP01)", "9 horas (Snapshot ZFS)", "Cumple el objetivo"),
]

PASOS_RECUPERACION = [
    "Tomar nota de la hora y del último respaldo (fecha del dump horario en el bucket Cloud Storage / ZFS).",
    "Simular la pérdida del servicio: detener la VM o el servicio en producción (en la ventana acordada).",
    "Restaurar: en la nube, encender gcp-wms-drp y ejecutar activar_contingencia_drp.sh (descarga dump de GCS, obtiene secretos de Secret Manager y levanta imágenes de Artifact Registry); en sitio, validar promoción automática Patroni + VIP o habilitar recurso Samba de contingencia en BKP01.",
    "Verificar: conteo de filas en DB, respuesta HTTP 200 en /api/health/ y consulta de prueba desde WMS.",
    "Medir el RTO (desde la falla hasta el servicio funcionando) y el RPO (hora del último dato recuperado frente a la hora de la falla).",
    "Guardar la evidencia: salida de los comandos y capturas, sin contraseñas.",
]
