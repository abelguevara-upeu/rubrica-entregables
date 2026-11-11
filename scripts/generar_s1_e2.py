#!/usr/bin/env python3
"""
generar_s1_e2.py — Entregable S1_E2: Análisis y Diseño de Centro de Datos Híbrido.

Llena la plantilla de la rúbrica con los datos REALES del diseño (cologistic-infra) y las figuras de topologia.html.
La rúbrica habla de VMware ESXi y AWS; el diseño real usa Proxmox VE y Google Cloud, así que cada sección lo declara y
da la equivalencia de conceptos (vSwitch ↔ bridge, port group ↔ etiqueta VLAN, EC2 ↔ Compute Engine, Security Group ↔ regla de firewall de la VPC).

    python3 scripts/generar_s1_e2.py
"""
import docx
from docx.text.paragraph import Paragraph

import datos
from comun import cambiar_pie_de_figura, cambiar_texto_que_contiene, franja_en_dos_filas, llenar_tabla, poner_figura, reemplazar_seccion

RAIZ = datos.Path(__file__).resolve().parents[1]
PLANTILLA = RAIZ / "templates/s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido_crmjbimadn.docx"
SALIDA = RAIZ / "entregables/s1_e2_analisis_y_diseno_de_centro_de_datos_hibrido.docx"

N, L = "Normal", "List Paragraph"
NUBE = datos.nube()
TUNEL = NUBE["tuneles"]["wireguard-nube"]
VM = datos.totales_vm()
CAP = datos.capacidad()
HV = datos.hipervisores()
CARGA = datos.carga_por_nodo()
ZONAS_INTERNAS = [z for z in datos.zonas().values() if not z["externa"]]
SOBREASIGNACION = VM["vcpu"] / CAP["cores"]
PCT_RAM = 100 * VM["ram"] / CAP["ram"]
PCT_DISCO = 100 * VM["disco"] / CAP["disco"]


def renombrar_titulo(doc, viejo, nuevo):
    for p in doc.paragraphs:
        if p.text.strip() == viejo:
            runs = p.runs
            runs[0].text = nuevo                  # se conserva el formato del primer fragmento del título original
            for r in runs[1:]:
                r._r.getparent().remove(r._r)
            return
    raise SystemExit(f"No encuentro el título «{viejo}»")


def main():
    doc = docx.Document(str(PLANTILLA))
    cambiar_texto_que_contiene(doc, "On-Premise", "On-Premise (Proxmox VE sobre KVM) + Cloud (Google Cloud Platform)")
    cambiar_texto_que_contiene(doc, "Preparado por:", "Preparado por: Abel Guevara")
    cambiar_texto_que_contiene(doc, "Organización:", "Organización: Co-Logistic S.A.C.  |  Año: 2026")
    T = list(doc.tables)

    # ── 1. Resumen ──────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "1. Resumen ejecutivo del diseño del centro de datos híbrido", [
        (N, "Este informe presenta el diseño del centro de datos híbrido de Co-Logistic S.A.C.: un cluster de cinco servidores con Proxmox VE que aloja las "
            f"{VM['n']} máquinas virtuales de la operación, y una extensión en Google Cloud para el respaldo fuera de sitio y la recuperación ante desastre. "
            "La rúbrica del curso describe VMware ESXi y AWS; el diseño usa Proxmox VE y Google Cloud, que resuelven lo mismo. Cada sección indica la equivalencia."),
        (N, "Dimensiones del diseño:"),
        (L, f"Tecnología on-premise: cinco servidores Dell Precision en torre (HV-MAIN, HV1, HV2, HV3 y HV4) con Proxmox VE, unidos en un cluster (PVE-COLOGISTIC). "
            f"Capacidad física: {CAP['cores']} núcleos, {CAP['ram']:.1f} GB de RAM y {CAP['disco'] / 1000:.1f} TB de disco local."),
        (L, f"Máquinas virtuales: {VM['n']} ({VM['linux']} Linux y {VM['windows']} Windows) con {VM['vcpu']} vCPU, {VM['ram']:g} GB de RAM y {VM['disco']:g} GB de disco asignados. "
            "Los Linux se clonan de una plantilla cloud-init con Terraform; los Windows se instalan desde ISO."),
        (L, "Disponibilidad: no hay almacenamiento compartido (348 GB locales por nodo, 1 TB en HV-MAIN). Por eso la redundancia es por servicio con anti-afinidad D03: pares HA en nodos distintos, "
            "Patroni + etcd (3 nodos de quórum: DB01, DB02, INFRA01) y VIPs keepalived (10.10.31.10, 10.10.32.10, 10.10.33.10), además de sync rsync cada 5 min FS01 -> BKP01."),
        (L, f"Tecnología cloud: Google Cloud, región {NUBE['region']} (Santiago de Chile). Una VPC ({NUBE['vpc']['rango']}) con gateway GCP-BORDE (e2-micro, IP {NUBE['ip_publica']}, WireGuard + Tailscale), "
            "nodo privado GCP-WMS-DRP (e2-medium, apagado en standby = $0 cómputo), Artifact Registry, Secret Manager, Cloud DNS privada y buckets de Cloud Storage."),
        (L, "Integración híbrida: túnel WireGuard entre los dos pfSense y GCP-BORDE más Tailscale Subnet Router (10.10.0.0/16 y 10.20.0.0/24)."),
        (L, "Hoja de ruta: en el Semestre 2 se instala el cluster, se aprovisionan las máquinas con Terraform y se ejecuta la recuperación de PostgreSQL desde el bucket."),
    ])
    poner_figura(doc, T[0], "computo.png")

    # ── 2. Organización ─────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "2. Descripción de la organización y necesidades de infraestructura", [
        (N, "Co-Logistic S.A.C. presta servicios de logística y depende de un WMS (interfaz web, API y base de datos PostgreSQL) que usan las oficinas y los terminales del almacén. "
            "Criterios para repartir las cargas entre el centro de datos local y la nube:"),
        (L, "Local: todo lo transaccional (WMS, PostgreSQL, directorio, RADIUS, archivos, telefonía, videovigilancia, SIEM y respaldo primario). Los terminales del almacén necesitan latencia baja y continuidad aunque falle Internet."),
        (L, "Nube: solo lo que gana por estar fuera del sitio: respaldos fuera de sitio (dumps horarios cifrados de PostgreSQL y archivos FS01), el gateway GCP-BORDE "
            "(WireGuard + Tailscale 10.20.0.0/24) y el servidor privado DRP (GCP-WMS-DRP, apagado en standby) respaldado por Artifact Registry, Secret Manager y Cloud DNS."),
        (L, "Información: los datos de stock e inventarios (PostgreSQL, VLAN 32) y las identidades (Active Directory) son los activos más críticos; su pérdida detiene la operación."),
        (L, f"Capacidad: el diseño dimensiona {VM['n']} máquinas y deja {100 - PCT_RAM:.0f} % de la RAM física libre para crecer o para absorber la caída de un nodo (sección 9)."),
    ])

    # ── 3. Alcance ──────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "3.1 Declaración de alcance", [
        (N, f"El alcance abarca el diseño del centro de datos local (gabinete R1 de 24U, sala de servidores, cinco hipervisores Proxmox, dos firewalls y sus {VM['n']} máquinas virtuales) "
            "y de la extensión en Google Cloud (VPC, GCP-BORDE, GCP-WMS-DRP privado, Artifact Registry, Secret Manager, Cloud DNS y buckets), con su dimensionamiento, disponibilidad y respaldo. No incluye la implementación, que es del Semestre 2."),
    ])
    reemplazar_seccion(doc, "3.2 Límites", [
        (N, "Límites del diseño:"),
        (L, "Físicos: un gabinete R1 de 24U con router y switches, y una sala contigua con los cinco servidores y los dos firewalls, todos en torre."),
        (L, "Tecnológicos: Proxmox VE (KVM) con un bridge VLAN-aware por nodo, bond active-backup hacia los dos switches ToR, cluster de cinco nodos, plantillas cloud-init, Docker dentro de las VM donde el diseño lo indica, y Google Cloud."),
        (L, "Organizacionales: el equipo de TI administra el cluster desde la VLAN de gestión (70) a través del bastión; el proveedor de nube administra su infraestructura física."),
    ])
    reemplazar_seccion(doc, "3.3 Exclusiones", [
        (N, "Exclusiones:"),
        (L, "Equipos de usuario final (PC, laptops, terminales): son parte del entregable de red, no del centro de datos."),
        (L, "Kubernetes: se descarta por la escala del proyecto (decisión D06); Docker Compose dentro de VM basta para versionar los despliegues."),
        (L, "La infraestructura física de Google Cloud, a cargo del proveedor."),
        (L, "Migración en vivo de VM y reinicio automático en otro nodo: requieren almacenamiento compartido, que no existe."),
    ])

    # ── 4. Objetivos ────────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "4. Objetivos del diseño de centro de datos", [
        (N, "Objetivos medibles, alineados con el control A.8.14 de ISO/IEC 27001:2022 (redundancia de las instalaciones de procesamiento):"),
    ])
    llenar_tabla(T[1], [
        ["Que ningún par redundante comparta hipervisor", "Pares de servicio en el mismo nodo (el validador del modelo)", "0", "Infraestructura"],
        ["Dimensionar con holgura", "RAM y disco asignados sobre capacidad física", "RAM menor al 50 % y disco menor al 50 %", "Infraestructura"],
        ["Tener copia fuera de sitio de los datos críticos", "Respaldo horario pg_dump + rclone (WMS, DW, Metabase y FS01) en Cloud Storage", "Copias horarias verificadas", "Respaldo"],
        ["Aprovisionar sin pasos manuales", "VM Linux creadas con Terraform desde la plantilla", f"{VM['linux']} de {VM['linux']} VM Linux", "Infraestructura"],
    ])

    # ── 5. On-premise ───────────────────────────────────────────────────────────────────────────────────────────
    renombrar_titulo(doc, "5. Arquitectura on-premise — diseño (VMware ESXi)", "5. Arquitectura on-premise — diseño (Proxmox VE; equivalente a VMware ESXi)")
    reemplazar_seccion(doc, "5. Arquitectura on-premise — diseño (Proxmox VE; equivalente a VMware ESXi)", [
        (N, "El centro de datos local usa Proxmox VE, un hipervisor de tipo 1 sobre KVM. Sirve para lo mismo que VMware ESXi y se gestiona desde su web (puerto 8006), sin vCenter. "
            "La tabla de equivalencias usada en el resto de la sección:"),
        (L, "vSwitch estándar (ESXi) ↔ bridge Linux VLAN-aware vmbr1 (Proxmox)."),
        (L, "Port group con VLAN ↔ etiqueta de VLAN en la tarjeta virtual de cada VM (net0 con tag)."),
        (L, "NIC teaming ↔ bond0 en modo active-backup sobre las dos NIC físicas (una a cada ToR)."),
        (L, "VMkernel de gestión ↔ interfaz vmbr1.70 del propio host, en la VLAN 70."),
    ])
    reemplazar_seccion(doc, "5.1 Topología física propuesta", [
        (N, "La parte principal es el gabinete R1 de 24U con el router Cisco C1111-4P (U21) y los siete switches (U1 a U7, de abajo hacia arriba: SW1-CORE1, SW2-CORE2, SW3-DIST1, SW4-DIST2, SW5-ACCESO, SW6-TOR2 y SW7-TOR1). "
            "Junto al rack hay una sala de servidores con los cinco hipervisores Dell Precision en torre, los dos firewalls y un punto de acceso Wi-Fi en el techo. "
            "Cada servidor tiene tres puertos de red: dos se agrupan en bond0 hacia los dos ToR y el tercero queda libre. Los 16 U libres del rack son reserva de crecimiento."),
    ])
    poner_figura(doc, T[2], "ubicacion.png", ancho_cm=11)

    reemplazar_seccion(doc, "5.2 Diseño del hipervisor", [
        (N, "Cada nodo tiene un solo bridge, vmbr1, VLAN-aware, sobre un bond active-backup de dos NIC (nic1 al ToR1 y nic2 al ToR2; no hay MLAG entre los ToR, por eso no es LACP). "
            "El propio host tiene su IP en vmbr1.70 (VLAN 70). No hay red de gestión fuera de banda."),
        (L, "Conmutación virtual: la etiqueta de VLAN va en la tarjeta de cada VM; el bridge deja pasar solo las VLAN del grupo DATACENTER. Las VLAN usadas por cada nodo se ven en la figura 5.2."),
        (L, "Agregación: bond0 active-backup; una de las dos NIC está activa y la otra espera, de modo que la caída de un ToR no corta el nodo."),
        (L, "Cluster: los cinco nodos forman PVE-COLOGISTIC con un solo enlace de corosync por la VLAN 70. Con cinco nodos se toleran dos caídas sin perder el quórum. "
            "Sin almacenamiento compartido, el cluster da gestión central y una vista única de capacidad, no alta disponibilidad de las VM."),
        (L, "Regla D03: ningún par redundante comparte hipervisor. DC1 (HV2) y DC2 (HV-MAIN); AAA01 (HV2) y AAA02 (HV-MAIN); WMS01 (HV3) y WMS02 (HV-MAIN); DB01 (HV4) y DB02 (HV-MAIN); DW01 (HV4) y DW02 (HV1). "
            "FW-MAIN y FW-BACKUP son equipos distintos."),
        (L, "Despliegue: las VM Linux se clonan de una plantilla cloud-init (Debian 12) con Terraform y un identificador (VMID) fijo por máquina; las cinco Windows se instalan desde ISO. "
            "Docker Compose corre dentro de las VM donde el diseño lo indica (WMS, parches, certificados, GLPI y Oxidized, Metabase, relé SMTP, Guacamole y Vaultwarden)."),
        (N, f"Las {VM['n']} máquinas planeadas, con el nodo, la IP y sus recursos:"),
    ])
    llenar_tabla(T[3], datos.tabla_vms())
    poner_figura(doc, T[4], franja_en_dos_filas("hipervisor.png", "hipervisor_2filas.png"))

    # ── 6. Nube ─────────────────────────────────────────────────────────────────────────────────────────────────
    renombrar_titulo(doc, "6. Arquitectura AWS — diseño", "6. Arquitectura en la nube — diseño (Google Cloud; equivalente a AWS)")
    reemplazar_seccion(doc, "6. Arquitectura en la nube — diseño (Google Cloud; equivalente a AWS)", [
        (N, "La nube del proyecto es Google Cloud. Los conceptos que pide la rúbrica para AWS tienen su equivalente directo: VPC ↔ VPC; subred pública o privada ↔ subred con o sin IP pública; "
            "tabla de rutas ↔ rutas de la VPC; Internet Gateway ↔ ruta por defecto hacia Internet; EC2 ↔ Compute Engine; Security Group y NACL ↔ reglas de firewall de la VPC; S3 ↔ Cloud Storage."),
    ])
    renombrar_titulo(doc, "6.3 Servicios EC2 planeados", "6.3 Instancias de cómputo planeadas (equivalente a EC2)")
    renombrar_titulo(doc, "6.4 Security Groups y NACL planeados", "6.4 Reglas de firewall de la VPC (equivalente a Security Groups y NACL)")
    reemplazar_seccion(doc, "6.1 Selección de región y justificación", [
        (L, f"Región: {NUBE['region']} (Santiago de Chile). Es la región de Google Cloud más cercana a Perú en el Pacífico, lo que da menor latencia hacia el túnel que las de Norteamérica y deja los datos en Sudamérica. "
            "La latencia efectiva se medirá en el Semestre 2."),
        (L, "Uso mínimo: solo una VM e2-micro siempre encendida (GCP-BORDE), un servidor DRP privado apagado en standby (GCP-WMS-DRP, $0 cómputo hasta emergencia) y servicios serverless/gestionados (Artifact Registry, Secret Manager, Cloud DNS, Cloud Storage). Eso mantiene el costo mínimo."),
        (L, "Continuidad: los respaldos en otra región geográfica distinta a la del centro de datos protegen ante la pérdida total de la sede."),
    ])
    reemplazar_seccion(doc, "6.2 Diseño de VPC", [
        (N, f"VPC-COLOGISTIC usa {NUBE['vpc']['rango']}, sin solaparse con 10.10.0.0/16 del centro de datos. Tiene tres subredes /28 y /29: una pública para el borde, una privada para el túnel y otra privada "
            "reservada para contingencia. Las rutas son dos: 10.10.0.0/16 por el túnel y 0.0.0.0/0 por Internet. La salida a Internet es por la ruta por defecto de la VPC (sin Cloud NAT: la única VM con IP pública es la de borde)."),
    ])
    llenar_tabla(T[5], [
        ["NUBE-BORDE", NUBE["subredes"]["NUBE-BORDE"], "Pública", "Aloja GCP-BORDE; IP pública para el túnel y la página de contingencia"],
        ["NUBE-TUNEL", NUBE["subredes"]["NUBE-TUNEL"], "Privada", "Direcciones wg0 del túnel: GCP-BORDE .17, FW-MAIN .18, FW-BACKUP .19"],
        ["NUBE-PRIVADA", NUBE["subredes"]["NUBE-PRIVADA"], "Privada", "Reservada para cargas de contingencia (DRP), sin IP pública"],
    ])
    poner_figura(doc, T[6], "vpc.png")
    reemplazar_seccion(doc, "6.3 Instancias de cómputo planeadas (equivalente a EC2)", [
        (N, "Se usan los recursos mínimos que exige el servicio:"),
    ])
    llenar_tabla(T[7], [
        ["GCP-BORDE", "Compute Engine e2-micro", f"Termina el túnel WireGuard (IP {NUBE['ip_publica']}), anuncia 10.20.0.0/24 vía Tailscale Subnet Router y hace proxy TLS privado hacia GCP-WMS-DRP", "NUBE-BORDE (10.20.0.4)"],
        ["GCP-WMS-DRP", "Compute Engine e2-medium (TERMINATED)", "Servidor privado de contingencia WMS + BI + Postgres ($0 cómputo en standby; sin IP pública); restaura dumps y descarga imágenes por Private Google Access", "NUBE-PRIVADA (10.20.0.34)"],
        ["Artifact Registry + Secret Manager + Cloud DNS", "Servicios gestionados GCP", "Repositorio privado wms-repo (CI/CD), secreto wms-drp-env cifrado y zona privada cologistic.net.", "Private Google Access / VPC"],
        ["GCP-BUCKET (respaldos)", "Cloud Storage (bucket)", f"Copia fuera de sitio horaria de cologistic_wms, cologistic_dw, metabase_app y archivos FS01 ({NUBE['respaldo']['bucket_respaldos']})", "Sin subred (API de Cloud Storage)"],
        ["Bucket de estado de Terraform", "Cloud Storage (bucket)", f"Estado remoto de Terraform ({NUBE['respaldo']['bucket_estado_terraform']}), separado del de respaldos", "Sin subred"],
    ])
    reemplazar_seccion(doc, "6.4 Reglas de firewall de la VPC (equivalente a Security Groups y NACL)", [
        (N, "La VPC rechaza por defecto toda entrada. Las excepciones, las rutas y los permisos de las cuentas de servicio son:"),
    ])
    llenar_tabla(T[8], [
        ["wg-desde-datacenter", "Entrada a GCP-BORDE", "UDP 51820 solo desde la IP pública del centro de datos"],
        ["admin-por-tunel", "Entrada a GCP-BORDE", "TCP 22 solo desde 10.10.70.0/24 (VLAN de gestión, por el túnel)"],
        ["Ruta a-datacenter", "Tabla de rutas", "10.10.0.0/16 por el túnel WireGuard"],
        ["Ruta a-internet", "Tabla de rutas", "0.0.0.0/0 por la ruta por defecto hacia Internet"],
        ["Cuentas de servicio", "IAM", "sa-respaldo: administra objetos del bucket de respaldos; sa-terraform: administra GCP-BORDE y los buckets; sa-logs: solo escribe registros"],
    ])

    # ── 7. Integración ──────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "7. Mecanismo de integración híbrida", [
        (N, "Este diseño usa el mismo túnel que el entregable S1_E1: los mismos extremos y las mismas redes anunciadas."),
        (L, f"Extremos: FW-MAIN (wg0 {TUNEL['extremos']['FW-MAIN']['ip']}) y FW-BACKUP (wg0 {TUNEL['extremos']['FW-BACKUP']['ip']}) en el centro de datos, y GCP-BORDE (wg0 {TUNEL['extremos']['GCP-BORDE']['ip']}) en la nube. UDP 51820, lo inicia el centro de datos."),
        (L, "Redes anunciadas: 10.10.0.0/16 (centro de datos) y 10.20.0.0/24 (VPC). Cada lado tiene una ruta hacia el otro por el túnel."),
        (L, f"Respaldo fuera de sitio: BKP01 (10.10.120.11, VLAN 120) envía por TCP 443, por el túnel, las copias cifradas al bucket {NUBE['respaldo']['bucket_respaldos']}. "
            "La regla de pfSense solo permite ese destino hacia la nube desde la VLAN 120."),
        (L, "Recuperación ante desastre (modelo de luz piloto privado): en reposo gcp-wms-drp permanece TERMINATED ($0 cómputo). Ante caída total de la sede, al encender gcp-wms-drp ejecuta activar_contingencia_drp.sh: "
            "obtiene credenciales desde Secret Manager, descarga las últimas imágenes Docker desde Artifact Registry, restaura cologistic_wms/dw/metabase desde Cloud Storage y publica por Tailscale y proxy TLS de gcp-borde."),
    ])

    # ── 8. Matriz de componentes ────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "8. Matriz de componentes del centro de datos", [
        (N, f"La matriz cubre todo lo que muestran las figuras de este informe: el rack y sus equipos, la sala de servidores, las {VM['n']} máquinas y los recursos de la nube."),
    ])
    filas = [["Gabinete R1 (24U)", "On-premise", "Rack", "Aloja el router y los siete switches; 16 U libres", "Crítica"],
             ["Router-Cisco (C1111-4P)", "On-premise", "Router", "Emula los enlaces de Internet (VLAN 901 a 904) y hace NAT", "Crítica"],
             ["SW1-CORE1 y SW2-CORE2 (C9300L)", "On-premise", "Switch de núcleo", "Núcleo en capa 2; raíz STP en SW2-CORE2", "Crítica"],
             ["SW3-DIST1 y SW4-DIST2 (C9200L)", "On-premise", "Switch de distribución", "Agregan hacia el núcleo, el acceso y los ToR", "Alta"],
             ["SW5-ACCESO (C1000)", "On-premise", "Switch de acceso", "Usuarios y punto de acceso Wi-Fi", "Media"],
             ["SW6-TOR2 y SW7-TOR1 (C1000)", "On-premise", "Switch ToR", "Un cable a cada servidor Proxmox", "Crítica"],
             ["FW-MAIN y FW-BACKUP (pfSense CE)", "On-premise", "Servidor (torre)", "Firewall en alta disponibilidad con CARP", "Crítica"],
             ["AP1-WIFI", "On-premise", "Punto de acceso", "Cobertura inalámbrica", "Media"]]
    for n, r in HV.items():
        c = CARGA[n]
        filas.append([f"{n} (Proxmox VE)", "On-premise", "Hipervisor", f"{r['vcpu']} núcleos, {r['ram_gb']:g} GB, {r['disco_gb']:g} GB; aloja {c['n']} VM", "Crítica"])
    for n, d in sorted(datos.VMS.items(), key=lambda kv: (kv[1]["nodo"], kv[0])):
        filas.append([n, "On-premise", "VM " + ("Windows" if "Windows" in d["so"] else "Linux"), f"{d.get('rol') or '—'} · {d['nodo']}", datos.CRITICIDAD[n]])
    filas += [["VPC-COLOGISTIC", "Nube", "VPC", f"{NUBE['vpc']['rango']}; tres subredes + Private Google Access", "Alta"],
              ["GCP-BORDE", "Nube", "Instancia Compute Engine e2-micro", f"WireGuard ({NUBE['ip_publica']}), Tailscale Subnet Router y proxy TLS DRP", "Alta"],
              ["GCP-WMS-DRP", "Nube", "Instancia Compute Engine e2-medium", "Servidor privado WMS + BI + Postgres DRP (10.20.0.34, TERMINATED en standby)", "Alta"],
              ["Artifact Registry / Secret Manager / Cloud DNS", "Nube", "Servicios gestionados", "Imágenes Docker wms-repo, secretos DRP y resolución privada en contingencia", "Alta"],
              ["GCP-BUCKET", "Nube", "Bucket de Cloud Storage", "Copia horaria fuera de sitio de BD (WMS/DW/Metabase) y archivos FS01", "Alta"]]
    llenar_tabla(T[9], filas)

    # ── 9. Dimensionamiento ─────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "9. Dimensionamiento y capacidad", [
        (N, "Cálculo con los datos del modelo:"),
        (L, f"Capacidad física: 5 nodos × 6 núcleos = {CAP['cores']} núcleos (Intel Xeon Bronze 3204, sin hilos adicionales). RAM: 4 × 31,63 GB + 64 GB (HV-MAIN) = {CAP['ram']:.1f} GB. Disco: 4 × 348 GB + 1000 GB = {CAP['disco']} GB."),
        (L, f"Asignado a las {VM['n']} VM: {VM['vcpu']} vCPU, {VM['ram']:g} GB de RAM y {VM['disco']:g} GB de disco."),
        (L, f"CPU: {VM['vcpu']} vCPU sobre {CAP['cores']} núcleos = {SOBREASIGNACION:.2f} : 1. Es una sobreasignación baja; la guía del modelo admite hasta 4 : 1. RAM asignada: {PCT_RAM:.1f} % de la física. Disco: {PCT_DISCO:.1f} %."),
        (L, "Carga por nodo (vCPU / RAM / disco asignados, frente a 6 núcleos, la RAM y el disco del nodo): " + "; ".join(
            f"{n}: {CARGA[n]['vcpu']} / {CARGA[n]['ram']:g} GB / {CARGA[n]['disco']:g} GB de {HV[n]['ram_gb']:g} GB y {HV[n]['disco_gb']:g} GB" for n in HV) + "."),
        (L, f"Margen de crecimiento: queda más de la mitad de la RAM y del disco libre. Se podrían agregar unas 10 VM del tamaño medio (3 vCPU, 3 GB, 35 GB) sin superar el 4 : 1."),
        (L, f"Caída de un nodo: si falla HV-MAIN (23 GB de RAM asignada), la RAM libre en los otros cuatro nodos es de unos {sum(HV[n]['ram_gb'] - CARGA[n]['ram'] for n in HV if n != 'HV-MAIN'):.0f} GB, suficiente. "
            "Como no hay almacenamiento compartido, las VM de ese nodo se restauran desde el respaldo (vzdump y Bareos). Por eso la plantilla de cloud-init existirá en cada nodo."),
        (L, "Nube: GCP-BORDE (e2-micro) solo termina el túnel WireGuard, anuncia 10.20.0.0/24 por Tailscale y actúa como proxy TLS; la carga de cómputo (PostgreSQL, WMS Django DRF + React Nginx, Metabase) "
            "reside en GCP-WMS-DRP (e2-medium en NUBE-PRIVADA, sin IP pública), apagada en estado normal ($0 de cómputo) hasta un simulacro o desastre."),
    ])

    # ── 10. Disponibilidad ──────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "10. Consideraciones de disponibilidad y continuidad en el diseño", [
        (N, "Disponibilidad y continuidad:"),
        (L, "Por servicio con anti-afinidad (D03) y VIPs HA keepalived: Directorio activo y DHCP (DC1/DC2), RADIUS (AAA01/AAA02), WMS privado (WMS01/WMS02 con VIP 10.10.31.10), "
            "PostgreSQL WMS (DB01/DB02 Patroni + quórum etcd de 3 nodos con testigo INFRA01, VIP 10.10.32.10), DataWarehouse + Metabase BI (DW01/DW02 Patroni + VIP 10.10.33.10 sobre metabase_app), "
            "archivos (FS01 replicado cada 5 min vía rsync hacia BKP01 con Samba de contingencia) y Firewalls (FW-MAIN/FW-BACKUP con CARP)."),
        (L, "Respaldo 3-2-1: (1) datos en producción; (2) copia local en BKP01 (Bareos + ZFS + rsync FS01 + pg_dump horario WMS/DW/Metabase), más vzdump de Proxmox; (3) copia cifrada fuera de sitio horaria en Cloud Storage."),
        (L, "Objetivos de recuperación preliminares: PostgreSQL y DW/BI, RPO de segundos con Patroni HA en sitio y 1 hora en la nube (pg_dump horario); RTO de minutos por failover VIP automático y menor a 4 horas en GCP-WMS-DRP. "
            "FS01: RPO de 5 minutos mediante rsync hacia BKP01."),
        (L, "Red: bond active-backup hacia dos ToR, doce port-channels LACP entre los switches y dos proveedores de Internet con conmutación en pfSense."),
        (L, "Límite: sin almacenamiento compartido, la pérdida de un nodo requiere restaurar sus VM; la energía y el clima de la sala no forman parte de este diseño."),
    ])

    # ── 11. Conclusiones ────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "11. Conclusiones y hoja de ruta hacia la implementación", [
        (N, "Conclusiones:"),
        (L, f"El diseño consolida {VM['n']} máquinas en cinco servidores con un {SOBREASIGNACION:.2f} : 1 de sobreasignación de CPU y menos de la mitad de la RAM usada, dejando margen para crecer."),
        (L, "Proxmox VE cubre lo que pide la rúbrica de ESXi (conmutación virtual, agregación de enlaces, gestión y VM planeadas) sin licencias; Google Cloud cubre lo de AWS con una huella mínima."),
        (L, "La redundancia por servicio con la regla D03 compensa la ausencia de almacenamiento compartido, y el respaldo fuera de sitio protege ante la pérdida de la sede."),
        (L, "Todo el diseño está como datos versionados, y de ahí salen las tablas y las figuras de este informe, así que no pueden diferir entre sí."),
        (N, "Hoja de ruta (Semestre 2): Day-0 manual de los cinco Dell con Proxmox y red por Ansible; formar el cluster y comprobar el quórum; clonar las VM con Terraform; "
            "instalar las Windows desde ISO; probar la recuperación de PostgreSQL desde el bucket y medir RTO y RPO."),
    ])

    # ── 12. Referencias ─────────────────────────────────────────────────────────────────────────────────────────
    reemplazar_seccion(doc, "12. Referencias", [
        (N, "[1] Proxmox Server Solutions GmbH, \"Proxmox VE Administration Guide,\" Viena. [Online]. Disponible: https://pve.proxmox.com/pve-docs/"),
        (N, "[2] VMware by Broadcom, \"vSphere Networking,\" Documentación de VMware. [Online]. Disponible: https://docs.vmware.com/"),
        (N, "[3] Google Cloud, \"VPC network overview\" y \"Compute Engine documentation.\" [Online]. Disponible: https://cloud.google.com/vpc/docs/overview"),
        (N, "[4] Amazon Web Services, \"AWS Well-Architected Framework,\" 2023. [Online]. Disponible: https://aws.amazon.com/architecture/well-architected/"),
        (N, "[5] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security management systems — Requirements,\" Geneva, 2022."),
        (N, "[6] Bareos Project, \"Bareos Documentation.\" [Online]. Disponible: https://docs.bareos.org/"),
        (N, "[7] PostgreSQL Global Development Group, \"PostgreSQL Documentation: High Availability, Load Balancing, and Replication.\" [Online]. Disponible: https://www.postgresql.org/docs/"),
        (N, "[8] J. A. Donenfeld, \"WireGuard: Next Generation Kernel Network Tunnel,\" in Proc. NDSS, San Diego, CA, USA, 2017."),
    ])

    cambiar_pie_de_figura(doc, "Figura 5.1", "Figura 5.1 — Topología física propuesta del centro de datos on-premise (rack R1 y sala de servidores)")
    cambiar_pie_de_figura(doc, "Figura 5.2", "Figura 5.2 — Diseño interno de los hipervisores Proxmox VE: bridge vmbr1, VLAN y VM de cada nodo")
    cambiar_pie_de_figura(doc, "Figura 6.1", "Figura 6.1 — Diseño de la VPC en Google Cloud: subredes, VM de borde y bucket")
    SALIDA.parent.mkdir(exist_ok=True)
    doc.save(str(SALIDA))
    print(f"Guardado: {SALIDA}")


if __name__ == "__main__":
    main()
