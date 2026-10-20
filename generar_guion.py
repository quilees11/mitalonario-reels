#!/usr/bin/env python3
"""Genera guiones/AAAA-MM-DD.json para los próximos días que no tengan guion: UN reel diario.
Martes, sábado y domingo: reel de la suite Talonario (qué hace y sus ventajas, sin un módulo concreto).
Lunes, miércoles, jueves y viernes: un módulo por día, rotando en este orden: Residuos (DeI) · Cartas de Porte (DeCA) ·
Gestor de Contraseñas · Sistema de Fichajes · Soporte Informático. Dentro de cada módulo rota ganchos, pantallas y ventajas
para no repetir. Duración fija de cada escena: 3,4 + 4,0 x 3 + 4,8 + 5,0 = 25,2 s (entre 23 y 27 s).
No se promocionan la licencia de facturación "Talonario" ni las Copias de seguridad.
Uso: python3 generar_guion.py [dias_adelante]"""
import datetime as dt, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
GDIR = os.path.join(BASE, "guiones")
ORDEN = ["DeI", "DeCA", "Boveda", "Fichajes", "Soporte"]
ORIGEN = dt.date(2026, 10, 21)          # 21/10/2026 (miércoles) = Residuos (DeI)
DIAS_SUITE = (1, 5, 6)                   # martes, sábado, domingo
DUR = {"portada": 3.4, "pantalla": 4.0, "lista": 4.8, "cierre": 5.0}
CONTACTO = "a.esteban@mitalonario.es · WhatsApp 676 60 11 34"
CONTACTO_CAP = "📩 a.esteban@mitalonario.es\n📱 WhatsApp 676 60 11 34"

PRECIO = {
 "DeI": "Residuos (DeI) · 11,99 €/mes + IVA",
 "DeCA": "Cartas de Porte · 14,99 €/mes + IVA",
 "Boveda": "Gestor de Contraseñas · 14,99 €/mes + IVA",
 "Fichajes": "Sistema de Fichajes · 14,99 €/mes + IVA",
 "Soporte": "Presupuesto a medida",
 "Suite": "Módulos desde 11,99 €/mes + IVA",
}
PRECIO_CAP = {
 "DeI": "💶 Residuos (DeI): 11,99 €/mes + IVA · 15 días gratis en mitalonario.es",
 "DeCA": "💶 Cartas de Porte: 14,99 €/mes + IVA · 15 días gratis en mitalonario.es",
 "Boveda": "💶 Gestor de Contraseñas: 14,99 €/mes + IVA · 15 días gratis en mitalonario.es",
 "Fichajes": "💶 Sistema de Fichajes: 14,99 €/mes + IVA · 15 días gratis en mitalonario.es",
 "Soporte": "💶 Servicio a medida: te preparo un presupuesto sin compromiso.",
 "Suite": "💶 Pagas solo los módulos que usas, desde 11,99 €/mes + IVA · 15 días gratis en mitalonario.es",
}
CIERRE = {  # titulo, texto, web
 "DeI": ("*15 días gratis*", "Sin tarjeta. Sin permanencia.", "mitalonario.es"),
 "DeCA": ("*15 días gratis*", "Sin tarjeta. Sin permanencia.", "mitalonario.es"),
 "Boveda": ("*15 días gratis*", "Sin tarjeta. Sin permanencia.", "mitalonario.es"),
 "Fichajes": ("*15 días gratis*", "Sin tarjeta. Sin permanencia.", "mitalonario.es"),
 "Soporte": ("*Hablemos*", "Valoración gratis y sin compromiso", ""),
 "Suite": ("*15 días gratis*", "Sin tarjeta. Sin permanencia.", "mitalonario.es"),
}

# (titulo portada con *resaltado*, subtítulo, etiqueta, primera línea del caption)
HOOKS = {
 "DeI": [
  ("¿Otro DeI *a mano*?", "Hazlo desde el móvil", "CONTENEDORES", "¿Otro DeI a mano? ✍️"),
  ("Residuos de obra *sin papeleo*", "DeI del RD 553/2020", "RESIDUOS", "Residuos de obra sin papeleo ♻️"),
  ("Cada cliente, su *carpeta*", "Todos sus DeI ordenados", "CONTENEDORES", "Cada cliente, su carpeta 📁"),
  ("¿Dónde está el DeI de *esa obra*?", "En 2 segundos lo tienes", "RESIDUOS", "¿Dónde está el DeI de esa obra? 🔎"),
  ("¿Pierdes tiempo con los *LER*?", "Ya están en la app", "RESIDUOS", "¿Pierdes tiempo con los códigos LER? ⏳"),
  ("¿Una inspección *mañana*?", "Tus DeI, ordenados y a mano", "RESIDUOS", "¿Una inspección mañana? Tranquilo 😌"),
 ],
 "DeCA": [
  ("¿Llevas la carta de porte *encima*?", "Tiene que ser *digital*", "TRANSPORTISTAS", "¿Llevas la carta de porte encima? 🚛"),
  ("*600 €* de multa en un control", "¿Tu carta de porte es digital?", "TRANSPORTISTAS", "Un control y hasta 600 € de multa 😬"),
  ("La carta de porte, en tu *móvil*", "Sin imprimir nada", "AUTÓNOMOS", "La carta de porte, en tu móvil 📲"),
  ("El agente te pide la *carta de porte*", "Tú le enseñas un QR", "TRANSPORTISTAS", "El agente te pide la carta de porte… y tú le enseñas un QR 👮"),
  ("Cero papeles en la *guantera*", "La carta de porte va en el móvil", "CAMIONEROS", "Cero papeles en la guantera 🙌"),
  ("Antes de arrancar, *1 minuto*", "Y la carta de porte hecha", "TRANSPORTISTAS", "Antes de arrancar: 1 minuto y la carta de porte hecha ⏱️"),
 ],
 "Boveda": [
  ("¿Tus contraseñas en un *Excel*?", "Es lo primero que roban", "CIBERSEGURIDAD", "¿Las contraseñas de tu empresa están en un Excel? 😱"),
  ("El *post-it* del monitor", "Tiene los días contados", "PYMES", "Ese post-it con la contraseña del banco… 🟨"),
  ("Se va un empleado. ¿Y las *claves*?", "Con una bóveda, controlas quién ve qué", "EMPRESAS", "Se va un empleado… ¿y las contraseñas que sabía? 🔑"),
  ("Todas tus claves, *bajo llave*", "Cifradas de extremo a extremo", "SEGURIDAD", "Todas las claves de tu negocio, bajo llave 🔐"),
  ("¿Mandas contraseñas por *WhatsApp*?", "Compártelas de forma segura", "PYMES", "¿Sigues mandando contraseñas por WhatsApp? 📵"),
  ("Una sola contraseña *para todo*", "La tuya. El resto, en la bóveda", "AUTÓNOMOS", "Recuerda una sola contraseña. El resto, en la bóveda 🧠"),
 ],
 "Fichajes": [
  ("¿Aún fichas en *papel*?", "El registro de jornada es obligatorio", "EMPRESAS", "¿Tu equipo todavía ficha en papel? 📝"),
  ("Inspección de trabajo: *¿estás listo?*", "Que no te pille sin registro", "PYMES", "Si mañana llega una inspección de trabajo… ¿tienes el registro de jornada? 👀"),
  ("Tu equipo ficha *desde el móvil*", "En un toque", "EMPRESAS", "Tu equipo ficha desde el móvil, en un toque 📲"),
  ("Adiós al *reloj de fichar*", "Y a las hojas que se pierden", "HOSTELERÍA · COMERCIO", "Adiós al reloj de fichar y a las hojas de firmas 👋"),
  ("¿Cuántas horas hizo *cada uno*?", "Lo ves al momento", "PYMES", "¿Cuántas horas ha hecho cada uno este mes? Lo ves al momento ⏱️"),
  ("Trabajan *fuera de la oficina*", "Y fichan igual", "OBRAS · REPARTO", "¿Tu equipo trabaja en la calle o en obra? Fichan igual 🚐"),
 ],
 "Suite": [
  ("Tu empresa, en *una sola app*", "Documentos, equipo y seguridad", "TALONARIO", "Todo tu negocio en una sola app 📲"),
  ("Menos *papeles*, más trabajo", "Talonario lo hace por ti", "AUTÓNOMOS · PYMES", "Menos papeles y más tiempo para trabajar 💪"),
  ("¿Cuántas apps usas *para todo*?", "Con una te basta", "PYMES", "¿Cuántas aplicaciones usas para llevar tu negocio? 🤯"),
  ("Hecho para *contenedores y transporte*", "Y para cualquier pyme", "TALONARIO", "Hecho para contenedores y transporte… y para cualquier pyme 🚛"),
  ("Desde el *móvil*, en la nube", "Tu oficina va contigo", "TALONARIO", "Tu oficina va contigo, en el móvil ☁️"),
  ("Pagas *solo lo que usas*", "Módulos a tu medida", "AUTÓNOMOS · PYMES", "Pagas solo los módulos que usas 🧩"),
 ],
 "Soporte": [
  ("¿Sin *informático* en tu empresa?", "Yo me encargo", "SOPORTE INFORMÁTICO", "¿Tu empresa no tiene informático? Yo me encargo 💻"),
  ("El ordenador falla *a la peor hora*", "Y alguien lo arregla hoy", "PYMES", "Cuando el ordenador falla a la peor hora… 😩"),
  ("¿Estás protegido del *ransomware*?", "Revisamos tu seguridad", "CIBERSEGURIDAD", "¿Tu negocio está protegido frente al ransomware? 🛡️"),
  ("Remoto o *presencial*", "Soporte para autónomos y pymes", "SOPORTE INFORMÁTICO", "Soporte informático remoto y presencial 🧰"),
  ("¿Qué tecnología *necesitas* de verdad?", "Antes de gastar, pregunta", "CONSULTORÍA IT", "Antes de gastar en tecnología, pregunta 💡"),
  ("Tu oficina, *sin sustos*", "Equipos, red y accesos al día", "PYMES", "Tu oficina sin sustos informáticos ✅"),
 ],
}
SCREENS = {
 "DeI": [
  [("dei_formulario", "Rellenas el *DeI*", "Productor, obra, gestor y LER"), ("dei_documento", "Documento oficial con *QR*", "RD 553/2020"), ("dei_lista", "Guardado en su *carpeta*", "Por cliente")],
  [("dei_lista", "Tus DeI, por *cliente*", "Con sus códigos LER"), ("dei_formulario", "Todo *guardado*", "Clientes, obras y vertederos"), ("verificacion_qr", "Se verifica con el *QR*", "Documento íntegro")],
  [("dei_formulario", "Eliges *obra y vertedero*", "Ya guardados"), ("dei_documento", "Generas el *DeI*", "Oficial y con QR"), ("verificacion_qr", "El gestor lo *verifica*", "Escaneando el QR")],
 ],
 "DeCA": [
  [("deca_formulario", "Rellenas *origen y destino*", "Y la mercancía"), ("deca_documento", "PDF oficial con *QR*", "Orden FOM/2861/2012"), ("verificacion_qr", "En el control, *el QR*", "Sin contraseñas")],
  [("deca_formulario", "Lo haces en el *móvil*", "En un minuto"), ("deca_lista", "Todas tus cartas, *numeradas*", "CP-000001, CP-000002..."), ("verificacion_qr", "Documento *íntegro*", "Verificado con QR")],
  [("deca_documento", "El documento *oficial*", "Listo al instante"), ("verificacion_qr", "Se verifica *sin login*", "Solo escaneando el QR"), ("deca_lista", "Tu histórico *a mano*", "En la nube")],
 ],
 "Boveda": [
  [("boveda_maestra", "Solo tú tienes *la llave*", "Una contraseña maestra"), ("boveda_lista", "Todas tus *claves*", "Banco, Hacienda, correo..."), ("boveda_detalle", "Copias y *listo*", "Sin verla en pantalla")],
  [("boveda_lista", "Todo *en un sitio*", "Ordenado y cifrado"), ("boveda_detalle", "Compártela *segura*", "Sin WhatsApp ni papel"), ("boveda_maestra", "Cifrado *de extremo a extremo*", "Ni nosotros podemos verlas")],
  [("boveda_detalle", "Usuario, clave y *web*", "En una ficha"), ("boveda_maestra", "Bloqueada con *tu maestra*", "Nadie más entra"), ("boveda_lista", "Desde cualquier *dispositivo*", "En la nube")],
 ],
 "Fichajes": [
  [("fichajes_movil", "Fichan *desde el móvil*", "Entrada, pausas y salida"), ("fichajes_panel", "Tú lo ves *al momento*", "Toda la plantilla"), ("fichajes_informe", "Registro *listo*", "Para la inspección")],
  [("fichajes_panel", "¿Quién está *trabajando*?", "En tiempo real"), ("fichajes_movil", "Cada empleado, *su portal*", "Con su propio acceso"), ("fichajes_informe", "Informe *mensual*", "Por empleado")],
  [("fichajes_informe", "Todo *registrado*", "Día a día"), ("fichajes_movil", "Un toque y *fichado*", "Sin relojes"), ("fichajes_panel", "Horas de *cada uno*", "Sin hojas de firmas")],
 ],
 "Suite": [
  [("suite_inicio", "Todo en *un panel*", "Lo de hoy, de un vistazo"), ("deca_documento", "Documentos *oficiales*", "Con QR verificable"), ("fichajes_movil", "Tu equipo, *conectado*", "Fichan desde el móvil")],
  [("suite_inicio", "Una app, *todos tus módulos*", "Elige los que necesites"), ("dei_formulario", "Rellenas en *un minuto*", "Todo guardado"), ("boveda_lista", "Y tus claves, *seguras*", "Cifradas")],
  [("verificacion_qr", "Documentos *verificables*", "Con su QR, sin login"), ("suite_inicio", "Todo *ordenado*", "En la nube"), ("fichajes_panel", "Tu plantilla, *bajo control*", "En tiempo real")],
 ],
 "Soporte": [
  [("soporte_incidencias", "Incidencias *resueltas*", "Remoto o presencial"), ("soporte_seguridad", "Tu seguridad, *revisada*", "Equipos, red y accesos"), ("soporte_incidencias", "Un solo *interlocutor*", "Para toda tu tecnología")],
  [("soporte_seguridad", "Protección frente a *ransomware*", "Antes de que pase"), ("soporte_incidencias", "Te lo arreglo *hoy*", "Sin esperas eternas"), ("soporte_seguridad", "Accesos y contraseñas *en orden*", "Cumpliendo el RGPD")],
 ],
}
LISTAS = {
 "DeI": [("Lo que te *ahorras*", ["Clientes y vertederos guardados", "Códigos LER listos", "Documentos ilimitados", "Desde cualquier móvil"]),
         ("En la *nube*", ["Nada se pierde", "Carpeta por cliente", "Sin permanencia"]),
         ("Para *contenedores*", ["DeI con QR", "Más trabajo, menos oficina", "Soporte directo"])],
 "DeCA": [("Evita multas de *401 a 600 €*", ["Todo en la nube", "Documentos ilimitados", "Verificación por QR", "Sin permanencia"]),
          ("Con *Talonario*", ["Sin imprimir", "Sin contraseñas en el control", "Hash de integridad"]),
          ("Así de *fácil*", ["Desde cualquier móvil", "PDF al instante", "Sin permanencia"])],
 "Boveda": [("Con tu *bóveda*", ["Cifrado de extremo a extremo", "Una sola contraseña maestra", "Compartir sin riesgos", "Sin permanencia"]),
            ("Adiós a *Excel y post-its*", ["Todo cifrado", "Accesible desde el móvil", "Solo tú tienes la llave"]),
            ("Tu negocio, *más seguro*", ["Claves del banco y Hacienda", "Correo y redes sociales", "Wifi y proveedores"])],
 "Fichajes": [("Con el *Sistema de Fichajes*", ["Cumples el registro de jornada", "Fichaje desde el móvil", "Portal del empleado", "Sin permanencia"]),
              ("Se *acabó*", ["Hojas de firmas", "Relojes de fichar", "Cuentas de horas a mano"]),
              ("Para *tu plantilla*", ["Oficina, obra o reparto", "Informes por empleado", "Listo ante una inspección"])],
 "Suite": [("Con *Talonario*", ["DeI y Cartas de Porte con QR", "Fichajes de tu plantilla", "Contraseñas cifradas", "Desde el móvil y en la nube"]),
           ("Por qué *Talonario*", ["Pagas solo lo que usas", "Sin permanencia", "Soporte directo del equipo que lo programa"]),
           ("Hecho *para ti*", ["Contenedores y transporte", "Autónomos y pymes", "Listo ante inspecciones"])],
 "Soporte": [("Te *ayudo* con", ["Soporte remoto y presencial", "Sistemas y ciberseguridad", "Consultoría IT", "Para autónomos y pymes"]),
             ("Sin *sustos*", ["Equipos y red al día", "Protección frente a ataques", "Un técnico de confianza"])],
}
BENEFICIO = {
 "DeI": ["Con Talonario rellenas el DeI de residuos (RD 553/2020) desde el móvil, con clientes, obras, vertederos y códigos LER ya guardados. Cada cliente con su carpeta y cada documento con su QR.",
         "Generas el documento oficial en segundos y queda ordenado por cliente, listo para cualquier inspección."],
 "DeCA": ["La carta de porte tiene que ser digital en el transporte público de mercancías, con multas de 401 a 600 €. Con Talonario la haces desde el móvil y en el control solo enseñas el QR.",
          "Rellenas origen, destino y mercancía, y tienes el PDF oficial con QR al instante. Queda en tu histórico y se verifica sin login."],
 "Boveda": ["Guarda todas las contraseñas de tu negocio (banco, Hacienda, correo, proveedores, redes) en una bóveda cifrada de extremo a extremo. Solo tú tienes la llave: ni nosotros podemos verlas.",
            "Deja de guardar claves en Excel, papel o el navegador. Copia y comparte contraseñas de forma segura, sin enviarlas por WhatsApp."],
 "Fichajes": ["El registro de jornada es obligatorio para cualquier empresa con empleados y no tenerlo puede acabar en multa de la Inspección de Trabajo. Con el Sistema de Fichajes de Talonario tu equipo ficha desde el móvil y tú lo controlas todo.",
              "Cada empleado tiene su propio portal para fichar entrada, pausas y salida. Tú ves las horas de toda la plantilla y sacas el registro mensual en un clic."],
 "Suite": ["Talonario reúne en una sola app los documentos que te exige la normativa (DeI de residuos y cartas de porte con QR), el registro de jornada de tu equipo y un gestor de contraseñas cifrado. Desde el móvil, en la nube y sin permanencia.",
           "Eliges solo los módulos que necesitas y lo tienes todo ordenado en un panel. Hecho para empresas de contenedores y transporte, y para cualquier autónomo o pyme que quiera menos papeles."],
 "Soporte": ["Soy Adrián Esteban y ayudo a autónomos y pymes con su tecnología: soporte remoto y presencial, administración de sistemas y ciberseguridad, y consultoría IT.",
             "Incidencias resueltas sin esperas, equipos y red al día, protección frente a ransomware y un técnico de confianza para todo lo que tenga que ver con informática."],
}
TAGS = {
 "DeI": ["#residuos #rcd #contenedores #construccion #gestionderesiduos #autonomos #mitalonario",
         "#contenedores #gestionderesiduos #rcd #residuos #obras #pymes #mitalonario"],
 "DeCA": ["#cartadeporte #DeCA #transporte #transportistas #autonomos #camioneros #mitalonario",
          "#DeCA #cartadeporte #logistica #transporte #camion #pymes #mitalonario"],
 "Boveda": ["#ciberseguridad #contraseñas #gestordecontraseñas #pymes #autonomos #seguridadinformatica #mitalonario",
            "#contraseñas #ciberseguridad #empresas #proteccióndedatos #negocios #pymes #mitalonario"],
 "Fichajes": ["#registrodejornada #fichajes #controlhorario #rrhh #pymes #empresas #mitalonario",
              "#fichaje #registrohorario #inspecciondetrabajo #autonomos #pymes #recursoshumanos #mitalonario"],
 "Suite": ["#mitalonario #pymes #autonomos #transporte #contenedores #digitalizacion #software",
           "#mitalonario #digitalizacion #empresas #gestion #pymes #residuos #cartadeporte"],
 "Soporte": ["#soporteinformatico #informatica #ciberseguridad #pymes #autonomos #consultoriait #madrid",
             "#tecnico #informaticamadrid #ciberseguridad #ransomware #pymes #sistemas #madrid"],
}
MUSICA = {"Suite": "energica", "DeI": "optimista", "DeCA": "energica", "Boveda": "corporativa", "Fichajes": "optimista", "Soporte": "corporativa"}
NOMBRE = {"DeI": "Residuos (DeI)", "DeCA": "Cartas de Porte (DeCA)", "Boveda": "Gestor de Contraseñas", "Fichajes": "Sistema de Fichajes", "Soporte": "Soporte Informático", "Suite": "Talonario (suite)"}


def n_modulo(d):
    """Cuántos días de módulo (no de suite) hay desde ORIGEN hasta d, sin contar d."""
    return sum(1 for i in range((d - ORIGEN).days) if (ORIGEN + dt.timedelta(days=i)).weekday() not in DIAS_SUITE)


def tema(d):
    if d.weekday() in DIAS_SUITE: return "Suite"
    return ORDEN[n_modulo(d) % len(ORDEN)]


def guion(d):
    t = tema(d)
    if t == "Suite":
        k = sum(1 for i in range((d - ORIGEN).days) if (ORIGEN + dt.timedelta(days=i)).weekday() in DIAS_SUITE)
    else:
        k = n_modulo(d) // len(ORDEN)   # vuelta número k para este módulo
    h = HOOKS[t][k % len(HOOKS[t])]
    scr = SCREENS[t][k % len(SCREENS[t])]
    lst = LISTAS[t][k % len(LISTAS[t])]
    tit, txt, web = CIERRE[t]
    esc = [{"tipo": "portada", "titulo": h[0], "texto": h[1], "etiqueta": h[2], "duracion": DUR["portada"]}]
    esc += [{"tipo": "pantalla", "captura": c, "titulo": a, "texto": b, "duracion": DUR["pantalla"]} for c, a, b in scr]
    esc += [{"tipo": "lista", "titulo": lst[0], "puntos": lst[1], "duracion": DUR["lista"]},
            {"tipo": "cierre", "titulo": tit, "texto": txt, "precio": PRECIO[t], "web": web, "contacto": CONTACTO, "duracion": DUR["cierre"]}]
    total = sum(e["duracion"] for e in esc)
    assert 23 <= total <= 27, total
    cap = "\n\n".join([h[3], BENEFICIO[t][k % len(BENEFICIO[t])], PRECIO_CAP[t], CONTACTO_CAP, TAGS[t][k % len(TAGS[t])]])
    assert len(cap) <= 2000
    return {"tema": t, "modulo": NOMBRE[t], "musica": MUSICA[t], "duracion": round(total, 1), "escenas": esc, "caption": cap, "generado": "automatico"}


if __name__ == "__main__":
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    hoy = dt.date.today(); os.makedirs(GDIR, exist_ok=True)
    for i in range(dias + 1):
        d = hoy + dt.timedelta(days=i)
        if d < ORIGEN: continue
        f = os.path.join(GDIR, f"{d.isoformat()}.json")
        if os.path.exists(f): continue
        json.dump(guion(d), open(f, "w"), ensure_ascii=False, indent=1)
        print("Guion nuevo:", d, tema(d))
