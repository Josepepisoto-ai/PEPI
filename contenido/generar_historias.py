"""Genera las 75 historias (1080x1920) de historias-instagram-15-dias.md con la marca JS Personal Trainer (negro, bronce y plata).

Uso: python3 contenido/generar_historias.py
Salida: contenido/historias/dia-XX/NN.png y una hoja de contacto por día.
"""
import re
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# Colores del logo oficial JS Personal Trainer.
FONDO = (1, 1, 1)             # negro del logo
FONDO_CENTRO = (24, 19, 15)   # brillo cálido muy suave en el centro
ORO_CLARO = (218, 172, 120)   # bronce claro (brillos del cerebro)
ORO_OSCURO = (150, 100, 60)   # bronce oscuro (sombras)
ORO = (192, 144, 96)          # bronce medio
PLATA = (224, 224, 224)       # letras JS
CREMA = (240, 240, 240)       # texto principal
GRIS = (110, 104, 98)         # detalles secundarios

W, H = 1080, 1920
MARGEN = 96
FUENTE = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FUENTE_CHICA = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"

AQUI = Path(__file__).parent
FUENTE_MD = AQUI / "historias-instagram-15-dias.md"
SALIDA = AQUI / "historias"
LOGO = AQUI / "marca" / "logo-js.png"

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


def estilo(formato):
    f = formato.lower()
    if f.startswith("foto"):
        return "foto"
    if any(k in f for k in ("encuesta", "quiz", "slider", "caja", "dm")):
        return "interactiva"
    if "video" in f:
        return "dorado"
    return "texto"


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


def gradiente_oro(alto):
    """Banda vertical de bronce claro a bronce oscuro, como el cerebro del logo."""
    g = Image.new("RGB", (1, alto))
    for y in range(alto):
        t = y / max(alto - 1, 1)
        g.putpixel((0, y), tuple(int(ORO_CLARO[i] + (ORO_OSCURO[i] - ORO_CLARO[i]) * t) for i in range(3)))
    return g


def escribir(img, palabras, caja, todo_oro=False, alinear_arriba=False, maximo=104):
    """Texto blanco; las frases ancla (o todo, si todo_oro) van en bronce degradado."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = caja
    fuente, lineas, interlinea = ajustar(d, palabras, x1 - x0, y1 - y0, maximo=maximo)
    alto_total = len(lineas) * interlinea
    y = y0 if alinear_arriba else y0 + (y1 - y0 - alto_total) // 2
    espacio = d.textlength(" ", font=fuente)
    mascara = Image.new("L", img.size, 0)
    dm = ImageDraw.Draw(mascara)
    oro = Image.new("RGB", img.size, ORO)
    banda = gradiente_oro(interlinea).resize((img.size[0], interlinea))
    for linea in lineas:
        x = x0
        oro.paste(banda, (0, y))
        for palabra, res in linea:
            if res or todo_oro:
                dm.text((x, y), palabra, font=fuente, fill=255)
            else:
                d.text((x, y), palabra, font=fuente, fill=CREMA)
            x += d.textlength(palabra, font=fuente) + espacio
        y += interlinea
    img.paste(oro, (0, 0), mascara)


def fondo():
    """Negro del logo con un brillo cálido muy suave en el centro."""
    chico = Image.new("RGB", (108, 192), FONDO)
    for y in range(192):
        for x in range(108):
            dx, dy = (x - 54) / 54, (y - 80) / 110
            t = max(0.0, 1 - (dx * dx + dy * dy) ** 0.5)
            chico.putpixel((x, y), tuple(int(FONDO[i] + (FONDO_CENTRO[i] - FONDO[i]) * t) for i in range(3)))
    return chico.resize((W, H), Image.BICUBIC)


def logo(ancho):
    im = Image.open(LOGO).convert("RGB")
    im = im.resize((ancho, int(im.height * ancho / im.width)), Image.LANCZOS)
    # Bordes difuminados para que el fondo del logo se funda con el de la historia.
    mascara = Image.new("L", im.size, 0)
    m = ancho // 14
    ImageDraw.Draw(mascara).ellipse((m, m, im.width - m, im.height - m), fill=255)
    return im, mascara.filter(ImageFilter.GaussianBlur(ancho // 16))


def pegar_logo(img, ancho, centro_y=None, y=None):
    """El logo tiene fondo negro: se combina con "lighter" para que el negro desaparezca."""
    im, _ = logo(ancho)
    x = (W - im.width) // 2
    y = centro_y - im.height // 2 if centro_y is not None else y
    zona = img.crop((x, y, x + im.width, y + im.height))
    img.paste(ImageChops.lighter(zona, im), (x, y))
    return y + im.height


def marco(img, numero, mostrar_logo=True, ancho_logo=250):
    d = ImageDraw.Draw(img)
    d.rectangle((36, 36, W - 37, H - 37), outline=(44, 34, 26), width=2)
    f = ImageFont.truetype(FUENTE_CHICA, 30)
    d.text((W - MARGEN, H - 150), f"{numero} / 5", font=f, fill=GRIS, anchor="ra")
    d.text((MARGEN, H - 150), "P F   J O S E   P E P I   S O T O", font=f, fill=ORO)
    if mostrar_logo:
        return pegar_logo(img, ancho_logo, y=100)
    return 110


def render(story, numero):
    tipo = estilo(story["formato"])
    texto = story["texto"]
    img = fondo()

    if tipo == "texto":
        tope = marco(img, numero)
        escribir(img, segmentos(texto), (MARGEN, tope + 120, W - MARGEN, H - 260))
    elif tipo == "dorado":
        # Guion de video a cámara: todo en bronce. Se puede publicar así o grabar encima.
        tope = marco(img, numero)
        escribir(img, segmentos(texto), (MARGEN, tope + 120, W - MARGEN, H - 260), todo_oro=True)
    elif tipo == "foto":
        # Mitad de arriba libre para una foto propia; texto abajo.
        marco(img, numero, mostrar_logo=False)
        d = ImageDraw.Draw(img)
        d.rectangle((MARGEN, 200, W - MARGEN, 1080), outline=ORO_OSCURO, width=3)
        pegar_logo(img, 300, centro_y=640)
        d.line((MARGEN, 1170, MARGEN + 120, 1170), fill=ORO, width=6)
        escribir(img, segmentos(texto), (MARGEN, 1220, W - MARGEN, H - 240), maximo=88)
    else:  # interactiva: pregunta arriba, lugar libre abajo para el sticker
        tope = marco(img, numero, ancho_logo=190)
        pregunta = texto.split("→")[0].strip()
        d = ImageDraw.Draw(img)
        d.line((MARGEN, tope + 90, MARGEN + 120, tope + 90), fill=PLATA, width=6)
        escribir(img, segmentos(pregunta), (MARGEN, tope + 140, W - MARGEN, tope + 760), alinear_arriba=True, maximo=96)
    return img


def hoja_contacto(imagenes, titulo, destino):
    escala = 0.2
    w, h = int(W * escala), int(H * escala)
    sep = 20
    hoja = Image.new("RGB", (5 * w + 6 * sep, h + 2 * sep + 60), FONDO)
    d = ImageDraw.Draw(hoja)
    d.text((sep, 18), titulo, font=ImageFont.truetype(FUENTE_CHICA, 30), fill=ORO)
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
