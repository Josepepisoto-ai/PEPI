#!/usr/bin/env python3
"""Herramientas para preparar y publicar contenido en Instagram.

Subcomandos:

  check-video  Verifica que un video cumpla los requisitos de Reels.
  caption      Valida un texto de publicación (largo, hashtags, menciones).
  carousel     Genera las imágenes 1080x1350 de un carrusel a partir de un JSON.
  whoami       Comprueba el token y muestra la cuenta conectada.
  publish      Publica un Reel, una imagen o un carrusel.
  schedule     Agrega una publicación a la cola para una fecha y hora.
  queue        Muestra la cola de publicaciones programadas.
  publish-due  Publica lo que esté vencido en la cola (para correr con cron).
  comments     Lista comentarios recientes que todavía no tienen respuesta.
  reply        Responde un comentario.
  private-reply  Manda un DM a quien comentó (entrega por palabra clave).
  outliers     Rankea publicaciones por múltiplo sobre la mediana de cada cuenta.
  discover     Baja publicaciones de cuentas del nicho (Business Discovery).
  audit        Métricas de tus publicaciones: múltiplo de alcance y envíos por alcance.
  profile      Muestra los datos de tu perfil.

Requisitos: ffprobe (check-video), Pillow (carousel) y, para la API, las variables
IG_ACCESS_TOKEN e IG_USER_ID (token de "Instagram API with Instagram Login").
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_HOST = os.environ.get("IG_API_HOST", "https://graph.instagram.com")
API_VERSION = os.environ.get("IG_API_VERSION", "v23.0")
CONFIG_DIR = Path.home() / ".config" / "instagram-skill"
QUEUE_FILE = CONFIG_DIR / "queue.json"
CACHE_DIR = Path.home() / ".cache" / "instagram"

CAPTION_MAX = 2200
HASHTAG_MAX = 5          # límite actual de Instagram por publicación
MENTION_MAX = 20
CAROUSEL_MAX = 10        # máximo de elementos por carrusel en la API
SLIDE_W, SLIDE_H = 1080, 1350
SAFE_TOP, SAFE_BOTTOM = 96, 96   # historias: la interfaz tapa ~250 px arriba y ~340 abajo


# ---------------------------------------------------------------- utilidades

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def warn(msg):
    print(f"AVISO: {msg}", file=sys.stderr)


def read_text(path):
    p = Path(path).expanduser()
    if not p.exists():
        die(f"no existe {p}")
    return p.read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------- check-video

def probe(path):
    if not shutil.which("ffprobe"):
        die("no encuentro ffprobe. Instálalo (macOS: `brew install ffmpeg`).")
    res = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
                          "-show_format", str(path)], text=True, capture_output=True)
    if res.returncode != 0:
        die(f"ffprobe no pudo leer {path}: {res.stderr.strip()[-500:]}")
    return json.loads(res.stdout)


def cmd_check_video(args):
    path = Path(args.video).expanduser()
    info = probe(path)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if video is None:
        die("el archivo no tiene pista de video")
    w, h = int(video["width"]), int(video["height"])
    num, den = (video.get("avg_frame_rate") or "0/1").split("/")
    fps = float(num) / float(den) if float(den) else 0
    duration = float(info["format"].get("duration") or 0)
    size_mb = path.stat().st_size / 1e6

    problems = []
    if abs(w / h - 9 / 16) > 0.01:
        problems.append(f"relación {w}x{h}; Reels espera 9:16 (1080x1920)")
    if w < 720:
        problems.append(f"ancho {w}px; usar al menos 720px (ideal 1080)")
    if not 3 <= duration <= 900:
        problems.append(f"duración {duration:.1f}s; la API acepta de 3 s a 15 min")
    if video.get("codec_name") not in ("h264", "hevc"):
        problems.append(f"códec de video {video.get('codec_name')}; usar H.264")
    if not 23 <= fps <= 60:
        problems.append(f"{fps:.1f} fps; usar entre 23 y 60")
    if audio is None:
        problems.append("sin audio (se puede publicar, pero Reels rinde mejor con sonido)")
    elif audio.get("codec_name") != "aac":
        problems.append(f"audio {audio.get('codec_name')}; usar AAC")
    if size_mb > 300:
        problems.append(f"pesa {size_mb:.0f} MB; el máximo es 300 MB")

    print(f"{path.name}: {w}x{h}, {fps:.0f} fps, {duration:.1f} s, {size_mb:.1f} MB")
    if problems:
        for p in problems:
            print(f"  ✗ {p}")
        sys.exit(1)
    print("  ✓ listo para Reels")


# ---------------------------------------------------------------- caption

HASHTAG_RE = re.compile(r"(?<!\w)#(\w+)", re.UNICODE)
MENTION_RE = re.compile(r"(?<![\w.])@([\w.]+)", re.UNICODE)


def check_caption(text, max_hashtags=HASHTAG_MAX):
    problems = []
    tags = HASHTAG_RE.findall(text)
    mentions = MENTION_RE.findall(text)
    if len(text) > CAPTION_MAX:
        problems.append(f"{len(text)} caracteres; el máximo es {CAPTION_MAX}")
    if len(tags) > max_hashtags:
        problems.append(f"{len(tags)} hashtags; el máximo es {max_hashtags}")
    dup = sorted({t for t in tags if [x.lower() for x in tags].count(t.lower()) > 1})
    if dup:
        problems.append("hashtags repetidos: " + ", ".join("#" + t for t in dup))
    if len(mentions) > MENTION_MAX:
        problems.append(f"{len(mentions)} menciones; el máximo es {MENTION_MAX}")
    return {"chars": len(text), "hashtags": tags, "mentions": mentions,
            "first_line": text.splitlines()[0] if text else "", "problems": problems}


FEED_PREVIEW = 125
URL_RE = re.compile(r"https?://\S+|www\.\S+|\b\w+\.(?:com|ar|net|org|io|me|link)\b(?:/\S*)?", re.I)
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
CTA_RE = re.compile(r"\b(coment[aá]|guard[aá]|compart[ií]|mand[aá]|escrib[ií]|segu[ií]|"
                    r"contame|decime|etiquet[aá]|link en (la )?bio|respond[eé])\w*", re.I)


def feed_preview(text):
    """Lo que el feed muestra antes de "… más": hasta 2 líneas y ~125 caracteres."""
    lines = text.split("\n")
    shown = "\n".join(lines[:2])
    cut = len(shown) > FEED_PREVIEW or len(lines) > 2
    return shown[:FEED_PREVIEW].rstrip(), cut


def lint_caption(text):
    """Avisos de estilo (no bloquean la publicación)."""
    w = []
    first = text.lstrip().split("\n", 1)[0]
    if not first.strip():
        w.append("empieza con una línea vacía: el gancho tiene que ser lo primero")
    if first.startswith(("#", "@")):
        w.append("la primera línea arranca con # o @: arrancá con el gancho")
    if len(first) > FEED_PREVIEW:
        w.append(f"el gancho tiene {len(first)} caracteres y se corta en el feed (~{FEED_PREVIEW})")
    if len(first) < 15 and len(text) > 60:
        w.append("gancho muy corto: tiene que dar una razón para tocar \"más\"")
    if URL_RE.search(text):
        w.append("hay un link: en el texto no es clickeable; usá \"link en la bio\" o una palabra clave por DM")
    if not CTA_RE.search(text) and "?" not in text:
        w.append("no hay llamado a la acción (comentá, guardá, compartí, mandá…) ni pregunta")
    for i, para in enumerate(p for p in text.split("\n\n") if p.strip()):
        if len(para) > 300:
            w.append(f"el párrafo {i + 1} tiene {len(para)} caracteres: partilo")
    lines = [ln for ln in text.split("\n") if ln.strip()]
    tagged = [bool(HASHTAG_RE.search(ln)) for ln in lines]
    if any(tagged[i] and not all(tagged[i:]) for i in range(len(lines))):
        w.append("hay hashtags en el medio del texto: van todos al final")
    if text.count("—") >= 2:
        w.append(f"{text.count('—')} rayas (—): suena a IA; pasalo por /ig-human")
    if len(EMOJI_RE.findall(text)) > 6:
        w.append(f"{len(EMOJI_RE.findall(text))} emojis: con 1–3 alcanza")
    if len(re.findall(r"\b[A-ZÁÉÍÓÚÑ]{4,}\b", text)) > 3:
        w.append("muchas palabras en MAYÚSCULAS")
    return w


def cmd_caption(args):
    text = read_text(args.file)
    r = check_caption(text, args.max_hashtags)
    print(f"{r['chars']}/{CAPTION_MAX} caracteres · {len(r['hashtags'])} hashtags · "
          f"{len(r['mentions'])} menciones")
    shown, cut = feed_preview(text)
    print("\nLo que se ve en el feed antes de tocar \"más\":")
    print("┌" + "─" * 60)
    for line in shown.split("\n"):
        print("│ " + line)
    print("│ " + ("… más" if cut else "(entra completo)"))
    print("└" + "─" * 60)
    for p in r["problems"]:
        print(f"  ✗ {p}")
    for s in lint_caption(text):
        print(f"  ⚠ {s}")
    if r["problems"]:
        sys.exit(1)
    print("  ✓ se puede publicar")


# ---------------------------------------------------------------- carousel

def find_font(names, bold=True):
    if shutil.which("fc-match"):
        for name in names:
            q = f"{name}:bold" if bold else name
            res = subprocess.run(["fc-match", "-f", "%{file}\n%{family}", q],
                                 text=True, capture_output=True)
            if res.returncode == 0 and res.stdout:
                file, family = (res.stdout.split("\n") + [""])[:2]
                if name.split()[0].lower() in family.lower():
                    return file
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "C:/Windows/Fonts/arialbd.ttf"):
        if Path(p).exists():
            return p
    return None


def hex_color(value):
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def wrap(draw, text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            trial = f"{line} {word}".strip()
            if draw.textlength(trial, font=font) <= max_width or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        lines.append(line)
    return lines


def cover(img, w, h, focus=(0.5, 0.5)):
    """Recorta para llenar w x h; focus (x, y) en fracciones elige qué parte queda."""
    from PIL import Image
    scale = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = min(max(0, round(img.width * focus[0] - w / 2)), img.width - w)
    top = min(max(0, round(img.height * focus[1] - h / 2)), img.height - h)
    return img.crop((left, top, left + w, top + h))


def contain(img, w, h, top_ratio=0.5):
    """Encaja la foto entera sobre una versión desenfocada de sí misma (para fotos apaisadas)."""
    from PIL import Image, ImageEnhance, ImageFilter
    bg = cover(img, w, h).filter(ImageFilter.GaussianBlur(40))
    bg = ImageEnhance.Brightness(bg).enhance(0.55)
    scale = min(w / img.width, h / img.height)
    fg = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    bg.paste(fg, ((w - fg.width) // 2, round((h - fg.height) * top_ratio)))
    return bg


def render_slide(slide, style, index, total, base_dir):
    from PIL import Image, ImageDraw, ImageFont

    bg = hex_color(slide.get("background", style["background"]))
    fg = hex_color(slide.get("color", style["color"]))
    accent = hex_color(style["accent"])
    if accent == bg:
        accent = fg
    margin = 96

    if slide.get("image"):
        src = Path(slide["image"]).expanduser()
        if not src.is_absolute():
            src = base_dir / src
        from PIL import ImageOps
        img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        if slide.get("flip"):
            img = ImageOps.mirror(img)
        if slide.get("fit") == "contain":
            img = contain(img, SLIDE_W, SLIDE_H, slide.get("top", 0.3))
        else:
            img = cover(img, SLIDE_W, SLIDE_H, tuple(slide.get("focus", (0.5, 0.5))))
        if (slide.get("title") or slide.get("body")) and slide.get("text_pos") != "top":
            # degradé oscuro abajo para que el texto se lea sobre la foto
            shade = Image.new("L", (1, SLIDE_H))
            for y in range(SLIDE_H):
                shade.putpixel((0, y), int(200 * max(0, (y - SLIDE_H * 0.45) / (SLIDE_H * 0.55))))
            black = Image.new("RGB", (SLIDE_W, SLIDE_H), (0, 0, 0))
            img = Image.composite(black, img, shade.resize((SLIDE_W, SLIDE_H)))
            fg = (255, 255, 255)
    else:
        img = Image.new("RGB", (SLIDE_W, SLIDE_H), bg)

    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype(style["font"], slide.get("title_size", 84)) if style["font"] \
        else ImageFont.load_default()
    body_font = ImageFont.truetype(style["body_font"], slide.get("body_size", 46)) if style["body_font"] \
        else ImageFont.load_default()
    max_w = SLIDE_W - 2 * margin

    blocks = []
    if slide.get("title"):
        blocks.append((wrap(draw, slide["title"], title_font, max_w), title_font, fg, 1.15))
    if slide.get("body"):
        blocks.append((wrap(draw, slide["body"], body_font, max_w), body_font, fg, 1.35))

    def block_height(lines, font, spacing):
        return int(len(lines) * font.size * spacing)

    gap = 48
    total_h = sum(block_height(l, f, s) for l, f, _, s in blocks) + gap * max(0, len(blocks) - 1)
    if slide.get("text_pos") == "top":
        y = SAFE_TOP + 40
    elif slide.get("image"):
        y = SLIDE_H - SAFE_BOTTOM - 40 - total_h
    else:
        y = (SLIDE_H - total_h) // 2
    for lines, font, color, spacing in blocks:
        for line in lines:
            draw.text((margin, y), line, font=font, fill=color)
            y += int(font.size * spacing)
        y += gap

    if not slide.get("image") and blocks:
        draw.rectangle((margin, SAFE_TOP, margin + 120, SAFE_TOP + 14), fill=accent)
    if total > 1 and style.get("numbers", True):
        counter_font = ImageFont.truetype(style["body_font"], 34) if style["body_font"] \
            else ImageFont.load_default()
        label = f"{index}/{total}"
        tw = draw.textlength(label, font=counter_font)
        draw.text((SLIDE_W - margin - tw, SLIDE_H - SAFE_BOTTOM), label, font=counter_font, fill=fg)
    if style.get("handle"):
        handle_font = ImageFont.truetype(style["body_font"], 34) if style["body_font"] \
            else ImageFont.load_default()
        draw.text((margin, SLIDE_H - SAFE_BOTTOM), style["handle"], font=handle_font, fill=fg)
    return img


def cmd_carousel(args):
    try:
        import PIL  # noqa: F401
    except ImportError:
        die("falta Pillow: `pip install pillow`")
    spec_path = Path(args.spec).expanduser()
    spec = json.loads(read_text(spec_path))
    slides = spec.get("slides") or []
    if not slides:
        die("el JSON no tiene \"slides\"")
    if len(slides) > CAROUSEL_MAX and (spec.get("style") or {}).get("format") != "story":
        die(f"{len(slides)} slides; el máximo es {CAROUSEL_MAX}")
    style = {"background": "#111111", "color": "#FFFFFF", "accent": "#FFD400",
             "font": None, "body_font": None, "handle": None, "numbers": True}
    style.update(spec.get("style") or {})
    if style.get("format") == "story":
        global SLIDE_H, SAFE_TOP, SAFE_BOTTOM
        SLIDE_H, SAFE_TOP, SAFE_BOTTOM = 1920, 260, 380
        if "numbers" not in (spec.get("style") or {}):
            style["numbers"] = False
    style["font"] = style["font"] if style["font"] and Path(style["font"]).exists() \
        else find_font([style["font"] or "Montserrat ExtraBold", "Montserrat", "Inter", "DejaVu Sans"])
    style["body_font"] = style["body_font"] if style["body_font"] and Path(style["body_font"]).exists() \
        else find_font(["Montserrat SemiBold", "Montserrat", "Inter", "DejaVu Sans"])
    if not style["font"]:
        warn("no encontré una fuente TrueType; uso la de Pillow por defecto")

    out = Path(args.out).expanduser() if args.out else Path.home() / "Downloads" / f"{spec_path.stem}-carrusel"
    out.mkdir(parents=True, exist_ok=True)
    for i, slide in enumerate(slides, 1):
        img = render_slide(slide, style, i, len(slides), spec_path.parent)
        dest = out / f"{i:02d}.jpg"
        img.save(dest, "JPEG", quality=92, optimize=True)
        print(dest)


# ---------------------------------------------------------------- API

def credentials():
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token and (CONFIG_DIR / "token").exists():
        token = (CONFIG_DIR / "token").read_text().strip()
    if not token:
        die("falta IG_ACCESS_TOKEN (o el archivo ~/.config/instagram-skill/token). "
            "Ver la sección \"Conectar la cuenta\" del SKILL.md.")
    user = os.environ.get("IG_USER_ID")
    if not user and (CONFIG_DIR / "user_id").exists():
        user = (CONFIG_DIR / "user_id").read_text().strip()
    return token, user or "me"


def api(method, path, params=None, dry_run=False, url=None, headers=None, data=None,
        json_body=None, soft=False, token=None, host=None):
    """Llama a la Graph API. soft=True devuelve None ante un error de la API en vez de salir."""
    token = token or credentials()[0]
    params = dict(params or {})
    if url is None:
        url = f"{host or API_HOST}/{API_VERSION}/{path.lstrip('/')}"
    if dry_run:
        shown = json_body if json_body is not None else params
        print(f"[dry-run] {method} {url} {json.dumps(shown, ensure_ascii=False)}")
        return {"id": "DRY_RUN", "status_code": "FINISHED", "permalink": "https://instagram.com/p/DRY_RUN"}
    hdrs = {"Authorization": f"Bearer {token}"}
    hdrs.update(headers or {})
    body = data
    if method == "GET":
        if params:
            url += "?" + urllib.parse.urlencode(params)
    elif json_body is not None:
        body = json.dumps(json_body).encode()
        hdrs["Content-Type"] = "application/json"
    elif body is None:
        body = urllib.parse.urlencode(params).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            detail = json.loads(detail)["error"].get("message", detail)
        except (ValueError, KeyError, AttributeError):
            pass
        if soft:
            warn(f"la API respondió {e.code}: {detail}")
            return None
        die(f"la API respondió {e.code}: {detail}")
    except urllib.error.URLError as e:
        die(f"no pude conectar con {url}: {e.reason}")


def cmd_whoami(args):
    _, user = credentials()
    r = api("GET", user if user != "me" else "me",
            {"fields": "user_id,username,name,account_type,followers_count,media_count"})
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if r.get("user_id") and not os.environ.get("IG_USER_ID"):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        (CONFIG_DIR / "user_id").write_text(str(r["user_id"]))
        print(f"Guardé el IG_USER_ID en {CONFIG_DIR / 'user_id'}")


def wait_container(cid, dry_run, timeout=600):
    start = time.time()
    while True:
        r = api("GET", cid, {"fields": "status_code,status"}, dry_run=dry_run)
        code = r.get("status_code")
        if code in ("FINISHED", "PUBLISHED"):
            return
        if code in ("ERROR", "EXPIRED"):
            die(f"Instagram no pudo procesar el contenido: {r.get('status') or code}")
        if time.time() - start > timeout:
            die("Instagram tardó demasiado en procesar el contenido; reintentá más tarde")
        print(f"  procesando ({code})...", file=sys.stderr)
        time.sleep(5)


def upload_video_file(user, path, params, dry_run):
    """Crea un contenedor de video con subida reanudable desde un archivo local."""
    path = Path(path).expanduser()
    if not path.exists():
        die(f"no existe {path}")
    r = api("POST", f"{user}/media", dict(params, upload_type="resumable"), dry_run=dry_run)
    cid = r["id"]
    upload_url = r.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{API_VERSION}/{cid}"
    size = path.stat().st_size
    if dry_run:
        print(f"[dry-run] POST {upload_url} ({size} bytes de {path.name})")
        return cid
    token, _ = credentials()
    print(f"  subiendo {path.name} ({size / 1e6:.1f} MB)...", file=sys.stderr)
    api("POST", None, url=upload_url, data=path.read_bytes(),
        headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    return cid


def create_item(user, item, caption, dry_run, carousel_item=False):
    """item: {"video": ruta} | {"video_url": url} | {"image_url": url}"""
    params = {}
    if caption and not carousel_item:
        params["caption"] = caption
    if carousel_item:
        params["is_carousel_item"] = "true"
    if item.get("image_url"):
        params["image_url"] = item["image_url"]
        return api("POST", f"{user}/media", params, dry_run=dry_run)["id"]
    params["media_type"] = "VIDEO" if carousel_item else "REELS"
    if not carousel_item and item.get("share_to_feed") is not None:
        params["share_to_feed"] = "true" if item["share_to_feed"] else "false"
    if item.get("cover_url"):
        params["cover_url"] = item["cover_url"]
    if item.get("video_url"):
        params["video_url"] = item["video_url"]
        return api("POST", f"{user}/media", params, dry_run=dry_run)["id"]
    if item.get("video"):
        return upload_video_file(user, item["video"], params, dry_run)
    die(f"elemento sin contenido: {item}")


def do_publish(post, dry_run=False):
    """post: {"type": "reel|image|carousel", "caption": str, "items": [...]}"""
    _, user = credentials()
    caption = post.get("caption") or ""
    problems = check_caption(caption)["problems"]
    if problems:
        die("el texto no es válido: " + "; ".join(problems))
    items = post["items"]
    if post["type"] == "carousel":
        if not 2 <= len(items) <= CAROUSEL_MAX:
            die(f"un carrusel lleva de 2 a {CAROUSEL_MAX} elementos (hay {len(items)})")
        children = []
        for item in items:
            cid = create_item(user, item, None, dry_run, carousel_item=True)
            wait_container(cid, dry_run)
            children.append(cid)
        cid = api("POST", f"{user}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                                            "caption": caption}, dry_run=dry_run)["id"]
    else:
        if len(items) != 1:
            die(f"un {post['type']} lleva un solo elemento")
        cid = create_item(user, items[0], caption, dry_run)
    wait_container(cid, dry_run)
    media = api("POST", f"{user}/media_publish", {"creation_id": cid}, dry_run=dry_run)
    info = api("GET", media["id"], {"fields": "permalink,timestamp"}, dry_run=dry_run)
    print(f"Publicado: {info.get('permalink', media['id'])}")
    return info


def post_from_args(args):
    caption = read_text(args.caption_file) if args.caption_file else (args.caption or "")
    items = []
    for v in args.video or []:
        items.append({"video": str(Path(v).expanduser().resolve())})
    for u in args.video_url or []:
        items.append({"video_url": u})
    for u in args.image_url or []:
        items.append({"image_url": u})
    if not items:
        die("indicá el contenido con --video, --video-url o --image-url")
    if args.type == "reel":
        if args.cover_url:
            items[0]["cover_url"] = args.cover_url
        if args.no_feed:
            items[0]["share_to_feed"] = False
    if args.type == "image" and any("image_url" not in i for i in items):
        die("una publicación de imagen necesita --image-url")
    return {"type": args.type, "caption": caption, "items": items}


def cmd_publish(args):
    post = post_from_args(args)
    if not args.yes and not args.dry_run:
        die("publicar es irreversible desde acá: confirmá con el usuario y agregá --yes")
    do_publish(post, dry_run=args.dry_run)


def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return []


def save_queue(queue):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2))


def parse_when(text):
    try:
        when = datetime.fromisoformat(text)
    except ValueError:
        die(f"fecha inválida: {text!r} (usar AAAA-MM-DD HH:MM)")
    if when.tzinfo is None:
        when = when.astimezone()  # hora local de la máquina
    return when


def cmd_schedule(args):
    post = post_from_args(args)
    when = parse_when(args.at)
    if when < datetime.now(timezone.utc):
        die("esa fecha ya pasó")
    problems = check_caption(post["caption"])["problems"]
    if problems:
        die("el texto no es válido: " + "; ".join(problems))
    queue = load_queue()
    post.update(id=f"p{int(time.time())}", at=when.isoformat(), status="pendiente")
    queue.append(post)
    save_queue(queue)
    print(f"Programado {post['id']} para {when:%Y-%m-%d %H:%M %Z} en {QUEUE_FILE}")


def cmd_queue(args):
    queue = load_queue()
    if args.remove:
        new = [p for p in queue if p["id"] != args.remove]
        if len(new) == len(queue):
            die(f"no hay ninguna publicación {args.remove}")
        save_queue(new)
        print(f"Quité {args.remove} de la cola")
        return
    if not queue:
        print("La cola está vacía")
    for p in sorted(queue, key=lambda p: p["at"]):
        first = (p.get("caption") or "").splitlines()[0][:60] if p.get("caption") else ""
        print(f"{p['id']}  {p['at'][:16]}  {p['type']:<8} {p['status']:<10} {first}")


def cmd_publish_due(args):
    queue = load_queue()
    now = datetime.now(timezone.utc)
    due = [p for p in queue if p["status"] == "pendiente" and datetime.fromisoformat(p["at"]) <= now]
    if not due:
        print("Nada para publicar")
        return
    for p in due:
        print(f"Publicando {p['id']} ({p['type']})...")
        info = do_publish(p, dry_run=args.dry_run)
        if not args.dry_run:
            p.update(status="publicado", permalink=info.get("permalink"))
            save_queue(queue)


def cmd_comments(args):
    _, user = credentials()
    me = api("GET", user, {"fields": "username"})
    username = me.get("username", "")
    since = datetime.now(timezone.utc) - timedelta(days=args.days)
    media = api("GET", f"{user}/media", {"fields": "id,caption,permalink,timestamp,comments_count",
                                         "limit": args.posts})
    pending = []
    for m in media.get("data", []):
        if datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00")) < since:
            continue
        if not m.get("comments_count"):
            continue
        comments = api("GET", f"{m['id']}/comments",
                       {"fields": "id,text,username,timestamp,replies{username,text}", "limit": 50})
        for c in comments.get("data", []):
            if c.get("username") == username:
                continue
            replies = (c.get("replies") or {}).get("data", [])
            if any(r.get("username") == username for r in replies):
                continue
            pending.append({"comment_id": c["id"], "username": c.get("username"), "text": c.get("text"),
                            "timestamp": c.get("timestamp"), "post": m.get("permalink"),
                            "post_caption": (m.get("caption") or "")[:200]})
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / "comments.json"
    out.write_text(json.dumps(pending, ensure_ascii=False, indent=2))
    print(json.dumps(pending, ensure_ascii=False, indent=2))
    print(f"{len(pending)} comentarios sin responder (guardados en {out})", file=sys.stderr)


def cmd_reply(args):
    if not args.yes and not args.dry_run:
        die("responder publica en Instagram: confirmá con el usuario y agregá --yes")
    r = api("POST", f"{args.comment_id}/replies", {"message": args.message}, dry_run=args.dry_run)
    print(f"Respondido: {r.get('id')}")


def cmd_private_reply(args):
    """Mensaje privado a quien comentó (entrega por palabra clave). Una sola vez por comentario."""
    if not args.yes and not args.dry_run:
        die("esto manda un DM: confirmá con el usuario y agregá --yes")
    _, user = credentials()
    r = api("POST", f"{user}/messages", dry_run=args.dry_run,
            json_body={"recipient": {"comment_id": args.comment_id}, "message": {"text": args.message}})
    print(f"DM enviado: {r.get('message_id') or r.get('id')}")


# ---------------------------------------------------------------- análisis

def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def to_num(v):
    """'12.345' → 12345, '1,2K' / '1.2k' → 1200, '3,4 mil' → 3400, '2M' → 2000000."""
    if v in (None, ""):
        return None
    if not isinstance(v, str):
        return float(v)
    t = v.strip().lower().replace(" ", "")
    mult = 1
    for suffix, m in (("mil", 1e3), ("k", 1e3), ("m", 1e6)):
        if t.endswith(suffix):
            t, mult = t[:-len(suffix)], m
            break
    if mult > 1:
        t = t.replace(",", ".")
    else:
        t = t.replace(".", "").replace(",", "")
    try:
        return float(t) * mult
    except ValueError:
        return None


def rank_outliers(rows, metric, group="account", min_posts=3):
    """Agrega 'multiple' = métrica / mediana de su cuenta. Devuelve filas ordenadas."""
    by_group = {}
    for r in rows:
        by_group.setdefault(r.get(group) or "?", []).append(r)
    out = []
    for name, items in by_group.items():
        vals = [to_num(r.get(metric)) for r in items]
        med = median(vals)
        if len([v for v in vals if v is not None]) < min_posts:
            warn(f"{name}: menos de {min_posts} publicaciones con {metric}; no se puede comparar")
            continue
        for r, v in zip(items, vals):
            if v is None or not med:
                continue
            out.append(dict(r, metric=metric, value=v, median=med, multiple=round(v / med, 2)))
    return sorted(out, key=lambda r: r["multiple"], reverse=True)


def load_rows(path):
    import csv
    p = Path(path).expanduser()
    text = read_text(p)
    if p.suffix.lower() == ".json":
        data = json.loads(text)
        return data.get("rows", data) if isinstance(data, dict) else data
    return list(csv.DictReader(text.splitlines()))


def short(text, n=60):
    t = " ".join((text or "").split())
    return t if len(t) <= n else t[:n - 1] + "…"


def cmd_outliers(args):
    rows = load_rows(args.file)
    metric = args.metric
    if metric == "auto":
        cols = set().union(*(r.keys() for r in rows)) if rows else set()
        metric = next((m for m in ("views", "plays", "reach", "engagement", "likes") if m in cols), None)
        if not metric:
            die("no encontré columna de métrica (views, plays, reach, engagement o likes); usá --metric")
        if metric == "likes" and "comments" in cols:
            for r in rows:
                r["engagement"] = (to_num(r.get("likes")) or 0) + (to_num(r.get("comments")) or 0)
            metric = "engagement"
    ranked = [r for r in rank_outliers(rows, metric, min_posts=args.min_posts) if r["multiple"] >= args.min]
    print(f"{len(ranked)} publicaciones con {metric} ≥ {args.min}x la mediana de su cuenta\n")
    print(f"{'múltiplo':>8}  {'cuenta':<20} {metric:>10}  texto")
    for r in ranked[:args.top]:
        print(f"{r['multiple']:>7}x  {short(r.get('account'), 20):<20} {int(r['value']):>10}  "
              f"{short(r.get('caption') or r.get('hook') or r.get('url'))}")
    if args.out:
        Path(args.out).expanduser().write_text(json.dumps(ranked[:args.top], ensure_ascii=False, indent=2))
        print(f"\nGuardado en {args.out}", file=sys.stderr)


def cmd_discover(args):
    """Últimas publicaciones de cuentas profesionales ajenas (Business Discovery)."""
    import csv
    token = os.environ.get("IG_FB_ACCESS_TOKEN")
    user = os.environ.get("IG_FB_USER_ID")
    if not token or not user:
        die("Business Discovery necesita IG_FB_ACCESS_TOKEN e IG_FB_USER_ID (token de Instagram API con "
            "Facebook Login, permiso instagram_basic). Sin eso, armá el CSV a mano (ver /ig-viral).")
    rows = []
    for username in args.usernames:
        username = username.lstrip("@")
        fields = (f"business_discovery.username({username}){{username,followers_count,"
                  f"media.limit({args.posts}){{caption,like_count,comments_count,media_product_type,"
                  f"permalink,timestamp}}}}")
        r = api("GET", user, {"fields": fields}, token=token, host="https://graph.facebook.com", soft=True)
        if not r:
            continue
        bd = r.get("business_discovery", {})
        for m in bd.get("media", {}).get("data", []):
            rows.append({"account": bd.get("username"), "followers": bd.get("followers_count"),
                         "url": m.get("permalink"), "date": m.get("timestamp", "")[:10],
                         "format": m.get("media_product_type"), "likes": m.get("like_count"),
                         "comments": m.get("comments_count"),
                         "caption": " ".join((m.get("caption") or "").split())})
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        cols = ["account", "followers", "url", "date", "format", "likes", "comments", "caption"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} publicaciones de {len(args.usernames)} cuentas → {out}")


def own_media(user, limit):
    items, after = [], None
    while len(items) < limit:
        params = {"fields": "id,caption,media_type,media_product_type,permalink,timestamp,"
                            "like_count,comments_count", "limit": min(50, limit - len(items))}
        if after:
            params["after"] = after
        page = api("GET", f"{user}/media", params)
        items += page.get("data", [])
        after = page.get("paging", {}).get("cursors", {}).get("after")
        if not after or not page.get("data"):
            break
    return items[:limit]


def cmd_audit(args):
    _, user = credentials()
    media = own_media(user, args.posts)
    rows = []
    for m in media:
        ins = api("GET", f"{m['id']}/insights",
                  {"metric": "views,reach,saved,shares,likes,comments,total_interactions"}, soft=True) \
            or api("GET", f"{m['id']}/insights", {"metric": "reach,saved,shares"}, soft=True) or {}
        vals = {d["name"]: (d.get("values") or [{}])[0].get("value", d.get("total_value", {}).get("value"))
                for d in ins.get("data", [])}
        reach = vals.get("reach") or 0
        rows.append({"account": "yo", "url": m.get("permalink"), "date": m.get("timestamp", "")[:10],
                     "format": m.get("media_product_type") or m.get("media_type"),
                     "caption": " ".join((m.get("caption") or "").split()),
                     "views": vals.get("views"), "reach": reach or None,
                     "likes": vals.get("likes", m.get("like_count")),
                     "comments": vals.get("comments", m.get("comments_count")),
                     "shares": vals.get("shares"), "saves": vals.get("saved"),
                     "sends_per_1k": round(1000 * (vals.get("shares") or 0) / reach, 1) if reach else None,
                     "saves_per_1k": round(1000 * (vals.get("saved") or 0) / reach, 1) if reach else None})
    ranked = rank_outliers(rows, "reach", min_posts=3)
    send_med = median(r["sends_per_1k"] for r in rows)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = CACHE_DIR / "audit.json"
    out.write_text(json.dumps({"median_reach": ranked[0]["median"] if ranked else None,
                               "median_sends_per_1k": send_med, "posts": ranked},
                              ensure_ascii=False, indent=2))
    print(f"{len(rows)} publicaciones · alcance mediano {int(ranked[0]['median']) if ranked else '-'} · "
          f"envíos/1000 de alcance mediano {send_med}\n")
    print(f"{'múlt.':>6} {'alcance':>8} {'env/1k':>7} {'guar/1k':>8}  {'formato':<9} {'fecha':<10}  texto")
    for r in ranked:
        print(f"{r['multiple']:>5}x {int(r['value']):>8} {r['sends_per_1k'] or 0:>7} {r['saves_per_1k'] or 0:>8}  "
              f"{(r['format'] or '')[:9]:<9} {r['date']:<10}  {short(r['caption'], 50)}")
    print(f"\nDetalle en {out}", file=sys.stderr)


def cmd_profile(args):
    _, user = credentials()
    base = "username,name,account_type,followers_count,follows_count,media_count,profile_picture_url"
    r = api("GET", user, {"fields": base + ",biography,website"}, soft=True) \
        or api("GET", user, {"fields": base})
    print(json.dumps(r, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------- main

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check-video", help="verifica requisitos de Reels")
    c.add_argument("video")
    c.set_defaults(func=cmd_check_video)

    c = sub.add_parser("caption", help="valida el texto de una publicación")
    c.add_argument("file")
    c.add_argument("--max-hashtags", type=int, default=HASHTAG_MAX)
    c.set_defaults(func=cmd_caption)

    c = sub.add_parser("carousel", help="genera las imágenes de un carrusel")
    c.add_argument("spec", help="JSON con style y slides")
    c.add_argument("--out", help="carpeta de salida (default ~/Downloads/<spec>-carrusel)")
    c.set_defaults(func=cmd_carousel)

    c = sub.add_parser("whoami", help="comprueba el token")
    c.set_defaults(func=cmd_whoami)

    def content_args(c):
        c.add_argument("--type", choices=["reel", "image", "carousel"], required=True)
        c.add_argument("--caption-file")
        c.add_argument("--caption")
        c.add_argument("--video", action="append", help="archivo de video local (se sube a Instagram)")
        c.add_argument("--video-url", action="append", help="URL pública de un video")
        c.add_argument("--image-url", action="append", help="URL pública de una imagen JPEG")
        c.add_argument("--cover-url", help="portada del Reel (URL pública)")
        c.add_argument("--no-feed", action="store_true", help="el Reel no aparece en el feed")
        c.add_argument("--dry-run", action="store_true", help="mostrar las llamadas sin hacerlas")

    c = sub.add_parser("publish", help="publica ahora")
    content_args(c)
    c.add_argument("--yes", action="store_true", help="el usuario confirmó la publicación")
    c.set_defaults(func=cmd_publish)

    c = sub.add_parser("schedule", help="programa una publicación")
    content_args(c)
    c.add_argument("--at", required=True, help="AAAA-MM-DD HH:MM (hora local)")
    c.set_defaults(func=cmd_schedule)

    c = sub.add_parser("queue", help="muestra la cola")
    c.add_argument("--remove", help="id a quitar de la cola")
    c.set_defaults(func=cmd_queue)

    c = sub.add_parser("publish-due", help="publica lo vencido de la cola")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(func=cmd_publish_due)

    c = sub.add_parser("comments", help="comentarios sin responder")
    c.add_argument("--days", type=int, default=7, help="solo publicaciones de los últimos N días")
    c.add_argument("--posts", type=int, default=10, help="cuántas publicaciones revisar")
    c.set_defaults(func=cmd_comments)

    c = sub.add_parser("reply", help="responde un comentario")
    c.add_argument("comment_id")
    c.add_argument("message")
    c.add_argument("--yes", action="store_true", help="el usuario aprobó la respuesta")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(func=cmd_reply)

    c = sub.add_parser("private-reply", help="DM a quien comentó (palabra clave)")
    c.add_argument("comment_id")
    c.add_argument("message")
    c.add_argument("--yes", action="store_true", help="el usuario aprobó el mensaje")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(func=cmd_private_reply)

    c = sub.add_parser("outliers", help="rankea publicaciones por múltiplo sobre la mediana de su cuenta")
    c.add_argument("file", help="CSV o JSON con account, url, caption y una métrica (views, likes…)")
    c.add_argument("--metric", default="auto")
    c.add_argument("--min", type=float, default=2.0, help="múltiplo mínimo (default 2x)")
    c.add_argument("--min-posts", type=int, default=3, help="publicaciones mínimas por cuenta")
    c.add_argument("--top", type=int, default=30)
    c.add_argument("--out", help="guardar el ranking en JSON")
    c.set_defaults(func=cmd_outliers)

    c = sub.add_parser("discover", help="baja publicaciones de cuentas del nicho (Business Discovery)")
    c.add_argument("usernames", nargs="+")
    c.add_argument("--posts", type=int, default=25)
    c.add_argument("--out", default=str(CACHE_DIR / "nicho.csv"))
    c.set_defaults(func=cmd_discover)

    c = sub.add_parser("audit", help="métricas de tus publicaciones, rankeadas por múltiplo")
    c.add_argument("--posts", type=int, default=30)
    c.set_defaults(func=cmd_audit)

    c = sub.add_parser("profile", help="datos de tu perfil")
    c.set_defaults(func=cmd_profile)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
