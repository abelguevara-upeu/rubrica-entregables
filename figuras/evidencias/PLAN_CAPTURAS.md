# Plan de Capturas de Evidencia Web — Co-Logistic S.A.C.

> **Carpeta de salida:** `rubrica-entregables/figuras/evidencias/`  
> **Convención estricta de nombres:** `<entregable>_sec<NN>_<orden>_<slug>.png`  
> Donde `<entregable>` es `s2_e1`, `s2_e2` o `s2_e3` y `sec<NN>` es el número exacto de sección H1 del generador Python (`scripts/generar_s2_e*.py`) donde se incrustará la imagen automáticamente.
>
> **Contexto técnico previo:** leer `cologistic-infra/CONTEXTO-PROYECTO.md` y `rubrica-entregables/README.md`.

---

## Reglas Obligatorias para Claude (Chrome MCP)

1. **SOLO LECTURA:** No cambiar configuraciones, no apagar servicios ni hacer clics destructivos.
2. **CERO SECRETOS EN PANTALLA (bloqueante de rúbrica):**
   - Nunca mostrar contraseñas, tokens API, códigos QR TOTP, llaves privadas, cookies ni `/admin` de Vaultwarden con token visible.
   - Si una página solicita login o 2FA, **detente y pide al usuario que inicie sesión manualmente**; luego continúa.
3. **Formato y actualización:**
   - Ventana limpia (`1440x900`), sin popups ni barras innecesarias.
   - Guardar cada PNG **exactamente** con el nombre de la columna `Archivo` dentro de `rubrica-entregables/figuras/evidencias/`.
   - Al terminar cada bloque, marcar `[x]` en la columna `Estado` de este mismo archivo y reportar confirmación de `0 secretos visibles`.

---

## Bloque 1 — Entregable `S2_E2` (Red, pfSense HA, Suricata, Wazuh y Oxidized · 13 capturas)

### Sección 3 (`sec03`): Conectividad híbrida implementada: VPN y enrutamiento
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e2_sec03_01_pfsense_carp_services.png` | `https://pfsense.cologistic.net` | **Status → CARP** y **Status → Services** (Tailscale, Suricata, DHCP activos) | Estado CARP HA y servicios VPN/IDS activos en pfSense-MAIN |
| `[ ]` | `s2_e2_sec03_02_gcp_vpc_rutas.png` | `https://console.cloud.google.com/networking/routes/list?project=cologistic-cloud` | **Routes** mostrando `ruta-a-datacenter` (`10.10.0.0/16 -> 10.20.0.4`) | Ruta estática híbrida `ruta-a-datacenter` en `vpc-cologistic` |

### Sección 4 (`sec04`): Seguridad perimetral implementada: firewall, DMZ y segmentación
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e2_sec04_01_pfsense_dashboard.png` | `https://pfsense.cologistic.net` | **Status → Dashboard** (pfSense CE 2.9.0, interfaces VLAN, CPU/RAM) | Panel general de pfSense CE 2.9.0 HA (`pfSense-MAIN`) |
| `[ ]` | `s2_e2_sec04_02_pfsense_rules_vlan10.png` | `https://pfsense.cologistic.net` | **Firewall → Rules → ADMINISTRACION (VLAN 10)** mostrando bloqueo hacia VLAN 70 | Reglas de segmentación en VLAN 10 con denegación hacia VLAN 70 |
| `[ ]` | `s2_e2_sec04_03_pfsense_rules_dmz.png` | `https://pfsense.cologistic.net` | **Firewall → Rules → DMZ (VLAN 80)** mostrando aislamiento hacia WMS/DB/VLAN 70 | Aislamiento perimetral de DMZ (VLAN 80) en pfSense HA |
| `[ ]` | `s2_e2_sec04_04_pfsense_rules_vlan70.png` | `https://pfsense.cologistic.net` | **Firewall → Rules → GESTION_TI (VLAN 70)** (flujos acotados a AD/SIEM/Zabbix) | Reglas de mínimo privilegio en VLAN 70 (`GESTION_TI`) |

### Sección 5 (`sec05`): IDS/IPS, honeypot y detección implementados
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e2_sec05_01_pfsense_suricata_ids.png` | `https://pfsense.cologistic.net` | **Services → Suricata → Interfaces + Alerts** (`em0.31`, firma `SID 9000001`) | Sensor Suricata IDS 8.0.7 activo en `em0.31` con alertas registradas |
| `[ ]` | `s2_e2_sec05_02_wazuh_alerta_t24.png` | `https://wazuh.cologistic.net` | **Threat Hunting** (`Last 24h`, `rule.id: 100120`) con detalle expandido (`T24`, `MITRE T1046`) | Alerta correlacionada Wazuh `100120` (Suricata `SID 9000001`, prueba T24) |
| `[ ]` | `s2_e2_sec05_03_wazuh_tuning_100121.png` | `https://wazuh.cologistic.net` | **Threat Hunting** (`Last 15 min`, `rule.id: 100120`) en **0 resultados** | Eliminación de falsos positivos tras SIEM tuning `100121` (ISO 27001 A.8.16) |

### Sección 6 (`sec06`): Monitoreo, registros y visibilidad de red
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e2_sec06_01_wazuh_overview.png` | `https://wazuh.cologistic.net` | **Overview** (`Active: 3`, `Disconnected: 0`) | Panel general de Wazuh SIEM v4.9.2 en `SIEM01` |
| `[ ]` | `s2_e2_sec06_02_oxidized_7_switches.png` | `https://oxidized.cologistic.net` | Lista principal con los **7/7 switches Cisco en `success`** (`SW1-CORE1`..`SW7-TOR1`) | Respaldo automático en Git de los 7 switches Cisco en Oxidized (`ITSM01`) |
| `[ ]` | `s2_e2_sec06_03_oxidized_remove_secret.png` | `https://oxidized.cologistic.net` | Config de `SW1-CORE1` mostrando `<secret hidden>` (`remove_secret: true`) | Sanitización automática de credenciales (`<secret hidden>`) en Oxidized |
| `[ ]` | `s2_e2_sec06_04_guacamole_ssh_switch.png` | `https://guacamole.cologistic.net` | Sesión SSH web en `SW1-CORE1` o **Settings → History** con grabación de sesión | Administración SSH web mediante bastión Guacamole con grabación forense |

---

## Bloque 2 — Entregable `S2_E1` (SGSI, IAM, Incidentes GLPI y Auditoría · 9 capturas)

*(Nota: `glpi_ordenadores.png`, `glpi_red.png` y `glpi_problemas.png` ya existen en `figuras/`).*

### Sección 7 (`sec07`): Gobernanza de identidades, accesos y protección de datos
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e1_sec07_01_glpi_ldap_rbac.png` | `https://glpi.cologistic.net` | **Configuración → Autenticación → Directorios LDAP** (`DC1`) + **Reglas RBAC** | Integración LDAP Active Directory (`DC1`) y reglas RBAC en GLPI |
| `[ ]` | `s2_e1_sec07_02_guacamole_totp_mfa.png` | `https://guacamole.cologistic.net` | Solicitud de código **2FA TOTP** *(SIN QR ni clave secreta)* | Verificación de segundo factor (MFA TOTP) en bastión Apache Guacamole |
| `[ ]` | `s2_e1_sec07_03_guacamole_14_conexiones.png` | `https://guacamole.cologistic.net` | Lista agrupada de **14 conexiones IaC** (Cisco, Proxmox, DCs) | Catálogo de 14 conexiones privilegiadas aprovisionadas como código en Guacamole |
| `[ ]` | `s2_e1_sec07_04_vaultwarden_org_colecciones.png` | `https://vault.cologistic.net` | Organización **`Co-Logistic S.A.C.`** y **8 colecciones** *(SIN abrir contraseñas)* | Organización `Co-Logistic S.A.C.` y 8 colecciones segregadas en Vaultwarden |
| `[ ]` | `s2_e1_sec07_05_vaultwarden_miembros_2fa.png` | `https://vault.cologistic.net` | **Miembros** o estado de **2FA activo** *(SIN códigos de recuperación)* | Gobernanza de miembros y autenticación 2FA en Vaultwarden |

### Sección 8 (`sec08`): Gestión de incidentes, continuidad y recuperación
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e1_sec08_01_glpi_ticket_inc001_top.png` | `https://glpi.cologistic.net/front/ticket.form.php?id=1` | Ticket **`INC-2026-001`** parte superior (`WMS01`, `H05`, `Responsable de Seguridad`) | Registro del incidente real `INC-2026-001` (T24) vinculado a CMDB en GLPI |
| `[ ]` | `s2_e1_sec08_02_glpi_ticket_inc001_fases.png` | `https://glpi.cologistic.net/front/ticket.form.php?id=1` | Ticket **`INC-2026-001`** parte inferior (**3 followups** + **Solución** Resuelto) | Ciclo completo de respuesta y cierre del incidente `INC-2026-001` (A.5.24–A.5.28) |

### Sección 10 (`sec10`): Monitoreo, medición y auditoría interna del SGSI
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e1_sec10_01_wazuh_vuln_sca.png` | `https://wazuh.cologistic.net` | **Vulnerability Detection** o **SCA (CIS Benchmark)** en `WMS01` | Evaluación continua de vulnerabilidades (CVE) y línea base CIS en Wazuh |
| `[ ]` | `s2_e1_sec10_02_proxmox_rol_terraformprov.png` | `https://10.10.70.41:8006` | **Datacenter → Permissions → Roles / API Tokens** (`TerraformProv`, cierre `H03`) | Rol de mínimo privilegio `TerraformProv` en Proxmox VE (cierre `H03`) |

---

## Bloque 3 — Entregable `S2_E3` (Proxmox, WMS/BI, Google Cloud y Monitoreo · 16 capturas)

### Sección 3 (`sec03`): Implementación on-premise: Proxmox VE y máquinas virtuales
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec03_01_proxmox_cluster_5_nodos.png` | `https://10.10.70.41:8006` | **Datacenter → Summary** (`PVE-COLOGISTIC`, **Quorate: Yes**, 5/5 nodos) | Clúster `PVE-COLOGISTIC` con 5 nodos físicos en quórum |
| `[ ]` | `s2_e3_sec03_02_wms_produccion_https.png` | `https://wms.cologistic.net` | Dashboard principal del WMS autenticado (candado TLS válido) | Aplicación WMS corporativa operando en alta disponibilidad sobre HTTPS |
| `[ ]` | `s2_e3_sec03_03_metabase_bi_datos.png` | `https://bi.cologistic.net` | Panel/consulta en Metabase mostrando datos cargados por el ETL | Tablero analítico en Metabase BI alimentado por el pipeline ETL |
| `[ ]` | `s2_e3_sec03_04_metabase_dw_conexion.png` | `https://bi.cologistic.net` | **Admin → Databases** (`Co-Logistic DataWarehouse`, `10.10.33.10`, *sin password*) | Conexión de Metabase BI hacia el DataWarehouse Patroni HA (`10.10.33.10`) |

### Sección 4 (`sec04`): Implementación en la nube: Google Cloud
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec04_01_gcp_vpc_subredes.png` | `https://console.cloud.google.com/networking/networks/details/vpc-cologistic?project=cologistic-cloud` | **Subredes** (`nube-borde`, `nube-tunel`, `nube-privada` + Private Google Access) | VPC `vpc-cologistic` y sus tres subredes en `southamerica-west1` |
| `[ ]` | `s2_e3_sec04_02_gcp_firewall_h02_cerrado.png` | `https://console.cloud.google.com/networking/firewalls/list?project=cologistic-cloud` | Reglas de `vpc-cologistic` (`fw-permitir-wireguard` en **`168.121.48.246/32`** y `fw-permitir-drp-ssh`) | Reglas de firewall GCP endurecidas con cierre de `H02` (`168.121.48.246/32`) |
| `[ ]` | `s2_e3_sec04_03_gcp_compute_vms.png` | `https://console.cloud.google.com/compute/instances?project=cologistic-cloud` | `gcp-borde` (`RUNNING`, `34.176.121.24`) y `gcp-wms-drp` (`TERMINATED`, Pilot Light `$0`) | Instancias Compute Engine en arquitectura Pilot Light (`gcp-borde` + `gcp-wms-drp`) |

### Sección 5 (`sec05`): Gestión de identidades y accesos del centro de datos
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec05_01_gcp_iam_service_accounts.png` | `https://console.cloud.google.com/iam-admin/serviceaccounts?project=cologistic-cloud` | `sa-gcp-compute`, `sa-respaldo`, `sa-terraform`, `sa-logs` | Cuentas de servicio segregadas de mínimo privilegio en Google Cloud IAM |

### Sección 6 (`sec06`): Inventario final de activos con evidencia
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec06_01_glpi_aplicativos_cloud.png` | `https://glpi.cologistic.net` | **Activos → Aplicativos** (los 6 recursos de Google Cloud en CMDB) | Activos de Google Cloud registrados como Aplicativos en GLPI CMDB |

### Sección 7 (`sec07`): Continuidad: respaldo, restauración y recuperación probada
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec07_01_gcp_bucket_respaldos.png` | `https://console.cloud.google.com/storage/browser/cologistic-respaldos-cologistic-cloud?project=cologistic-cloud` | Carpeta `backups/` + pestaña **Protection / Lifecycle** (versionado y borrado a 90 días) | Bucket offsite `cologistic-respaldos-cologistic-cloud` con versionado y ciclo de vida |

### Sección 8 (`sec08`): Monitoreo y control operativo del centro de datos
| Estado | Archivo | URL | Vista exacta | Pie de figura sugerido |
| :---: | :--- | :--- | :--- | :--- |
| `[ ]` | `s2_e3_sec08_01_zabbix_31_hosts.png` | `https://zabbix.cologistic.net` | **Monitoring → Hosts** mostrando los **31 hosts** registrados | Inventario de 31 hosts monitoreados en Zabbix 7.0 (`MON01`) |
| `[ ]` | `s2_e3_sec08_02_zabbix_proxmox_agentless.png` | `https://zabbix.cologistic.net` | `PVE-COLOGISTIC` → **Latest data / Graphs** con los **5 nodos Proxmox** | Descubrimiento agentless de los 5 nodos Proxmox VE en Zabbix (Decisión D33) |
| `[ ]` | `s2_e3_sec08_03_zabbix_triggers_capacidad.png` | `https://zabbix.cologistic.net` | **Triggers** con umbrales de capacidad (**80% RAM / disco**) | Triggers de capacidad (80% RAM y disco) configurados en Zabbix |
| `[ ]` | `s2_e3_sec08_04_wazuh_3_agentes.png` | `https://wazuh.cologistic.net` | **Endpoints Summary** (`WMS01`, `DB02`, `DB01` en `Active`) | Agentes Wazuh v4.9.2 activos en nodos críticos de aplicación y datos |
| `[ ]` | `s2_e3_sec08_05_gcp_monitoring_4_alertas.png` | `https://console.cloud.google.com/monitoring/alerting/policies?project=cologistic-cloud` | Las **4 políticas de alerta activas** (CPU > 85%, RAM > 85%, Disco > 80%, Uptime HTTP) | Cuatro políticas de alerta activas en Google Cloud Monitoring |
| `[ ]` | `s2_e3_sec08_06_gcp_monitoring_dashboard.png` | `https://console.cloud.google.com/monitoring/dashboards?project=cologistic-cloud` | Dashboard **`Co-Logistic Cloud — Monitoreo Híbrido (GCP)`** con métricas del Ops Agent | Dashboard consolidado de Cloud Monitoring con métricas del Ops Agent |
