"""Genera las 75 historias (1080x1920) de historias-instagram-15-dias.md con los colores del logo.

Uso: python3 contenido/generar_historias.py
Salida: contenido/historias/dia-XX/NN.png y una hoja de contacto por día.
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROJO = (214, 39, 32)       # rojo del logo
NEGRO = (17, 17, 17)
BLANCO = (245, 245, 245)
GRIS = (120, 120, 120)

W, H = 1080, 1920
MARGEN = 96
FUENTE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FUENTE_CHICA = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

AQUI = Path(__file__).parent
FUENTE_MD = AQUI / "historias-instagram-15-dias.md"
SALIDA = AQUI / "historias"

# Frases que se resaltan en el color de acento.
ANCLAS = [
    "Si no tenés un plan, no vas a lograr nada.",
    "Hacer las cosas consciente no es hacerlas con conciencia.",
    "Sé coherente con lo que hacés y con lo que decís.",
    "Si no tenés resultado, es porque no estás planificando.",
    "Salí de la caja.",
    "Esto no te va a gustar:",
    "Esto no es culpa. Es coherencia.",
    "No te voy a prometer un talle.",
    "Después de los 35 no te estás apagando.",
]


def leer_historias():
    dias, actual = [], None
    for linea in FUENTE_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"## Día (\d+) · \*\*(.+?)\*\*", linea)
        if m:
            actual = {"dia": int(m.group(1)), "titulo": m.group(2), "stories": []}
            dias.append(actual)
            continue
        m = re.match(r"(\d)\. \*\*\[(.+?)\]\*\* (.+)", linea)
        if m and actual:
            actual["stories"].append({"formato": m.group(2), "texto": m.group(3).strip()})
    return dias


def estilo(formato, i):
    f = formato.lower()
    if f.startswith("foto"):
        return "foto"
    if any(k in f for k in ("encuesta", "quiz", "slider", "caja", "dm")):
        return "interactiva"
    if "video" in f:
        return "rojo"
    if "foto" in f:
        return "foto"
    if "negro" in f or "oscuro" in f or "grande" in f:
        return "negro"
    return "negro" if i % 2 == 0 else "blanco"


def segmentos(texto):
    """Divide el texto en (fragmento, resaltado) según las frases ancla."""
    partes = [(texto, False)]
    for ancla in ANCLAS:
        nuevas = []
        for frag, res in partes:
            if res or ancla not in frag:
                nuevas.append((frag, res))
                continue
            a, b = frag.split(ancla, 1)
            if a:
                nuevas.append((a, False))
            nuevas.append((ancla, True))
            if b:
                nuevas.append((b, False))
        partes = nuevas
    palabras = []
    for frag, res in partes:
        palabras += [(p, res) for p in frag.split()]
    return palabras


def envolver(draw, palabras, fuente, ancho):
    lineas, linea = [], []
    for p in palabras:
        prueba = " ".join(w for w, _ in linea + [p])
        if linea and draw.textlength(prueba, font=fuente) > ancho:
            lineas.append(linea)
            linea = [p]
        else:
            linea.append(p)
    if linea:
        lineas.append(linea)
    return lineas


def ajustar(draw, palabras, ancho, alto, maximo=104, minimo=52):
    for tam in range(maximo, minimo - 1, -4):
        fuente = ImageFont.truetype(FUENTE, tam)
        lineas = envolver(draw, palabras, fuente, ancho)
        interlinea = int(tam * 1.18)
        if len(lineas) * interlinea <= alto:
            return fuente, lineas, interlinea
    return fuente, lineas, interlinea


def escribir(draw, palabras, caja, base, acento, alinear_arriba=False):
    x0, y0, x1, y1 = caja
    fuente, lineas, interlinea = ajustar(draw, palabras, x1 - x0, y1 - y0)
    alto_total = len(lineas) * interlinea
    y = y0 if alinear_arriba else y0 + (y1 - y0 - alto_total) // 2
    espacio = draw.textlength(" ", font=fuente)
    for linea in lineas:
        x = x0
        for palabra, res in linea:
            draw.text((x, y), palabra, font=fuente, fill=acento if res else base)
            x += draw.textlength(palabra, font=fuente) + espacio
        y += interlinea


def curva(draw, color, caja, ancho=46, arriba=False):
    """Arco inspirado en la curva del logo."""
    inicio, fin = (30, 150) if arriba else (200, 330)
    draw.arc(caja, start=inicio, end=fin, fill=color, width=ancho)


def marca(draw, color, numero):
    f = ImageFont.truetype(FUENTE_CHICA, 34)
    draw.rectangle((MARGEN, 150, MARGEN + 90, 160), fill=color)
    draw.text((W - MARGEN, 136), f"{numero}/5", font=f, fill=color, anchor="ra")
    draw.text((MARGEN, H - 150), "PEPI SOTO", font=f, fill=color)


def render(story, numero):
    tipo = estilo(story["formato"], numero - 1)
    texto = story["texto"]
    img = Image.new("RGB", (W, H), NEGRO)
    d = ImageDraw.Draw(img)
    caja = (MARGEN, 300, W - MARGEN, H - 300)

    if tipo == "negro":
        curva(d, ROJO, (380, -560, 1460, 520), arriba=True)
        marca(d, GRIS, numero)
        escribir(d, segmentos(texto), caja, BLANCO, ROJO)
    elif tipo == "blanco":
        d.rectangle((0, 0, W, H), fill=BLANCO)
        curva(d, ROJO, (-500, 1400, 640, 2500))
        marca(d, GRIS, numero)
        escribir(d, segmentos(texto), caja, NEGRO, ROJO)
    elif tipo == "rojo":
        d.rectangle((0, 0, W, H), fill=ROJO)
        curva(d, NEGRO, (380, -560, 1460, 520), arriba=True)
        marca(d, BLANCO, numero)
        palabras = segmentos(texto)
        escribir(d, palabras, caja, BLANCO, NEGRO)
    elif tipo == "foto":
        # Fondo para reemplazar por una foto propia: bloque rojo diagonal + texto.
        d.polygon([(0, 1150), (W, 900), (W, H), (0, H)], fill=ROJO)
        curva(d, ROJO, (380, -560, 1460, 520), arriba=True)
        marca(d, BLANCO, numero)
        escribir(d, segmentos(texto), (MARGEN, 1160, W - MARGEN, H - 230), BLANCO, NEGRO)
    else:  # interactiva: pregunta arriba, lugar libre abajo para el sticker
        d.rectangle((0, 0, W, H), fill=BLANCO)
        d.rectangle((0, 0, W, 24), fill=ROJO)
        marca(d, GRIS, numero)
        pregunta = texto.split("→")[0].strip()
        escribir(d, segmentos(pregunta), (MARGEN, 300, W - MARGEN, 900), NEGRO, ROJO, alinear_arriba=True)
        curva(d, ROJO, (-500, 1400, 640, 2500))
    return img


def hoja_contacto(imagenes, titulo, destino):
    escala = 0.2
    w, h = int(W * escala), int(H * escala)
    sep = 20
    hoja = Image.new("RGB", (5 * w + 6 * sep, h + 2 * sep + 60), NEGRO)
    d = ImageDraw.Draw(hoja)
    d.text((sep, 18), titulo, font=ImageFont.truetype(FUENTE_CHICA, 30), fill=BLANCO)
    for i, im in enumerate(imagenes):
        hoja.paste(im.resize((w, h)), (sep + i * (w + sep), 60 + sep))
    hoja.save(destino)


def main():
    dias = leer_historias()
    assert len(dias) == 15 and all(len(x["stories"]) == 5 for x in dias), "se esperaban 15 días x 5 stories"
    for dia in dias:
        carpeta = SALIDA / f"dia-{dia['dia']:02d}"
        carpeta.mkdir(parents=True, exist_ok=True)
        imagenes = []
        for n, story in enumerate(dia["stories"], 1):
            im = render(story, n)
            im.save(carpeta / f"{n:02d}.png", optimize=True)
            imagenes.append(im)
        hoja_contacto(imagenes, f"Día {dia['dia']} · {dia['titulo']}", SALIDA / f"resumen-dia-{dia['dia']:02d}.png")
    print(f"{sum(len(x['stories']) for x in dias)} historias en {SALIDA}")


if __name__ == "__main__":
    main()
