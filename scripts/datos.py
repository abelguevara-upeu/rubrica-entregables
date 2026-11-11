"""
datos.py — Los datos reales del diseño, leídos de cologistic-infra (la fuente única), para que las tablas de los
entregables no se escriban a mano ni se desfasen del diseño.

  especificacion/*.yml        lo que generan las herramientas (VLAN, VM, nodos, switches, nube, zonas, enlaces)
  docs/topologia.html         el visor: de ahí salen las figuras y los recursos de cada hipervisor
  etapas/10-red/.../reglas.yml  las reglas de pfSense (la matriz de comunicación permitida/denegada)
"""
import collections
import json
import re
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parents[2] / "cologistic-infra"
ESPEC = RAIZ / "especificacion"
REGLAS = RAIZ / "etapas/10-red/roles/pfsense_base/vars/reglas.yml"
VISOR = RAIZ / "docs/topologia.html"


def _yaml(ruta):
    return yaml.safe_load(Path(ruta).read_text(encoding="utf-8"))


def _datos_visor():
    s = VISOR.read_text(encoding="utf-8")
    return json.JSONDecoder().raw_decode(s[re.search(r"DATOS\s*=\s*", s).end():])[0]


ESP = {n: _yaml(ESPEC / f"{n}.yml") for n in ("vlans", "maquinas", "isos", "nodos", "switches", "nube", "zonas", "enlaces", "puertos")}
VISOR_DATOS = _datos_visor()

# Para qué sirve cada VLAN (el diseño solo da nombre y subred; el propósito sale de lo que corre en ella)
PROPOSITO_VLAN = {
    "ADMINISTRACION": "PC y laptops de oficina; dos estaciones de administración (PAW01 y PAW02)",
    "OPERACIONES_WMS": "Terminales de almacén que usan el WMS, impresoras de etiquetas y de oficina",
    "INFRAESTRUCTURA": "Directorio activo (DC1, DC2), RADIUS, archivos, caché de parches, autoridad de certificados",
    "APLICACIONES": "Servidores del WMS privado (Django DRF + React Nginx; WMS01/WMS02 con VIP keepalived 10.10.31.10)",
    "BASE_DATOS": "PostgreSQL HA con Patroni + etcd + VIP 10.10.32.10 (DB01 y DB02, 2 vCPU / 4 GB)",
    "DATA_WAREHOUSE": "DataWarehouse analítico HA (DW01 y DW02) con Patroni + VIP 10.10.33.10 y Metabase BI (metabase_app)",
    "MONITOREO_SEGURIDAD": "SIEM Wazuh, escáner de vulnerabilidades, monitoreo Zabbix y mesa de ayuda",
    "COMUNICACIONES": "Central telefónica IP (PBX01) y relé de correo (MAIL01)",
    "CCTV": "Cámaras IP y grabador de video (NVR01); única VLAN que no pasa por el firewall hacia su grabador (D02)",
    "VOZ_IP": "Teléfonos IP de escritorio",
    "INVITADOS_WIFI": "Wi-Fi de visitantes: solo sale a Internet",
    "GESTION_TI": "Administración de switches, hipervisores y firewalls; bastión y bóveda de secretos",
    "DMZ": "WAF perimetral aislado del WMS privado (WAF01) y SFTP para socios (SFTP01)",
    "WIFI_INDUSTRIAL": "Terminales inalámbricos de almacén y puntos de acceso",
    "HA_SYNC": "Sincronización entre FW-MAIN y FW-BACKUP (CARP, pfsync); sin gateway",
    "IOT_CONTROL_ACCESO": "Lectores de puerta y sensores; servidor de control de acceso (ACS01)",
    "BACKUP_STORAGE": "Respaldos Bareos + ZFS (BKP01), pg_dump/rclone horario a GCS y contingencia Samba FS01 (rsync 5 min)",
    "HONEYPOT": "Servidor señuelo (HONEY01): cualquier conexión hacia él es una alerta",
}

# Criticidad de cada VM según el servicio que presta (Crítica: sin ella se detiene la operación)
CRITICIDAD = {"DC1": "Crítica", "DC2": "Crítica", "AAA01": "Alta", "AAA02": "Alta", "WMS01": "Crítica", "WMS02": "Crítica",
              "DB01": "Crítica", "DB02": "Crítica", "DW01": "Media", "DW02": "Media", "BKP01": "Alta", "WAF01": "Alta", "SFTP01": "Media",
              "SIEM01": "Alta", "VULN01": "Media", "MON01": "Alta", "ITSM01": "Media", "INFRA01": "Alta", "FS01": "Media",
              "MGMT01": "Alta", "PBX01": "Media", "MAIL01": "Media", "NVR01": "Alta", "WLC01": "Media", "ACS01": "Media",
              "HONEY01": "Media", "PAW01": "Media", "PAW02": "Media"}


def _por_dueno_ip():
    """{VM: {nodo, ip, vlan, vcpu, ram_gb, disco_gb, so, rol}} mezclando clonadas (maquinas.yml) y de ISO (isos.yml)."""
    vms = {}
    for n, v in ESP["maquinas"]["vms"].items():
        vms[n] = dict(v)
    for n, v in ESP["isos"]["maquinas"].items():
        vms[n] = dict(v)
    for sv in VISOR_DATOS["vistas"]["computo"]["servidores"]:
        for m in sv["maquinas"]:
            d = vms.setdefault(m["nombre"], {})
            d.update(rol=m.get("rol"), so=m.get("so") or d.get("so"), vcpu=m.get("vcpu"), ram_gb=m.get("ram_gb"),
                     disco_gb=m.get("disco_gb"), nodo=sv["nombre"], pareja=m.get("pareja_ha"))
    return vms


VMS = _por_dueno_ip()


def vlans():
    """[(id, nombre, cidr, vip, propósito)] de las VLAN que pasan por el firewall."""
    return [(v["id"], v["name"], v["subnet"], v.get("vip"), PROPOSITO_VLAN.get(v["name"], "")) for v in ESP["vlans"]["vlans"]]


def tabla_vlans():
    return [[str(i), n, f"{c}" + (f" · gw {vip}" if vip else " · sin gw"), p] for i, n, c, vip, p in vlans()]


def tabla_vms():
    """Las VM locales (28 con DW02): nombre (nodo · IP), vCPU, RAM, disco, SO, función."""
    filas = []
    for n, d in sorted(VMS.items(), key=lambda kv: (kv[1]["nodo"], kv[0])):
        ip = d.get("ip", "—")
        filas.append([f"{n} ({d['nodo']} · {ip})", str(d["vcpu"]), f"{d['ram_gb']:g} GB", f"{d['disco_gb']:g} GB",
                      d["so"], d.get("rol") or "—"])
    return filas


def totales_vm():
    t = collections.Counter()
    for d in VMS.values():
        t["n"] += 1
        t["vcpu"] += d["vcpu"]
        t["ram"] += d["ram_gb"]
        t["disco"] += d["disco_gb"]
        t["windows" if "Windows" in d["so"] else "linux"] += 1
    return dict(t)


def hipervisores():
    """{nodo: {vcpu, ram_gb, disco_gb}} de los servidores físicos."""
    return {s["nombre"]: s["recursos"] for s in VISOR_DATOS["vistas"]["computo"]["servidores"] if s["hipervisor"]}


def capacidad():
    h = hipervisores()
    return {"nodos": len(h), "cores": sum(r["vcpu"] for r in h.values()), "ram": sum(r["ram_gb"] for r in h.values()),
            "disco": sum(r["disco_gb"] for r in h.values())}


def carga_por_nodo():
    c = collections.defaultdict(lambda: collections.Counter())
    for d in VMS.values():
        c[d["nodo"]]["vcpu"] += d["vcpu"]
        c[d["nodo"]]["ram"] += d["ram_gb"]
        c[d["nodo"]]["disco"] += d["disco_gb"]
        c[d["nodo"]]["n"] += 1
    return c


def switches():
    return ESP["switches"]["switches"]


def tabla_switches():
    return [[n, f"{s['marca']} {s['modelo']}", s["ip"], s["rol"], str(s["stp_prioridad"])] for n, s in switches().items()]


def nube():
    return ESP["nube"]["nube"]["GOOGLE-CLOUD"]


def reglas_por_interfaz():
    r = _yaml(REGLAS)["pfsense_firewall_rules"]
    por = collections.OrderedDict()
    for x in r:
        por.setdefault(x["interface"], []).append(x)
    return por


def resumen_reglas():
    r = _yaml(REGLAS)["pfsense_firewall_rules"]
    return {"total": len(r), "pass": sum(x["action"] == "pass" for x in r), "block": sum(x["action"] == "block" for x in r)}


def zonas():
    return ESP["zonas"]["zonas"]


if __name__ == "__main__":
    print(totales_vm(), capacidad(), resumen_reglas(), len(vlans()), len(zonas()))
    for n, c in sorted(carga_por_nodo().items()):
        print(n, dict(c))
