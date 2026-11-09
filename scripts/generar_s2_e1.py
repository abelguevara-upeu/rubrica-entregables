"""
generar_s2_e1.py — Contenido del entregable S2_E1: Planificación e Implementación del SGSI (ISO/IEC 27001:2022 y 27005).

Inventario, riesgos y SoA salen de sgsi_datos.py (los mismos datos que los XLSX). Los hallazgos de la auditoría interna son reales: salen de revisar
el repositorio cologistic-infra y el estado de Terraform de la nube (fecha del informe: noviembre de 2026).
Lo que todavía no se ejecutó (revisión por la dirección, pruebas de recuperación) se dice como pendiente, no como hecho.
"""
import datos
import sgsi_datos as sg
from redactor import Redactor

NUBE = datos.nube()
RIESGOS = sg.riesgos()
SOA = sg.soa()
RESUMEN = sg.resumen_soa()
INV = sg.inventario()


def contenido():
    r = Redactor()
    n_alto = sum(1 for x in RIESGOS if x[7] in ("Alto", "Crítico"))
    n_alto_res = sum(1 for x in RIESGOS if x[13] in ("Alto", "Crítico"))
    aplican = len(SOA) - RESUMEN.get("No aplica", 0)

    # ── 1 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Resumen ejecutivo")
    r.p("Este informe presenta el Sistema de Gestión de Seguridad de la Información (SGSI) de Co-Logistic S.A.C. conforme a ISO/IEC 27001:2022, con el análisis de riesgos de "
        "ISO/IEC 27005. El SGSI cubre la infraestructura híbrida diseñada en el Semestre 1: la red segmentada de siete switches y dos firewalls, el cluster Proxmox de cinco servidores "
        "con 27 máquinas virtuales y la extensión en Google Cloud.")
    r.bullets(
        f"Inventario: {len(INV)} activos con propietario, ubicación, criticidad y clasificación C-I-D.",
        f"Riesgos: {len(RIESGOS)} riesgos evaluados con una escala de 1 a 5 de impacto y probabilidad; {n_alto} están en nivel alto o crítico antes del tratamiento y {n_alto_res} después.",
        f"Declaración de aplicabilidad: {aplican} de los 93 controles del Anexo A aplican y {RESUMEN.get('No aplica', 0)} se excluyen con justificación. "
        f"Hoy hay {RESUMEN.get('Implementado', 0)} controles implementados, {RESUMEN.get('Parcial', 0)} parciales y {RESUMEN.get('Planificado', 0)} planificados.",
        "Políticas: seguridad, accesos, incidentes, proveedores y nube, respaldo y recuperación, y uso aceptable, vinculadas a componentes reales (pfSense, Active Directory, bastión, Bareos, Google Cloud).",
        "Auditoría interna: se hizo una revisión del repositorio y del estado de la nube. Encontró 1 no conformidad mayor, 3 menores y 5 observaciones, cada una con su acción correctiva.",
        "Lo que falta: la aprobación formal de la dirección, las pruebas de recuperación y la ejecución de las pruebas de seguridad del entregable S2_E2.")

    # ── 2 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Contexto, alcance y liderazgo del SGSI")
    r.h2("Contexto de la organización")
    r.p("Co-Logistic S.A.C. presta servicios de logística. Su operación depende del sistema de gestión de almacenes (WMS) y de su base de datos PostgreSQL, que usan las oficinas y los terminales "
        "del almacén. La infraestructura tiene un centro de datos local con Proxmox VE y una extensión en Google Cloud para el respaldo fuera de sitio y la recuperación ante desastre. "
        "Cuestiones internas relevantes: un equipo pequeño de TI, la infraestructura gestionada como código y la ausencia de almacenamiento compartido. "
        "Cuestiones externas: la Ley N.° 29733 de protección de datos personales, los acuerdos con clientes y socios logísticos y la dependencia de los proveedores de Internet y de nube.")
    r.h2("Partes interesadas y sus requisitos")
    r.tabla(["Parte interesada", "Qué espera de la seguridad"], [
        ["Clientes y socios", "Disponibilidad del inventario y confidencialidad de sus datos en el intercambio de archivos."],
        ["Dirección", "Continuidad de la operación y cumplimiento legal; evidencia para auditorías."],
        ["Personal de almacén y de oficina", "Servicios estables; no ver ni alterar datos que no son suyos."],
        ["Equipo de TI y seguridad", "Administración controlada, registros y detección temprana."],
        ["Proveedores de Internet y de nube", "Uso dentro de los términos del servicio y rangos de direcciones que no se solapen."],
        ["Autoridad de protección de datos personales", "Cumplimiento de la Ley N.° 29733 y su reglamento."],
    ])
    r.h2("Alcance del SGSI")
    r.p("El SGSI comprende la infraestructura tecnológica híbrida de Co-Logistic S.A.C.: el rack R1 con el router y los siete switches Cisco, los dos firewalls pfSense, los cinco hipervisores "
        "Proxmox VE y sus 27 máquinas virtuales, los servicios que corren en ellas (directorio, WMS, bases de datos, respaldo, monitoreo, telefonía, correo, control de acceso y videovigilancia) "
        "y los recursos de Google Cloud (VPC, VM de borde, buckets y cuentas de servicio), junto con las redes, el túnel, el monitoreo y los procesos de administración asociados.")
    r.p("Este alcance es el mismo de los entregables S1_E1 (red) y S1_E2 (centro de datos). Quedan fuera los dispositivos personales, las redes de los proveedores, el código del WMS y "
        "los procesos de contratación y de oficina.")
    r.fig("enlace.png", "Figura 2.1 — Alcance técnico del SGSI: red, cluster y nube (vista de enlace del modelo)")
    r.h2("Política de seguridad de la información")
    r.p("La dirección de Co-Logistic S.A.C. se compromete a proteger la confidencialidad, integridad y disponibilidad de la información que sustenta su operación. Para ello:")
    r.bullets(
        "Se aplica el mínimo privilegio y la denegación por defecto en la red, los servicios y la nube.",
        "Los riesgos se evalúan con una metodología única (ISO/IEC 27005) y se revisan cada seis meses o ante un cambio importante.",
        "Toda la infraestructura se gestiona como código, con cambios revisados y registrados.",
        "Los incidentes se reportan, se contienen, se investigan y se aprenden de ellos.",
        "Se cumple la normativa de protección de datos personales y los acuerdos con clientes.",
        "El SGSI se mejora de forma continua con auditorías internas y la revisión por la dirección.")
    r.h2("Liderazgo, roles y responsabilidades")
    r.tabla(["Rol", "Responsabilidad en el SGSI"], [
        ["Dirección general", "Aprueba la política, los objetivos y los recursos; hace la revisión anual."],
        ["Responsable del SGSI", "Mantiene el sistema, coordina riesgos y auditorías y reporta a la dirección."],
        ["Jefatura de TI", "Ejecuta los controles técnicos y es dueña de la infraestructura."],
        ["Responsable de Seguridad", "Monitorea, gestiona incidentes y vulnerabilidades y administra el bastión y la bóveda de secretos."],
        ["Responsable de Redes", "Switches, router, firewalls, VLAN y el túnel híbrido."],
        ["Responsable de Aplicaciones y de Datos", "WMS, bases de datos, respaldos y la clasificación de la información."],
        ["Todo el personal", "Cumple las políticas y reporta los eventos de seguridad."],
    ])
    r.h2("Objetivos de seguridad medibles")
    r.tabla(["Objetivo", "Indicador", "Meta"], [
        ["Reducir los riesgos altos y críticos", "Riesgos en nivel alto o crítico después del tratamiento", "0"],
        ["Aplicar los controles aplicables", "Controles del Anexo A en estado implementado", "100 % de los aplicables en 12 meses"],
        ["Recuperar los servicios críticos", "RTO y RPO obtenidos en el ejercicio de recuperación", "Dentro de los objetivos de la sección de continuidad"],
        ["Detectar incidentes a tiempo", "Tiempo entre el evento y la alerta en SIEM01", "Menos de 10 minutos"],
        ["Mantener la configuración trazable", "Cambios de red y servidores con registro en Git", "100 %"],
        ["Cerrar los hallazgos de auditoría", "No conformidades mayores abiertas", "0 a los 30 días"],
    ])

    # ── 3 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Inventario de activos y clasificación de la información")
    r.p("El inventario se genera a partir del modelo del diseño (cologistic-nettop-datos), de modo que cada activo coincide con lo dibujado en las topologías. Cada activo tiene un propietario (un rol), "
        "su ubicación, su criticidad y su valoración de confidencialidad (C), integridad (I) y disponibilidad (D) en una escala de 1 (baja) a 3 (alta). La criticidad es la del mayor de los tres valores, "
        "y la clasificación sigue a la confidencialidad: 3 Confidencial, 2 Interna y 1 Pública.")
    r.tabla(["ID", "Activo", "Tipo", "Propietario", "Crit.", "C-I-D"],
            [[a[0], a[1], a[2], a[3], a[5], f"{a[6]}-{a[7]}-{a[8]}"] for a in INV])
    r.p("El inventario completo, con la ubicación y la clasificación de cada activo, se entrega también en el archivo Excel «Inventario de activos».")

    # ── 4 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Evaluación y tratamiento de riesgos (ISO/IEC 27005)")
    r.h2("Metodología")
    r.bullets(
        "Identificación: por activo o grupo de activos del inventario, con la amenaza y la vulnerabilidad que la hace posible.",
        "Impacto (1 a 5): 1 sin efecto, 2 menor, 3 moderado, 4 grave (servicio crítico detenido o fuga de datos), 5 muy grave (pérdida de la operación o de datos críticos).",
        "Probabilidad (1 a 5): 1 muy improbable, 2 improbable, 3 posible, 4 probable, 5 casi segura en un año.",
        "Nivel de riesgo = impacto × probabilidad: Bajo de 1 a 6, Medio de 7 a 12, Alto de 13 a 19 y Crítico desde 20.",
        "Tratamiento: mitigar con controles, aceptar (solo riesgos bajos, con justificación), transferir o evitar. Se calcula el riesgo residual con el impacto y la probabilidad esperados tras los controles.",
        "Criterio de aceptación: la dirección acepta los riesgos de nivel Bajo; los Medio, Alto y Crítico requieren un plan de tratamiento y su seguimiento.")
    r.h2("Matriz de riesgos y tratamiento")
    r.tabla(["ID", "Activo y amenaza", "Vulnerabilidad", "I×P = nivel", "Tratamiento y controles", "Residual"],
            [[x[0], f"{x[1]}: {x[2]}", x[3], f"{x[4]}×{x[5]} = {x[6]} ({x[7]})", f"{x[8]}: {x[9]}", f"{x[10]}×{x[11]} = {x[12]} ({x[13]})"] for x in RIESGOS])
    r.p("Los riesgos altos y críticos antes del tratamiento (R01, R04, R06 y R10) se priorizan en el plan de acción. El riesgo R16 (SSH antiguo en los switches C1000) se acepta porque la gestión está aislada en la VLAN 70 y su nivel es bajo. "
        "La matriz se entrega también en el archivo Excel «Matriz de riesgos».")

    # ── 5 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Declaración de Aplicabilidad (SoA) y selección de controles")
    r.p(f"La declaración cubre los 93 controles del Anexo A de ISO/IEC 27001:2022. Aplican {aplican} y se excluyen {RESUMEN.get('No aplica', 0)} con justificación. "
        f"El estado se determinó con la evidencia del repositorio: {RESUMEN.get('Implementado', 0)} implementados, {RESUMEN.get('Parcial', 0)} parciales y {RESUMEN.get('Planificado', 0)} planificados. "
        "Cada control se vincula con los riesgos que trata (columna «Controles» de la matriz) y con el componente que lo evidencia. Los estados se revisan cada vez que se verifica un control en los equipos.")
    r.tabla(["Control", "Aplica", "Estado", "Justificación y evidencia"],
            [[f"{c} {nombre}", "No" if e == "No aplica" else "Sí", e, j] for c, nombre, e, j in SOA])

    # ── 6 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Políticas y procedimientos del SGSI")
    r.h2("Política de control de accesos")
    r.bullets(
        "Las cuentas son personales; no se comparten. La identidad corporativa es Active Directory (DC1 y DC2); RADIUS (AAA01 y AAA02) autentica a los administradores en los switches.",
        "La administración de servidores, switches e hipervisores se hace solo desde la VLAN 70, a través del bastión (MGMT01, Apache Guacamole). Los usuarios no alcanzan la VLAN 70 (regla de bloqueo en pfSense).",
        "Las contraseñas y llaves se guardan en la bóveda de secretos (Vaultwarden en MGMT01). No se escriben en el repositorio ni en scripts.",
        "El acceso privilegiado usa cuentas distintas de las de uso diario y se otorga por tarea y con el mínimo permiso.",
        "Las altas, cambios y bajas se piden al Responsable de Seguridad y se registran; las bajas se ejecutan el mismo día.")
    r.h2("Política de gestión de incidentes")
    r.p("Se define en el procedimiento de la sección «Gestión de incidentes, continuidad y recuperación». Todo el personal reporta los eventos sospechosos al Responsable de Seguridad por el canal definido.")
    r.h2("Política de proveedores y uso de la nube")
    r.bullets(
        "Los proveedores de Internet y de nube se evalúan por disponibilidad y seguridad antes de contratarlos y se revisan cada año.",
        "En Google Cloud solo se despliega lo que el diseño declara (Terraform, etapa 50). Las cuentas de servicio tienen un único propósito y permisos acotados al recurso.",
        "Los datos que salen de la sede hacia la nube viajan cifrados por el túnel WireGuard y se guardan cifrados en el bucket.",
        "El estado de Terraform se guarda en un bucket distinto del de respaldos, con versionado.",
        "Las alertas de presupuesto y de capacidad de la nube se revisan cada mes.")
    r.h2("Política de respaldo y recuperación ante desastres")
    r.bullets(
        "Esquema 3-2-1: los datos de producción, una copia local en BKP01 (Bareos y almacenamiento ZFS) y una copia cifrada fuera de sitio en el bucket de Cloud Storage.",
        "Respaldo diario a las 02:00 de PostgreSQL (DB01) y de las configuraciones, con sincronización al bucket; las máquinas virtuales se respaldan con vzdump de Proxmox.",
        "El bucket conserva versiones y elimina objetos a los 90 días.",
        "Se hace un ejercicio de recuperación al menos cada seis meses y se compara el RTO y RPO obtenidos con los objetivos.",
        "La restauración de un servicio crítico sigue el orden: directorio, base de datos, WMS, y después los servicios de apoyo.")
    r.h2("Política de uso aceptable")
    r.bullets(
        "Los equipos y cuentas de la organización se usan para el trabajo. Se prohíbe instalar software no autorizado y desactivar protecciones.",
        "Se mantiene el escritorio y la pantalla limpios en las estaciones de administración.",
        "La red de invitados solo da acceso a Internet; no se conectan dispositivos personales a las redes internas.",
        "Los datos clasificados como Confidencial no se envían por canales no autorizados ni se guardan fuera de los sistemas de la organización.")
    r.h2("Política de seguridad de la información")
    r.p("Es la declarada en la sección de contexto, alcance y liderazgo. Se revisa una vez al año y cuando cambia el alcance, y la comunica el Responsable del SGSI a todo el personal.")

    # ── 7 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Gobernanza de identidades, accesos y protección de datos")
    r.h2("Matriz de accesos por rol")
    r.tabla(["Rol", "AD", "Bastión", "Switches y Proxmox", "WMS", "BD", "Respaldos", "Google Cloud"], [
        ["Usuario de oficina", "Cuenta", "—", "—", "Uso web", "—", "—", "—"],
        ["Operador de almacén", "Cuenta", "—", "—", "Uso web", "—", "—", "—"],
        ["Responsable de Aplicaciones", "Cuenta", "Sí", "—", "Admin.", "Solo lectura", "—", "—"],
        ["Responsable de Datos", "Cuenta", "Sí", "—", "—", "Admin.", "Operador", "Respaldos"],
        ["Responsable de Redes", "Cuenta", "Sí", "Admin. de switches y firewalls", "—", "—", "—", "VPC y túnel"],
        ["Responsable de Seguridad", "Admin. delegado", "Admin.", "Solo lectura", "—", "—", "Solo lectura", "Registros"],
        ["Jefatura de TI", "Admin.", "Admin.", "Admin.", "Admin.", "Admin.", "Admin.", "Admin."],
    ])
    r.h2("Mínimo privilegio y segregación")
    r.p("Cada rol tiene solo lo necesario para su tarea. Los usuarios y los terminales del almacén no llegan a la base de datos ni a la gestión: pfSense lo bloquea de forma explícita y solo permite que "
        "el WMS consulte PostgreSQL. El token de Terraform en Proxmox hoy tiene el rol Administrador sobre todo el cluster; se creará un rol propio con los permisos de VM y almacenamiento (hallazgo H03).")
    r.h2("Autenticación multifactor y credenciales")
    r.bullets(
        "MFA (TOTP) obligatorio en el bastión (Guacamole), en la bóveda (Vaultwarden) y en la consola de Google Cloud. Está definido; falta habilitarlo y probarlo en cada uno.",
        "Los secretos viven en .env (fuera de Git) y en Vaultwarden. Se rotan cada 90 días y siempre que alguien con acceso deje el equipo.",
        "Hay una contraseña de administrador de Windows en archivos del repositorio; se rotará y se retirará del historial (hallazgo H01).",
        "Los certificados TLS de los servicios se emitirán con la autoridad interna step-ca (INFRA01) en lugar de certificados autofirmados.")
    r.h2("Protección de datos")
    r.p("Los datos personales y comerciales se encuentran en la base de datos del WMS, en el intercambio de archivos con socios (SFTP enjaulado por socio) y en el video. Se protegen con la segmentación de red, "
        "el cifrado en tránsito (TLS y WireGuard), el cifrado de las copias de respaldo y el mínimo privilegio. Se cumple la Ley N.° 29733: finalidad, consentimiento, seguridad y atención de los derechos de las personas.")

    # ── 8 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Gestión de incidentes, continuidad y recuperación")
    r.h2("Procedimiento de gestión de incidentes")
    r.tabla(["Fase", "Qué se hace", "Responsable", "Plazo"], [
        ["1. Detección y reporte", "Una alerta de SIEM01 (Wazuh) o de Zabbix, o el reporte de una persona, abre el incidente con fecha, origen y activos afectados.", "Quien lo detecta, y Seguridad", "Inmediato"],
        ["2. Clasificación", "Se asigna severidad: crítica (servicio crítico detenido o fuga de datos), alta, media o baja.", "Responsable de Seguridad", "30 minutos"],
        ["3. Contención", "Se aísla el equipo (puerto o VLAN en pfSense), se bloquean las cuentas y se preservan las evidencias.", "Seguridad y Redes", "1 hora si es crítica"],
        ["4. Erradicación y recuperación", "Se elimina la causa y se restaura desde el respaldo, según el orden de la política de recuperación.", "TI", "Según el RTO del servicio"],
        ["5. Comunicación", "Se informa a la dirección (crítica y alta) y, si hay datos personales, a la autoridad y a los afectados dentro de lo que exige la ley.", "Responsable del SGSI", "24 horas si es crítica"],
        ["6. Cierre y aprendizaje", "Informe del incidente, causa raíz y acciones; se actualiza la matriz de riesgos.", "Responsable del SGSI", "5 días hábiles"],
    ])
    r.p("Escalamiento: Responsable de Seguridad, después Jefatura de TI, después Dirección general. Las evidencias se guardan en un repositorio de solo lectura y se registran con fecha, hora y quién las obtuvo.")
    r.h2("Objetivos de recuperación por servicio")
    r.p("Son objetivos de diseño coherentes con la arquitectura (redundancia por servicio y copia fuera de sitio). Se validarán en el ejercicio de recuperación del entregable S2_E3.")
    r.tabla(["Servicio", "Criticidad", "Mecanismo", "RTO objetivo", "RPO objetivo"], [
        ["Active Directory, DNS y DHCP (DC1, DC2)", "Crítica", "Dos controladores con replicación y DHCP en failover", "15 minutos", "Casi cero"],
        ["PostgreSQL (DB01, DB02)", "Crítica", "Réplica en flujo; copia diaria a la nube", "15 minutos (réplica); 4 horas (nube)", "Segundos (réplica); 24 horas (nube)"],
        ["WMS (WMS01, WMS02)", "Crítica", "Nodo activo y nodo en espera", "15 minutos", "Los datos están en PostgreSQL"],
        ["Firewalls (FW-MAIN, FW-BACKUP)", "Crítica", "CARP y pfsync", "Segundos", "Sin pérdida de estado"],
        ["RADIUS (AAA01, AAA02)", "Alta", "Dos servidores", "15 minutos", "Casi cero"],
        ["SIEM, monitoreo y bastión", "Alta", "Restauración desde vzdump", "8 horas", "24 horas"],
        ["Telefonía, correo, archivos, mesa de ayuda", "Media", "Restauración desde respaldo", "24 horas", "24 horas"],
    ])
    r.h2("Plan de continuidad")
    r.bullets(
        "Falla de un servicio redundante: el par asume el servicio y se repone el nodo afectado.",
        "Falla de un hipervisor: los servicios redundantes siguen en los otros cuatro; las máquinas sin par se restauran desde vzdump en otro nodo.",
        "Pérdida de la sede: la VM de borde de Google Cloud coordina la restauración de PostgreSQL desde el bucket; el resto se reconstruye con Terraform y Ansible desde el repositorio.",
        "El plan se revisa cada seis meses con un ejercicio.")

    # ── 9 ───────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Ética de la seguridad de la información")
    r.h2("Código de conducta")
    r.bullets(
        "Actuar con honestidad e integridad; usar los accesos solo para el trabajo para el que fueron otorgados.",
        "Respetar la confidencialidad: no divulgar ni copiar información de la organización, de clientes o de socios.",
        "Cumplir la ley peruana: Ley N.° 29733 de protección de datos personales y su reglamento, y la Ley N.° 30096 de delitos informáticos.",
        "Seguir el código de ética y conducta profesional de la ACM y las normas de la universidad.",
        "No ocultar errores ni incidentes; reportarlos a tiempo.")
    r.h2("Alcance ético de las pruebas")
    r.bullets(
        "Las pruebas de seguridad se hacen solo sobre los sistemas del proyecto: las VLAN y los equipos listados en el inventario y la VPC propia de Google Cloud.",
        "Con autorización escrita del propietario de la organización y en la ventana acordada.",
        "Quedan prohibidos los ataques de denegación de servicio sobre servicios productivos, la ingeniería social contra personas reales y la extracción de datos reales: se prueba con datos de ejemplo.",
        "No se prueban redes de terceros, del proveedor de Internet ni la infraestructura de Google Cloud, solo los recursos propios.",
        "Las herramientas de prueba (escaneo, intrusión) se ejecutan desde equipos del equipo y se detienen ante cualquier efecto no previsto.")
    r.h2("Consentimiento informado")
    r.p("Antes de cualquier prueba que afecte a personas o a sus datos se informa a los afectados del objetivo, el alcance y el tratamiento de los datos, y se obtiene su consentimiento. "
        "La dirección de la organización autoriza por escrito las pruebas técnicas.")
    r.h2("Manejo confidencial de datos")
    r.bullets(
        "Los datos se usan solo para la finalidad declarada y se guardan lo mínimo necesario.",
        "Las capturas y evidencias no incluyen claves, contraseñas, tokens ni datos personales reales; se ocultan antes de entregarlas.",
        "Las evidencias se guardan en un medio de acceso restringido y se eliminan al terminar el proyecto.")
    r.h2("Divulgación responsable")
    r.p("Las vulnerabilidades encontradas se reportan primero y de forma privada al Responsable de Seguridad en un plazo de 24 horas, con el detalle para reproducirlas. "
        "No se publican hasta que estén corregidas o se haya acordado un plazo, y los hallazgos de proveedores se informan a ellos por su canal de reporte.")
    r.h2("Declaración y firmas del equipo")
    r.p("Los integrantes del equipo declaran que conocen y cumplirán este código de ética durante el proyecto.")
    r.tabla(["Nombre y apellidos", "Documento", "Firma", "Fecha"], [["Abel Guevara", "", "", ""], ["", "", "", ""], ["", "", "", ""]])

    # ── 10 ──────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Monitoreo, medición y auditoría interna del SGSI")
    r.h2("Métricas de los objetivos")
    r.p("Valores medidos en la revisión del repositorio de noviembre de 2026:")
    r.tabla(["Indicador", "Meta", "Valor actual", "Estado"], [
        ["Riesgos altos y críticos antes del tratamiento", "—", str(n_alto), "Con plan"],
        ["Riesgos altos y críticos después del tratamiento", "0", str(n_alto_res), "Cumple"],
        ["Controles aplicables implementados", "100 %", f"{RESUMEN.get('Implementado', 0)} de {aplican} ({100 * RESUMEN.get('Implementado', 0) // aplican} %)", "En progreso"],
        ["Controles implementados o parciales", "—", f"{RESUMEN.get('Implementado', 0) + RESUMEN.get('Parcial', 0)} de {aplican}", "En progreso"],
        ["Activos inventariados", "100 % de lo dibujado", str(len(INV)), "Cumple"],
        ["Reglas de firewall escritas", "—", str(datos.resumen_reglas()["total"]), "Pruebas pendientes (S2_E2)"],
        ["No conformidades mayores abiertas", "0", "1", "Acción en curso"],
        ["Ejercicio de recuperación realizado", "1 por semestre", "0", "Pendiente (S2_E3)"],
    ])
    r.h2("Auditoría interna")
    r.p("Criterios: ISO/IEC 27001:2022 (cláusulas 4 a 10 y Anexo A), las políticas de este informe y el diseño del Semestre 1. Método: revisión documental y de configuración del repositorio "
        "cologistic-infra, de los datos del diseño y del estado de Terraform de Google Cloud. No incluyó inspección directa de los equipos. Fecha: noviembre de 2026.")
    r.tabla(["ID", "Hallazgo", "Tipo", "Criterio", "Acción correctiva", "Responsable"], [
        ["H01", "Una contraseña de administrador de Windows está escrita en archivos de instalación desatendida y como valor por defecto en scripts del repositorio.", "No conformidad mayor", "A.5.17, A.8.5",
         "Rotarla, leerla de .env o de la bóveda, y retirarla del historial de Git.", "Responsable de Seguridad"],
        ["H02", "El firewall de la VPC permite UDP 51820 desde cualquier origen y la VM de borde usa la cuenta de servicio por defecto. El diseño pedía solo la IP pública del centro de datos y una cuenta propia.", "No conformidad menor", "A.5.23, A.8.20",
         "Restringir el origen a la IP del centro de datos y asignar una cuenta de servicio dedicada.", "Responsable de Redes"],
        ["H03", "El token de Terraform en Proxmox tiene el rol Administrador sobre todo el cluster.", "No conformidad menor", "A.8.2",
         "Crear un rol con los permisos de VM y almacenamiento y reasignar el token.", "Jefatura de TI"],
        ["H04", "El WAF01 y Vaultwarden usan certificados TLS autofirmados.", "No conformidad menor", "A.8.24",
         "Emitirlos con la autoridad interna step-ca de INFRA01.", "Responsable de Seguridad"],
        ["H05", "El IDS/IPS de pfSense y el extremo WireGuard de pfSense no están automatizados en el repositorio.", "Observación", "A.8.16, A.5.7",
         "Escribir el rol e implementar el IDS; documentar la configuración del túnel.", "Responsable de Redes"],
        ["H06", "Los datos del diseño y lo desplegado difieren: los nombres de los buckets (cologistic-respaldos-sa-west1 en el modelo y cologistic-respaldos-cologistic-cloud en la nube) y el tablero de avance de laboratorio está desactualizado.", "Observación", "A.8.9",
         "Alinear el modelo con lo desplegado y regenerar la especificación; actualizar el tablero.", "Jefatura de TI"],
        ["H07", "La restauración de respaldos no se ha probado todavía.", "Observación", "A.8.13, A.5.30", "Ejecutar el ejercicio de recuperación (entregable S2_E3).", "Responsable de Datos"],
        ["H08", "Los switches no tienen configurado el envío de syslog hacia SIEM01.", "Observación", "A.8.15", "Agregar el servidor de syslog en el rol de switches.", "Responsable de Redes"],
        ["H09", "Los switches C1000 solo ofrecen algoritmos SSH antiguos.", "Observación", "A.8.5", "Riesgo aceptado (R16) hasta actualizar IOS.", "Responsable de Redes"],
    ])
    r.h2("Revisión por la dirección")
    r.p("Todavía no se ha hecho. Está planificada con este informe como entrada, junto con los resultados de la auditoría interna, el estado de los riesgos, las métricas y las acciones correctivas. "
        "La dirección decidirá sobre la política, los recursos y las oportunidades de mejora, y se levantará un acta con fecha y firmas.")

    # ── 11 ──────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Matriz maestra de trazabilidad")
    r.p("Relaciona cada necesidad del negocio con su objetivo, el riesgo, el control que lo trata y la evidencia o el componente real.")
    r.tabla(["Necesidad del negocio", "Objetivo", "Riesgo", "Control", "Evidencia o componente"], [
        ["Operar el WMS sin interrupciones", "Recuperar los servicios críticos", "R03, R10", "A.8.14, A.8.13, A.5.30", "Pares D03, Bareos, bucket de respaldos, ejercicio de recuperación (S2_E3)"],
        ["Proteger la base de datos", "Aplicar los controles", "R06, R18", "A.8.22, A.8.3", "Reglas de bloqueo de pfSense; VLAN 32; pruebas de S2_E2"],
        ["Evitar el movimiento lateral", "Aplicar los controles", "R01, R06, R15", "A.8.22, A.8.20", "18 VLAN en 12 zonas; 146 reglas"],
        ["Administrar de forma controlada", "Aplicar los controles", "R04, R07, R20", "A.5.15, A.8.2, A.8.5", "Bastión, Vaultwarden, RADIUS, rol de Proxmox"],
        ["Detectar intrusiones", "Detectar incidentes a tiempo", "R13", "A.8.15, A.8.16", "SIEM01 (Wazuh), OpenCanary, Zabbix; IDS pendiente"],
        ["Mantener la conectividad con la nube", "Cifrar el enlace", "R08, R09", "A.8.24, A.5.23", "Túnel WireGuard, firewall de la VPC (hallazgo H02)"],
        ["Cambiar sin romper", "Mantener la configuración trazable", "R17", "A.8.9, A.8.32", "Git, Terraform plan, Ansible --check, make verificar"],
        ["Cumplir la ley", "Cumplir la normativa", "R18", "A.5.34, A.5.31", "Política de datos y ética de este informe"],
        ["Seguir si cae la sede", "Recuperar los servicios críticos", "R11", "A.5.29, A.5.30", "Copia fuera de sitio y VM de borde"],
    ])

    # ── 12 ──────────────────────────────────────────────────────────────────────────────────────────────────────
    r.h1("Conclusiones")
    r.bullets(
        "El SGSI cubre todo el alcance de los diseños del Semestre 1 y se apoya en datos reales del repositorio, no en listas genéricas.",
        f"De los 20 riesgos evaluados, {n_alto} están en nivel alto o crítico antes del tratamiento; con los controles previstos ninguno queda en ese nivel.",
        "La auditoría interna encontró una no conformidad mayor, la contraseña en el repositorio, que tiene prioridad. Las demás tienen acción asignada.",
        "Quedan por hacer, y no se declaran como hechas: la aprobación y revisión por la dirección, el ejercicio de recuperación y la ejecución de las pruebas de seguridad.")

    r.biblio(
        "[1] International Organization for Standardization, \"ISO/IEC 27001:2022 Information security management systems — Requirements,\" Geneva, 2022.",
        "[2] International Organization for Standardization, \"ISO/IEC 27002:2022 Information security controls,\" Geneva, 2022.",
        "[3] International Organization for Standardization, \"ISO/IEC 27005:2022 Information security risk management,\" Geneva, 2022.",
        "[4] Congreso de la República del Perú, \"Ley N.° 29733, Ley de Protección de Datos Personales,\" 2011, y su reglamento, D. S. N.° 003-2013-JUS.",
        "[5] Congreso de la República del Perú, \"Ley N.° 30096, Ley de Delitos Informáticos,\" 2013, modificada por la Ley N.° 30171.",
        "[6] Association for Computing Machinery, \"ACM Code of Ethics and Professional Conduct,\" 2018.",
        "[7] Wazuh Inc., \"Wazuh Documentation.\" [Online]. Disponible: https://documentation.wazuh.com/")
    return r
