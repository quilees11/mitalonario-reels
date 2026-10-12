#!/usr/bin/env python3
"""Genera guiones/AAAA-MM-DD.json para los próximos lunes, miércoles y viernes que no tengan guion.
L: DeCA · X: DeI · V: pack (semana ISO par) / historia (semana ISO impar).
Rota ganchos, pantallas y ventajas para no repetir. Uso: python3 generar_guion.py [dias_adelante]"""
import datetime as dt, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
GDIR = os.path.join(BASE, "guiones")
P_DECA, P_DEI, P_PACK = "14,99 €/mes + IVA", "11,99 €/mes + IVA", "21,99 €/mes + IVA"
CIERRE = {"DeCA": "Cartas de Porte · " + P_DECA, "DeI": "Residuos (DeI) · " + P_DEI, "Pack": "Pack DeI + DeCA · " + P_PACK}
PRECIO_TXT = {"DeCA": "Cartas de Porte: " + P_DECA, "DeI": "Residuos (DeI): " + P_DEI, "Pack": "Pack DeI + DeCA: " + P_PACK}
FIN = "15 días gratis, sin tarjeta → mitalonario.es"

# (titulo portada con *resaltado*, subtítulo, etiqueta, primera línea caption)
HOOKS = {
 "DeCA": [
  ("¿Llevas la carta de porte *encima*?", "Desde el 5/10/2026 tiene que ser *digital*", "TRANSPORTISTAS", "¿Llevas la carta de porte encima? 🚛"),
  ("*600 €* de multa en un control", "¿Tu carta de porte es digital?", "TRANSPORTISTAS", "Un control y 600 € de multa 😬"),
  ("La carta de porte, en tu *móvil*", "Sin imprimir nada", "AUTÓNOMOS", "La carta de porte, en tu móvil 📲"),
  ("¿Aún imprimes la *carta de porte*?", "Ya no hace falta", "TRANSPORTISTAS", "¿Aún imprimes la carta de porte? 🖨️"),
  ("3 pasos y estás *en regla*", "Carta de porte digital", "TRANSPORTISTAS", "3 pasos y estás en regla ✅"),
  ("El agente te pide la *carta de porte*", "Tú le enseñas un QR", "TRANSPORTISTAS", "El agente te pide la carta de porte… y tú le enseñas un QR 👮"),
  ("¿Sabes qué es el *DeCA*?", "El documento de control, ya digital", "AUTÓNOMOS", "¿Sabes qué es el DeCA? 🤔"),
  ("Antes de arrancar, *1 minuto*", "Y la carta de porte hecha", "TRANSPORTISTAS", "Antes de arrancar: 1 minuto y la carta de porte hecha ⏱️"),
  ("Cero papeles en la *guantera*", "La carta de porte va en el móvil", "CAMIONEROS", "Cero papeles en la guantera 🙌"),
  ("Tu *camión*, tu oficina", "La carta de porte va contigo", "AUTÓNOMOS", "Tu camión es tu oficina: la carta de porte va contigo 🚚"),
 ],
 "DeI": [
  ("¿Otro DeI *a mano*?", "Hazlo desde el móvil", "CONTENEDORES", "¿Otro DeI a mano? ✍️"),
  ("Residuos de obra *sin papeleo*", "DeI del RD 553/2020", "RESIDUOS", "Residuos de obra sin papeleo ♻️"),
  ("El *vertedero* ya está guardado", "Solo eliges y generas", "CONTENEDORES", "El vertedero ya está guardado. Solo eliges y generas 🗂️"),
  ("Cada cliente, su *carpeta*", "Todos sus DeI ordenados", "CONTENEDORES", "Cada cliente, su carpeta 📁"),
  ("¿Dónde está el DeI de *esa obra*?", "En 2 segundos lo tienes", "RESIDUOS", "¿Dónde está el DeI de esa obra? 🔎"),
  ("Tu DeI con *QR*", "Verificable al instante", "RESIDUOS", "Tu DeI con QR, verificable al instante 📱"),
  ("Del contenedor al *gestor*", "Con el documento listo", "CONTENEDORES", "Del contenedor al gestor, con el documento listo 🚛"),
  ("¿Pierdes tiempo con los *LER*?", "Ya están en la app", "RESIDUOS", "¿Pierdes tiempo con los códigos LER? ⏳"),
  ("Menos oficina, más *contenedores*", "El DeI se hace solo", "CONTENEDORES", "Menos oficina, más contenedores 💪"),
  ("¿Una inspección *mañana*?", "Tus DeI, ordenados y a mano", "RESIDUOS", "¿Una inspección mañana? Tranquilo 😌"),
 ],
 "Pack": [
  ("DeI + carta de porte, *una app*", "Todo lo que necesitas", "CONTENEDORES", "DeI + carta de porte, en una sola app 📲"),
  ("¿Residuos y mercancías? *Un pack*", "Y un solo precio", "TRANSPORTISTAS", "¿Mueves residuos y mercancías? Un pack, un precio 💡"),
  ("Los dos documentos, *ilimitados*", "Pack DeI + DeCA", "AUTÓNOMOS", "Los dos documentos obligatorios, ilimitados ♾️"),
  ("Ahorra con el *pack*", "Y más contratando 12 meses", "PYMES", "Ahorra con el pack (y más si contratas 12 meses) 💸"),
  ("Todo tu papeleo, *en el móvil*", "DeI y carta de porte", "CONTENEDORES", "Todo tu papeleo, en el móvil 📱"),
 ],
 "Historia": [
  ("Paco, *20 años* en el camión", "Y por fin sin papeles", "TRANSPORTISTAS", "Paco lleva 20 años en el camión… y por fin sin papeles 🚛"),
  ("Laura y sus *12 contenedores*", "Ni un DeI perdido", "CONTENEDORES", "Laura tiene 12 contenedores y ni un DeI perdido 🏗️"),
  ("Viernes, 19:00. *Papeles* pendientes", "Hasta que Rubén probó esto", "AUTÓNOMOS", "Viernes, 19:00 y papeles pendientes… hasta que Rubén probó esto 📋"),
  ("Control en la *A-4*", "Y Toni ni se bajó del camión", "TRANSPORTISTAS", "Control en la A-4… y Toni ni se bajó del camión 👮"),
  ("La oficina de *Ana*", "Antes llena de archivadores", "CONTENEDORES", "La oficina de Ana antes estaba llena de archivadores 🗄️"),
 ],
}
SCREENS = {
 "DeCA": [
  [("deca_formulario", "Rellenas *origen y destino*", "Y la mercancía"), ("deca_documento", "PDF oficial con *QR*", "Orden FOM/2861/2012"), ("verificacion_qr", "En el control, *el QR*", "Sin contraseñas")],
  [("deca_formulario", "Lo haces en el *móvil*", "En un minuto"), ("deca_lista", "Todas tus cartas, *numeradas*", "CP-000001, CP-000002..."), ("verificacion_qr", "Documento *íntegro*", "Verificado con QR")],
  [("deca_documento", "El documento *oficial*", "Listo al instante"), ("verificacion_qr", "Se verifica *sin login*", "Solo escaneando el QR"), ("deca_lista", "Tu histórico *a mano*", "En la nube")],
 ],
 "DeI": [
  [("dei_formulario", "Rellenas el *DeI*", "Productor, obra, gestor y LER"), ("dei_documento", "Documento oficial con *QR*", "RD 553/2020"), ("dei_lista", "Guardado en su *carpeta*", "Por cliente")],
  [("dei_lista", "Tus DeI, por *cliente*", "Con sus códigos LER"), ("dei_formulario", "Todo *guardado*", "Clientes, obras y vertederos"), ("verificacion_qr", "Se verifica con el *QR*", "Documento íntegro")],
  [("dei_formulario", "Eliges *obra y vertedero*", "Ya guardados"), ("dei_documento", "Generas el *DeI*", "Oficial y con QR"), ("verificacion_qr", "El gestor lo *verifica*", "Escaneando el QR")],
 ],
 "Pack": [
  [("dei_lista", "Tus *DeI* por cliente", "Con sus códigos LER"), ("deca_lista", "Tus *cartas de porte*", "Numeradas")],
  [("dei_documento", "El *DeI* de residuos", "RD 553/2020"), ("deca_documento", "La *carta de porte*", "Orden FOM/2861/2012")],
 ],
 "Historia": [
  [("deca_formulario", "Ahora la hace *antes de salir*", "Desde el móvil"), ("verificacion_qr", "En el control, *el QR*", "Ni un minuto parado"), ("deca_lista", "Y todo su *histórico*", "En la nube")],
  [("dei_lista", "Cada obra, su *carpeta*", "Lo encuentra en segundos"), ("dei_formulario", "El DeI, *en la obra*", "Desde el móvil"), ("dei_documento", "Oficial y con *QR*", "RD 553/2020")],
 ],
}
LISTAS = {
 "DeCA": [("Evita multas de *401 a 600 €*", ["Todo en la nube", "Documentos ilimitados", "Histórico por QR 7 días", "Sin permanencia"]),
          ("Con *Talonario*", ["Sin imprimir", "Sin contraseñas en el control", "Hash de integridad"]),
          ("Así de *fácil*", ["Desde cualquier móvil", "PDF al instante", "Sin permanencia"])],
 "DeI": [("Lo que te *ahorras*", ["Clientes y vertederos guardados", "Códigos LER listos", "Documentos ilimitados", "Copias de seguridad diarias"]),
         ("En la *nube*", ["Nada se pierde", "Desde cualquier móvil", "Sin permanencia"]),
         ("Para *contenedores*", ["Carpeta por cliente", "DeI con QR", "Más trabajo, menos oficina"])],
 "Pack": [("El *pack* incluye", ["DeI de residuos ilimitados", "Cartas de porte ilimitadas", "Verificación por QR", "Más barato contratando 12 meses"])],
 "Historia": [("Lo que *ganó*", ["Cero papeles", "Cero multas", "Más tiempo para trabajar"]),
              ("Lo que *cambió*", ["Adiós archivadores", "Nada se pierde", "Todo desde el móvil"])],
}
BENEFICIO = {
 "DeCA": ["Desde el 5/10/2026 la carta de porte tiene que ser digital en el transporte público de mercancías, con multas de 401 a 600 €. Con Talonario la haces desde el móvil y en el control solo enseñas el QR.",
          "Rellenas origen, destino y mercancía, y tienes el PDF oficial con QR al instante. Queda en tu histórico y se verifica sin login."],
 "DeI": ["Con Talonario rellenas el DeI de residuos (RD 553/2020) desde el móvil, con clientes, obras, vertederos y códigos LER ya guardados. Cada cliente con su carpeta y cada documento con su QR.",
         "Generas el documento oficial en segundos, queda ordenado por cliente y con copia de seguridad diaria."],
 "Pack": ["Con el pack de Talonario tienes el DeI de residuos y la carta de porte digital en la misma app, ilimitados y con QR. Y si contratas 12 meses, te sale más barato al mes."],
 "Historia": ["Ahora hace sus documentos desde el móvil: la carta de porte o el DeI, con QR y en la nube. Sin papeles, sin multas y con más tiempo para lo importante."],
}
TAGS = {
 "DeCA": ["#cartadeporte #DeCA #transporte #transportistas #autonomos", "#DeCA #cartadeporte #camioneros #logistica #transporte"],
 "DeI": ["#residuos #rcd #contenedores #construccion #autonomos", "#contenedores #gestionderesiduos #rcd #residuos #pymes"],
 "Pack": ["#transporte #residuos #cartadeporte #contenedores #pymes"],
 "Historia": ["#transportistas #contenedores #cartadeporte #residuos #autonomos"],
}
MUSICA = {"DeCA": "energica", "DeI": "optimista", "Pack": "corporativa", "Historia": "corporativa"}
ORIGEN = dt.date(2026, 10, 12)

def tema(d):
    wd = d.weekday()
    if wd == 0: return "DeCA"
    if wd == 2: return "DeI"
    return "Pack" if d.isocalendar()[1] % 2 == 0 else "Historia"

def guion(d):
    t = tema(d); n = (d - ORIGEN).days // 7  # semana desde el inicio
    k = n if t in ("DeCA", "DeI") else n // 2
    h = HOOKS[t][k % len(HOOKS[t])]
    scr = SCREENS[t][(k // len(HOOKS[t]) + k) % len(SCREENS[t])]
    lst = LISTAS[t][k % len(LISTAS[t])]
    precio_tema = "Pack" if t == "Historia" else t
    esc = [{"tipo": "portada", "titulo": h[0], "texto": h[1], "etiqueta": h[2]}]
    esc += [{"tipo": "pantalla", "captura": c, "titulo": a, "texto": b} for c, a, b in scr]
    esc += [{"tipo": "lista", "titulo": lst[0], "puntos": lst[1]},
            {"tipo": "cierre", "titulo": "*15 días gratis*", "texto": "Sin tarjeta. Sin permanencia.", "precio": CIERRE[precio_tema]}]
    cap = "\n\n".join([h[3], BENEFICIO[t][k % len(BENEFICIO[t])], PRECIO_TXT[precio_tema] + "\n" + FIN, TAGS[t][k % len(TAGS[t])]])
    assert len(cap) <= 600
    return {"tema": t, "musica": MUSICA[t], "escenas": esc, "caption": cap, "generado": "automatico"}

if __name__ == "__main__":
    dias = int(sys.argv[1]) if len(sys.argv) > 1 else 14
    hoy = dt.date.today(); os.makedirs(GDIR, exist_ok=True)
    for i in range(dias + 1):
        d = hoy + dt.timedelta(days=i)
        if d.weekday() not in (0, 2, 4): continue
        f = os.path.join(GDIR, f"{d.isoformat()}.json")
        if os.path.exists(f): continue
        json.dump(guion(d), open(f, "w"), ensure_ascii=False, indent=1)
        print("Guion nuevo:", d)
