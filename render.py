#!/usr/bin/env python3
"""Reel vertical 1080x1920 de Talonario con música sintetizada (libre de derechos).
Requisitos: ffmpeg, pip install pillow numpy qrcode. Fuentes Inter en ./fonts (licencia OFL).
Guion JSON: {"escenas":[{tipo:portada|pantalla|lista|cierre, titulo, texto?, etiqueta?, captura?, puntos?, precio?, duracion?}]}
Capturas (maquetas): deca_formulario, deca_lista, deca_documento, dei_formulario, dei_lista, dei_documento, verificacion_qr,
fichajes_movil, fichajes_panel, fichajes_informe, boveda_lista, boveda_detalle, boveda_maestra, soporte_incidencias, soporte_seguridad.
Cierre: {titulo, texto, precio?, web? (por defecto mitalonario.es; "" para ocultar), contacto?}."""
import math, subprocess, sys, wave
import numpy as np
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
if len(sys.argv) < 3:
    sys.exit("uso: python3 render.py salida.mp4 guion.json [--preview]  (guion: {\"escenas\":[...]} mismo formato que crear_reel)")
OUT = sys.argv[1]
import os
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Inter-%s.otf")
def font(w, s): return ImageFont.truetype(F % w, s)

BG1, BG2 = (12, 22, 40), (22, 38, 66)
ORANGE, WHITE, MUTED = (255, 122, 26), (255, 255, 255), (170, 184, 206)
CARD, INK, LINE, GREEN = (255, 255, 255), (24, 32, 48), (222, 228, 238), (34, 170, 96)

# ---------- utilidades ----------
def bg():
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(BG1) * (1 - g[..., None]) + np.array(BG2) * g[..., None]).astype(np.uint8)
    arr = np.broadcast_to(arr, (H, W, 3)).copy()
    im = Image.fromarray(arr).convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse((600, -300, 1500, 600), fill=(255, 122, 26, 60))
    d.ellipse((-500, 1400, 400, 2300), fill=(60, 120, 255, 45))
    return Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(160)))
BG = bg()

def rich(text, fnt, maxw, color=WHITE, hl=ORANGE, align="center", spacing=1.18):
    """Texto con *resaltado*, ajustado a ancho. Devuelve RGBA."""
    words, on = [], False
    for part in text.split("*"):
        for k, w in enumerate(part.split()):
            if k == 0 and words and not part[0].isspace() and w[0] in "?!.,:;":
                words.append(("\x00" + w, on))
            else:
                words.append((w, on))
        on = not on
    merged = []
    for w, h in words:
        if w.startswith("\x00") and merged:
            pw, ph = merged[-1]; merged[-1] = (pw, ph); merged.append((w[1:], h, True))
        else:
            merged.append((w, h))
    words = []
    for it in merged:
        if len(it) == 3 and words:
            pw, ph = words[-1]; words[-1] = ((pw, ph), (it[0], it[1]))
        else:
            words.append(it[:2])
    # aplanar: cada palabra es lista de segmentos
    words = [list(w) if isinstance(w[0], tuple) else [w] for w in words]
    lines, cur = [], []
    sp = fnt.getlength(" ")
    def width(ws): return sum(fnt.getlength(t) for w in ws for t, _ in w) + sp * (len(ws) - 1)
    for w in words:
        if cur and width(cur + [w]) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    asc, desc = fnt.getmetrics(); lh = int((asc + desc) * spacing)
    im = Image.new("RGBA", (maxw, lh * len(lines) + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        lw = width(ln)
        x = (maxw - lw) / 2 if align == "center" else 0
        for w in ln:
            for t, h in w:
                d.text((x, i * lh), t, font=fnt, fill=hl if h else color)
                x += fnt.getlength(t)
            x += sp
    return im

def pill(text, fnt, fg, bgc, padx=34, pady=16):
    tw = fnt.getlength(text); asc, desc = fnt.getmetrics()
    im = Image.new("RGBA", (int(tw + 2 * padx), asc + desc + 2 * pady), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=bgc)
    d.text((padx, pady), text, font=fnt, fill=fg)
    return im

def shadow(im, r=40, off=24, a=110):
    pad = r * 2
    s = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2 + off), (0, 0, 0, 0))
    mask = im.split()[3].point(lambda v: a if v > 0 else 0)
    s.paste((0, 0, 0, 255), (pad, pad + off), mask)
    s = s.filter(ImageFilter.GaussianBlur(r))
    s.alpha_composite(im, (pad, pad))
    return s

def phone(content):
    """Marco de móvil con contenido 760x1360."""
    pw, ph = 820, 1440
    im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=90, fill=(8, 12, 20))
    scr = Image.new("RGBA", (pw - 60, ph - 60), (0, 0, 0, 0))
    m = Image.new("L", scr.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, scr.width - 1, scr.height - 1), radius=64, fill=255)
    scr.paste(content.resize(scr.size), (0, 0), m)
    im.alpha_composite(scr, (30, 30))
    d.rounded_rectangle((pw // 2 - 90, 48, pw // 2 + 90, 92), radius=22, fill=(8, 12, 20))
    return shadow(im)

def appbar(d, title, w):
    d.rectangle((0, 0, w, 210), fill=(16, 30, 56))
    d.text((48, 120), title, font=font("Bold", 46), fill=WHITE)
    d.text((48, 70), "Talonario", font=font("SemiBold", 30), fill=ORANGE)

def field(d, x, y, w, label, value):
    d.text((x, y), label, font=font("SemiBold", 28), fill=(110, 122, 142))
    d.rounded_rectangle((x, y + 42, x + w, y + 132), radius=18, fill=(246, 248, 252), outline=LINE, width=3)
    d.text((x + 26, y + 66), value, font=font("Medium", 34), fill=INK)

def qr_img(size):
    q = qrcode.QRCode(border=1, box_size=10); q.add_data("https://mitalonario.es"); q.make()
    return q.make_image(fill_color=(20, 26, 40), back_color="white").convert("RGBA").resize((size, size), Image.NEAREST)

# ---------- pantallas simuladas ----------
SW, SH = 760, 1380
def scr_form():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Nueva Carta de Porte", SW)
    d.rounded_rectangle((32, 250, SW - 32, 1250), radius=30, fill=CARD)
    d.text((64, 285), "1 · Origen y destino", font=font("Bold", 36), fill=INK)
    field(d, 64, 360, SW - 128, "Origen", "Polígono Ind. Sur, Getafe")
    field(d, 64, 520, SW - 128, "Destino", "Av. del Puerto 12, Valencia")
    d.text((64, 700), "2 · Mercancía", font=font("Bold", 36), fill=INK)
    field(d, 64, 770, SW - 128, "Descripción", "Palés de material cerámico")
    field(d, 64, 930, (SW - 160) // 2, "Peso (kg)", "8.400")
    field(d, 96 + (SW - 160) // 2, 930, (SW - 160) // 2, "Bultos", "22")
    d.rounded_rectangle((64, 1120, SW - 64, 1215), radius=24, fill=ORANGE)
    t = "Generar DeCA"; f = font("Bold", 38)
    d.text(((SW - f.getlength(t)) / 2, 1142), t, font=f, fill=WHITE)
    return im

def scr_pdf():
    im = Image.new("RGBA", (SW, SH), (90, 98, 112)); d = ImageDraw.Draw(im)
    d.rectangle((40, 60, SW - 40, SH - 40), fill=WHITE)
    d.text((80, 100), "DOCUMENTO DE CONTROL", font=font("Black", 40), fill=INK)
    d.text((80, 152), "Carta de Porte · Orden FOM/2861/2012", font=font("Medium", 26), fill=(100, 110, 130))
    d.text((80, 196), "Nº CP-000148", font=font("Bold", 30), fill=ORANGE)
    y = 270
    for lab, val in [("Cargador", "Transportes Ejemplo S.L."), ("Transportista", "Autónomo · 1234-ABC"),
                     ("Origen", "Getafe (Madrid)"), ("Destino", "Valencia"),
                     ("Mercancía", "Material cerámico · 8.400 kg"), ("Fecha", "12/10/2026")]:
        d.line((80, y, SW - 80, y), fill=LINE, width=2)
        d.text((80, y + 22), lab, font=font("SemiBold", 26), fill=(110, 122, 142))
        d.text((80, y + 60), val, font=font("Medium", 32), fill=INK)
        y += 130
    q = qr_img(230); im.alpha_composite(q, ((SW - 230) // 2, 1040))
    t = "Verificar con QR"; f = font("SemiBold", 26)
    d.text(((SW - f.getlength(t)) / 2, 1278), t, font=f, fill=(110, 122, 142))
    return im

def scr_verif():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, SW, 190), fill=WHITE)
    d.rounded_rectangle((40, 100, SW - 40, 160), radius=28, fill=(238, 242, 248))
    d.text((70, 112), "mitalonario.es/verificar", font=font("Medium", 28), fill=(90, 100, 120))
    d.rounded_rectangle((40, 230, SW - 40, 1000), radius=34, fill=CARD)
    cx = SW // 2
    d.ellipse((cx - 110, 260, cx + 110, 480), fill=(225, 246, 234))
    d.line([(cx - 52, 372), (cx - 12, 412), (cx + 60, 330)], fill=GREEN, width=22, joint="curve")
    for t, f, c, y in [("Íntegro", font("Black", 72), GREEN, 520),
                       ("Documento verificado", font("SemiBold", 36), INK, 625),
                       ("No ha sido modificado", font("Medium", 30), (110, 122, 142), 680)]:
        d.text(((SW - f.getlength(t)) / 2, y), t, font=f, fill=c)
    d.line((90, 760, SW - 90, 760), fill=LINE, width=2)
    for i, (a, b) in enumerate([("Documento", "CP-000148"), ("Emitido", "12/10/2026 07:42"), ("Acceso", "Sin login")]):
        y = 790 + i * 62
        d.text((90, y), a, font=font("Medium", 30), fill=(110, 122, 142))
        f = font("Bold", 30); d.text((SW - 90 - f.getlength(b), y), b, font=f, fill=INK)
    return im

def scr_list(kind):
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    if kind == "deca":
        appbar(d, "Cartas de Porte", SW)
        rows = [("CP-%06d" % n, a, b) for n, a, b in [(148, "Getafe → Valencia", "12/10"), (147, "Coslada → Zaragoza", "11/10"),
                (146, "Alcalá → Toledo", "10/10"), (145, "Leganés → Sevilla", "09/10"), (144, "Pinto → Burgos", "08/10"),
                (143, "Móstoles → Murcia", "07/10")]]
    else:
        appbar(d, "Construcciones Ejemplo", SW)
        rows = [("DeI-%04d" % n, a, b) for n, a, b in [(52, "LER 17 01 07 · Hormigón", "12/10"), (51, "LER 17 09 04 · Mixtos", "11/10"),
                (50, "LER 17 05 04 · Tierras", "10/10"), (49, "LER 17 02 01 · Madera", "09/10"), (48, "LER 17 04 05 · Hierro", "08/10"),
                (47, "LER 17 01 07 · Hormigón", "07/10")]]
    for i, (a, b, c) in enumerate(rows):
        y = 250 + i * 170
        d.rounded_rectangle((32, y, SW - 32, y + 150), radius=26, fill=CARD)
        d.text((64, y + 26), a, font=font("Bold", 36), fill=ORANGE)
        d.text((64, y + 80), b, font=font("Medium", 30), fill=INK)
        f = font("SemiBold", 28); d.text((SW - 64 - f.getlength(c), y + 30), c, font=f, fill=(110, 122, 142))
    return im

def scr_dei_form():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Nuevo DeI de residuos", SW)
    d.rounded_rectangle((32, 250, SW - 32, 1250), radius=30, fill=CARD)
    field(d, 64, 280, SW - 128, "Productor (cliente)", "Construcciones Ejemplo S.L.")
    field(d, 64, 440, SW - 128, "Obra", "C/ Mayor 21, Alcorcón")
    field(d, 64, 600, SW - 128, "Gestor / vertedero", "Planta RCD Sur · Pinto")
    field(d, 64, 760, SW - 128, "Código LER", "17 01 07 · Mezcla de hormigón")
    field(d, 64, 920, (SW - 160) // 2, "Cantidad (t)", "12,5")
    field(d, 96 + (SW - 160) // 2, 920, (SW - 160) // 2, "Matrícula", "1234-ABC")
    d.rounded_rectangle((64, 1120, SW - 64, 1215), radius=24, fill=ORANGE)
    t = "Generar DeI"; f = font("Bold", 38)
    d.text(((SW - f.getlength(t)) / 2, 1142), t, font=f, fill=WHITE)
    return im

def scr_dei_pdf():
    im = Image.new("RGBA", (SW, SH), (90, 98, 112)); d = ImageDraw.Draw(im)
    d.rectangle((40, 60, SW - 40, SH - 40), fill=WHITE)
    d.text((80, 100), "DOCUMENTO DE IDENTIFICACIÓN", font=font("Black", 34), fill=INK)
    d.text((80, 148), "Traslado de RCD · RD 553/2020", font=font("Medium", 26), fill=(100, 110, 130))
    d.text((80, 192), "Nº DeI-0052", font=font("Bold", 30), fill=ORANGE)
    y = 270
    for lab, val in [("Productor", "Construcciones Ejemplo S.L."), ("Origen", "Obra C/ Mayor 21, Alcorcón"),
                     ("Destino", "Planta RCD Sur · Pinto"), ("Residuo", "LER 17 01 07 · 12,5 t"),
                     ("Transportista", "Contenedores Ejemplo · 1234-ABC"), ("Fecha", "12/10/2026")]:
        d.line((80, y, SW - 80, y), fill=LINE, width=2)
        d.text((80, y + 22), lab, font=font("SemiBold", 26), fill=(110, 122, 142))
        d.text((80, y + 60), val, font=font("Medium", 32), fill=INK)
        y += 130
    q = qr_img(230); im.alpha_composite(q, ((SW - 230) // 2, 1040))
    t = "Verificar con QR"; f = font("SemiBold", 26)
    d.text(((SW - f.getlength(t)) / 2, 1278), t, font=f, fill=(110, 122, 142))
    return im

def scr_fich_movil():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Portal del empleado", SW)
    d.rounded_rectangle((32, 250, SW - 32, 1250), radius=30, fill=CARD)
    for t, f, c, y in [("Hola, Marta", font("Bold", 44), INK, 300), ("Martes, 21 de octubre", font("Medium", 30), (110, 122, 142), 362),
                       ("08:02", font("Black", 150), INK, 440)]:
        d.text(((SW - f.getlength(t)) / 2, y), t, font=f, fill=c)
    cx = SW // 2
    d.ellipse((cx - 170, 660, cx + 170, 1000), fill=GREEN)
    for t, f, y in [("FICHAR", font("Black", 58), 770), ("ENTRADA", font("Bold", 34), 845)]:
        d.text(((SW - f.getlength(t)) / 2, y), t, font=f, fill=WHITE)
    for i, (a, b) in enumerate([("Hoy", "0 h 00 min"), ("Esta semana", "31 h 40 min")]):
        y = 1060 + i * 70
        d.text((80, y), a, font=font("Medium", 32), fill=(110, 122, 142))
        f = font("Bold", 32); d.text((SW - 80 - f.getlength(b), y), b, font=f, fill=INK)
    return im

def scr_fich_panel():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Fichajes de hoy", SW)
    rows = [("Marta G.", "08:02 → 16:05", "8 h 03", GREEN), ("Javier R.", "07:58 → 15:30", "7 h 32", GREEN),
            ("Lucía P.", "09:00 → en curso", "4 h 10", ORANGE), ("Andrés M.", "08:15 → 14:00", "5 h 45", GREEN),
            ("Sara L.", "Vacaciones", "—", (110, 122, 142)), ("Iván T.", "07:45 → 15:50", "8 h 05", GREEN)]
    for i, (a, b, c, col) in enumerate(rows):
        y = 250 + i * 170
        d.rounded_rectangle((32, y, SW - 32, y + 150), radius=26, fill=CARD)
        d.ellipse((60, y + 45, 120, y + 105), fill=col)
        d.text((150, y + 26), a, font=font("Bold", 36), fill=INK)
        d.text((150, y + 82), b, font=font("Medium", 28), fill=(110, 122, 142))
        f = font("Bold", 34); d.text((SW - 64 - f.getlength(c), y + 54), c, font=f, fill=INK)
    return im

def scr_fich_informe():
    im = Image.new("RGBA", (SW, SH), (90, 98, 112)); d = ImageDraw.Draw(im)
    d.rectangle((40, 60, SW - 40, SH - 40), fill=WHITE)
    d.text((80, 100), "REGISTRO DE JORNADA", font=font("Black", 40), fill=INK)
    d.text((80, 152), "Octubre 2026 · Marta García", font=font("Medium", 28), fill=(100, 110, 130))
    y = 240
    for dia, e, s_, h in [("01/10", "08:01", "16:03", "8:02"), ("02/10", "07:59", "16:00", "8:01"), ("03/10", "08:05", "15:02", "6:57"),
                          ("06/10", "08:00", "16:10", "8:10"), ("07/10", "08:02", "16:01", "7:59"), ("08/10", "07:57", "16:00", "8:03"),
                          ("09/10", "08:03", "16:04", "8:01"), ("10/10", "08:00", "14:00", "6:00")]:
        d.line((80, y, SW - 80, y), fill=LINE, width=2)
        for x, t in [(80, dia), (250, e), (420, s_), (590, h)]:
            d.text((x, y + 24), t, font=font("Medium", 32), fill=INK)
        y += 100
    d.rounded_rectangle((80, 1080, SW - 80, 1180), radius=22, fill=(225, 246, 234))
    t = "Listo para la inspección"; f = font("Bold", 34)
    d.text(((SW - f.getlength(t)) / 2, 1110), t, font=f, fill=GREEN)
    return im

def lock_icon(d, x, y, s, col):
    d.rounded_rectangle((x, y + s * 0.45, x + s, y + s), radius=int(s * 0.12), fill=col)
    d.arc((x + s * 0.2, y, x + s * 0.8, y + s * 0.8), 180, 360, fill=col, width=max(4, int(s * 0.12)))

def scr_bov_lista():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Gestor de Contraseñas", SW)
    rows = [("Banco · Empresa", "administracion@"), ("Agencia Tributaria", "certificado digital"), ("Correo corporativo", "info@"),
            ("Proveedor de luz", "contratos@"), ("Redes sociales", "@miempresa"), ("Wifi oficina", "OFICINA_5G")]
    for i, (a, b) in enumerate(rows):
        y = 250 + i * 170
        d.rounded_rectangle((32, y, SW - 32, y + 150), radius=26, fill=CARD)
        lock_icon(d, 64, y + 45, 56, ORANGE)
        d.text((150, y + 26), a, font=font("Bold", 36), fill=INK)
        d.text((150, y + 82), b + "  ·  ••••••••••", font=font("Medium", 28), fill=(110, 122, 142))
    return im

def scr_bov_detalle():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Banco · Empresa", SW)
    d.rounded_rectangle((32, 250, SW - 32, 1250), radius=30, fill=CARD)
    field(d, 64, 290, SW - 128, "Usuario", "administracion@miempresa.es")
    field(d, 64, 450, SW - 128, "Contraseña", "••••••••••••••")
    field(d, 64, 610, SW - 128, "Web", "banca.ejemplo.es")
    d.rounded_rectangle((64, 800, SW - 64, 895), radius=24, fill=ORANGE)
    t = "Copiar contraseña"; f = font("Bold", 38)
    d.text(((SW - f.getlength(t)) / 2, 822), t, font=f, fill=WHITE)
    d.rounded_rectangle((64, 930, SW - 64, 1025), radius=24, outline=ORANGE, width=4)
    t = "Compartir de forma segura"; f = font("Bold", 34)
    d.text(((SW - f.getlength(t)) / 2, 956), t, font=f, fill=ORANGE)
    lock_icon(d, SW // 2 - 30, 1080, 60, GREEN)
    t = "Cifrado de extremo a extremo"; f = font("SemiBold", 28)
    d.text(((SW - f.getlength(t)) / 2, 1160), t, font=f, fill=GREEN)
    return im

def scr_bov_maestra():
    im = Image.new("RGBA", (SW, SH), (16, 30, 56)); d = ImageDraw.Draw(im)
    lock_icon(d, SW // 2 - 90, 330, 180, ORANGE)
    for t, f, c, y in [("Tu bóveda", font("Black", 64), WHITE, 590), ("Solo tú tienes la llave", font("Medium", 34), MUTED, 680)]:
        d.text(((SW - f.getlength(t)) / 2, y), t, font=f, fill=c)
    d.rounded_rectangle((64, 800, SW - 64, 900), radius=22, fill=(255, 255, 255, 30), outline=(255, 255, 255, 80), width=3)
    d.text((100, 828), "Contraseña maestra  ••••••••", font=font("Medium", 34), fill=WHITE)
    d.rounded_rectangle((64, 940, SW - 64, 1040), radius=24, fill=ORANGE)
    t = "Desbloquear"; f = font("Bold", 38)
    d.text(((SW - f.getlength(t)) / 2, 966), t, font=f, fill=WHITE)
    return im

def scr_sop_tickets():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Incidencias", SW)
    rows = [("El correo no envía", "Resuelta en 25 min", GREEN), ("Impresora de recepción", "Resuelta en 40 min", GREEN),
            ("Equipo nuevo", "Instalado y configurado", GREEN), ("Wifi lento en oficina", "En curso", ORANGE),
            ("Accesos de un empleado", "Revocados", GREEN), ("Actualizaciones", "Al día", GREEN)]
    for i, (a, b, col) in enumerate(rows):
        y = 250 + i * 170
        d.rounded_rectangle((32, y, SW - 32, y + 150), radius=26, fill=CARD)
        d.ellipse((60, y + 45, 120, y + 105), fill=col)
        d.text((150, y + 26), a, font=font("Bold", 36), fill=INK)
        d.text((150, y + 82), b, font=font("Medium", 28), fill=(110, 122, 142))
    return im

def scr_sop_seguridad():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Revisión de seguridad", SW)
    d.rounded_rectangle((32, 250, SW - 32, 1250), radius=30, fill=CARD)
    cx = SW // 2
    d.ellipse((cx - 110, 290, cx + 110, 510), fill=(225, 246, 234))
    d.line([(cx - 52, 402), (cx - 12, 442), (cx + 60, 360)], fill=GREEN, width=22, joint="curve")
    for i, t in enumerate(["Antivirus y cortafuegos", "Equipos actualizados", "Accesos y contraseñas", "Red wifi protegida", "Protección ransomware"]):
        y = 580 + i * 120
        d.line((80, y - 14, SW - 80, y - 14), fill=LINE, width=2)
        d.text((80, y + 14), t, font=font("Medium", 34), fill=INK)
        f = font("Bold", 34); d.text((SW - 80 - f.getlength("OK"), y + 14), "OK", font=f, fill=GREEN)
    return im

def scr_suite():
    im = Image.new("RGBA", (SW, SH), (238, 242, 248)); d = ImageDraw.Draw(im)
    appbar(d, "Inicio", SW)
    tiles = [("Residuos (DeI)", "12 este mes", (34, 170, 96)), ("Cartas de Porte", "48 este mes", (60, 120, 255)),
             ("Fichajes", "6 empleados", (255, 122, 26)), ("Contraseñas", "24 guardadas", (150, 90, 220))]
    for i, (a, b, col) in enumerate(tiles):
        x = 32 + (i % 2) * ((SW - 96) // 2 + 32); y = 260 + (i // 2) * 330; w = (SW - 96) // 2
        d.rounded_rectangle((x, y, x + w, y + 300), radius=30, fill=CARD)
        d.ellipse((x + 30, y + 30, x + 120, y + 120), fill=col)
        d.text((x + 30, y + 160), a, font=font("Bold", 32), fill=INK)
        d.text((x + 30, y + 214), b, font=font("Medium", 26), fill=(110, 122, 142))
    d.rounded_rectangle((32, 940, SW - 32, 1250), radius=30, fill=CARD)
    d.text((64, 975), "Hoy", font=font("Bold", 36), fill=INK)
    for i, t in enumerate(["CP-000148 generada · Getafe → Valencia", "DeI-0052 firmado · Obra Alcorcón", "Marta fichó la entrada · 08:02"]):
        d.text((64, 1040 + i * 64), "•  " + t, font=font("Medium", 27), fill=INK)
    return im

SCREENS = {"deca_formulario": scr_form, "deca_documento": scr_pdf, "verificacion_qr": scr_verif,
           "deca_lista": lambda: scr_list("deca"), "dei_lista": lambda: scr_list("dei"),
           "dei_formulario": scr_dei_form, "dei_documento": scr_dei_pdf,
           "fichajes_movil": scr_fich_movil, "fichajes_panel": scr_fich_panel, "fichajes_informe": scr_fich_informe,
           "boveda_lista": scr_bov_lista, "boveda_detalle": scr_bov_detalle, "boveda_maestra": scr_bov_maestra,
           "soporte_incidencias": scr_sop_tickets, "soporte_seguridad": scr_sop_seguridad,
           "suite_inicio": scr_suite}

# ---------- escenas ----------
def centered(im, y): return (W - im.width) // 2, y
scenes = []
def add(dur, els): scenes.append((dur, els))

def build(spec):
    for sc in spec["escenas"]:
        tp = sc["tipo"]
        if tp == "portada":
            els, y0 = [], 560
            if sc.get("etiqueta"):
                tag = pill(sc["etiqueta"].upper(), font("Bold", 38), WHITE, ORANGE); els.append((tag, *centered(tag, y0), 0.05, "up"))
            t1 = rich(sc["titulo"], font("Black", 108), 940); els.append((t1, *centered(t1, y0 + 140), 0.25, "up"))
            if sc.get("texto"):
                s1 = rich(sc["texto"], font("SemiBold", 52), 900, color=MUTED); els.append((s1, *centered(s1, y0 + 200 + t1.height), 0.8, "up"))
            add(sc.get("duracion", 3.6), els)
        elif tp == "pantalla":
            tt = rich(sc["titulo"], font("Black", 78), 960)
            els = [(tt, *centered(tt, 150), 0.0, "up")]
            if sc.get("texto"):
                st = rich(sc["texto"], font("SemiBold", 42), 940, color=MUTED); els.append((st, *centered(st, 170 + tt.height), 0.2, "up"))
            ph = phone(SCREENS[sc["captura"]]()); ph = ph.resize((int(ph.width * 0.86), int(ph.height * 0.86)), Image.LANCZOS)
            els.append((ph, (W - ph.width) // 2, 420, 0.15, "rise"))
            add(sc.get("duracion", 3.9), els)
        elif tp == "lista":
            lt = rich(sc["titulo"], font("Black", 92), 960)
            els = [(lt, *centered(lt, 360), 0.0, "up")]
            for i, p in enumerate(sc["puntos"][:4]):
                row = Image.new("RGBA", (900, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(row)
                d.rounded_rectangle((0, 0, 899, 149), radius=40, fill=(255, 255, 255, 22), outline=(255, 255, 255, 40), width=2)
                d.ellipse((34, 35, 114, 115), fill=ORANGE)
                d.line([(55, 76), (69, 92), (95, 60)], fill=WHITE, width=10, joint="curve")
                fs = 50
                while fs > 30 and font("Bold", fs).getlength(p) > 720: fs -= 2
                fo = font("Bold", fs); a_, d_ = fo.getmetrics()
                d.text((150, 75 - (a_ + d_) // 2), p, font=fo, fill=WHITE)
                els.append((row, 90, 760 + i * 190, 0.35 + i * 0.35, "left"))
            add(sc.get("duracion", 4.6), els)
        elif tp == "cierre":
            c1 = rich(sc.get("titulo", "*15 días gratis*"), font("Black", 130), 980)
            c2 = rich(sc.get("texto", "Sin tarjeta. Sin permanencia."), font("SemiBold", 54), 940)
            els = [(c1, *centered(c1, 520), 0.0, "pop"), (c2, *centered(c2, 720), 0.3, "up")]
            if sc.get("precio"):
                c3 = pill(sc["precio"], font("Bold", 44), INK, WHITE, padx=44, pady=22); els.append((c3, *centered(c3, 880), 0.6, "up"))
            web = sc.get("web", "mitalonario.es")
            if web:
                c4 = rich(web, font("Black", 96 if len(web) < 16 else 64), 980, color=ORANGE); els.append((c4, *centered(c4, 1120), 0.9, "pop"))
            for j, linea in enumerate([x.strip() for x in sc.get("contacto", "").split("·") if x.strip()]):
                c5 = rich(linea, font("SemiBold", 46), 980, color=WHITE); els.append((c5, *centered(c5, 1290 + j * 80), 1.2 + j * 0.2, "up"))
            add(sc.get("duracion", 4.4), els)

import json
SPEC = json.load(open(sys.argv[2]))
build(SPEC)
TOTAL = sum(d for d, _ in scenes)

# ---------- render ----------
def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

brand = rich("*Talonario*  ·  mitalonario.es", font("Bold", 34), 700, color=MUTED)

def frame(t):
    acc = 0.0
    for idx, (dur, els) in enumerate(scenes):
        if t < acc + dur or idx == len(scenes) - 1:
            lt_ = t - acc; break
        acc += dur
    img = BG.copy()
    fade_out = 1.0 if idx == len(scenes) - 1 else ease((dur - lt_) / 0.25)
    for im, x, y, st, kind in els:
        p = ease((lt_ - st) / 0.45)
        if p <= 0: continue
        a = p * fade_out
        dx = dy = 0; el = im
        if kind == "up": dy = int((1 - p) * 70)
        elif kind == "rise": dy = int((1 - p) * 260) - int(lt_ * 12)
        elif kind == "left": dx = int((1 - p) * -160)
        elif kind == "pop":
            s = 0.85 + 0.15 * p + 0.02 * math.sin(lt_ * 3)
            el = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
            dx, dy = (im.width - el.width) // 2, (im.height - el.height) // 2
        if a < 1:
            el = el.copy(); al = el.split()[3].point(lambda v, a=a: int(v * a)); el.putalpha(al)
        img.alpha_composite(el, (x + dx, y + dy))
    # barra de progreso + marca
    img.alpha_composite(brand, ((W - brand.width) // 2, H - 150))
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 12, int(W * t / TOTAL), H), fill=ORANGE)
    return img.convert("RGB")

# ---------- música (sintetizada, libre de derechos) ----------
def music(path, secs, sr=44100, bpm=124):
    n = int(secs * sr); t = np.arange(n) / sr; out = np.zeros(n)
    beat = 60 / bpm
    def env(length, decay): x = np.arange(int(length * sr)) / sr; return np.exp(-x * decay)
    def place(sig, start):
        i = int(start * sr); j = min(n, i + len(sig))
        if i < n: out[i:j] += sig[: j - i]
    kl = 0.35; kx = np.arange(int(kl * sr)) / sr
    kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-kx * 30)) * kx) * np.exp(-kx * 9)
    hat = np.random.default_rng(1).standard_normal(int(0.05 * sr)) * env(0.05, 90) * 0.25
    hat = np.diff(hat, prepend=0)
    clap = np.random.default_rng(2).standard_normal(int(0.15 * sr)) * env(0.15, 28) * 0.35
    prog = [(45, 57, 60, 64), (41, 53, 57, 60), (36, 48, 52, 55), (43, 55, 59, 62)]  # Am F C G
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    b = 0; tt = 0.0
    while tt < secs:
        place(kick * 0.9, tt)
        place(hat, tt + beat / 2)
        if b % 2 == 1: place(clap, tt)
        bar = (b // 4) % 4; root, *ch = prog[bar]
        bx = np.arange(int(beat * sr)) / sr
        bass = np.sign(np.sin(2 * np.pi * f(root) * bx)) * 0.12 * np.exp(-bx * 4)
        place(bass, tt + beat / 2 * 0)
        if b % 4 == 0:
            px = np.arange(int(beat * 4 * sr)) / sr
            pad = sum(np.sin(2 * np.pi * f(m) * px) + 0.4 * np.sin(2 * np.pi * f(m) * 2 * px) for m in ch)
            pad *= 0.045 * np.minimum(1, px * 8) * np.exp(-px * 0.6)
            place(pad, tt)
        # arpegio
        for k in range(2):
            ax = np.arange(int(beat / 2 * sr)) / sr
            m = ch[(b * 2 + k) % 3] + 12
            place(np.sin(2 * np.pi * f(m) * ax) * np.exp(-ax * 14) * 0.08, tt + k * beat / 2)
        b += 1; tt += beat
    fade = np.minimum(1, np.minimum(t / 0.3, (secs - t) / 1.2))
    out = np.tanh(out * 1.4) * fade * 0.8
    st = np.stack([out, out], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((st * 32767).astype("<i2").tobytes())

if __name__ == "__main__":
    music("music.wav", TOTAL, bpm={"energica": 124, "optimista": 112, "corporativa": 100}.get(SPEC.get("musica"), 124))
    if "--preview" in sys.argv:
        acc = 0
        for i, (d_, _) in enumerate(scenes):
            frame(acc + min(d_ - 0.3, 2.2)).resize((360, 640)).save(f"prev_{i}.png"); acc += d_
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "music.wav",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE)
    for i in range(int(TOTAL * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("OK", OUT, round(TOTAL, 1), "s")
