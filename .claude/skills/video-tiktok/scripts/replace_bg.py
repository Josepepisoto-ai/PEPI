"""Reemplaza el fondo de un video por un azul oscuro usando segmentación de personas (rembg).

Uso: python3 replace_bg.py entrada.mp4 salida.mp4 [fondo.png]
Con `fondo.png` (mismo tamaño que el video) se usa esa imagen en lugar del azul; sirve, por ejemplo,
para sacar una sombra usando un fondo limpio armado a partir del propio video.
La máscara se calcula cada 2 cuadros, se interpola, se limpia y se suaviza en el tiempo.
"""
import json
import subprocess
import sys
import time

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

src, dst = sys.argv[1], sys.argv[2]
info = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "stream=width,height,r_frame_rate,nb_frames", "-of", "json", src],
    capture_output=True, text=True, check=True).stdout)["streams"][0]
W, H = info["width"], info["height"]
fps = info["r_frame_rate"]
total = int(info.get("nb_frames", 0))

# Fondo: azul oscuro con un leve degradé radial (más claro detrás de la cabeza).
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.3) / H) ** 2)
t = np.clip(d / 0.75, 0, 1)[..., None]
inner, outer = np.array([30, 58, 104], np.float32), np.array([8, 20, 44], np.float32)
bg = inner * (1 - t) + outer * t
if len(sys.argv) > 3:
    bg = np.asarray(Image.open(sys.argv[3]).convert("RGB").resize((W, H)), np.float32)

session = new_session("u2net_human_seg")


def mask_of(frame):
    m = np.asarray(remove(Image.fromarray(frame), session=session, only_mask=True), np.float32) / 255
    # quedarse con la figura principal (descarta manchas sueltas del fondo)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
    if n > 1:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        region = cv2.dilate((lab == keep).astype(np.uint8), np.ones((15, 15), np.uint8))
        m *= region
    return m


dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", f"{W}x{H}", "-r", fps, "-i", "-", "-i", src,
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "12", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)

smooth = None
pending = None          # cuadro impar esperando la máscara del siguiente cuadro par
prev_mask = None
n = 0
t0 = time.time()


def emit(frame, m):
    global smooth
    smooth = m if smooth is None else 0.55 * m + 0.45 * smooth      # suavizado temporal
    a = cv2.GaussianBlur(smooth, (0, 0), 1.5)[..., None]          # borde suave
    a = np.clip((a - 0.1) / 0.8, 0, 1)
    out = frame.astype(np.float32) * a + bg * (1 - a)
    enc.stdin.write(out.astype(np.uint8).tobytes())


while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    if n % 2 == 0:
        m = mask_of(frame)
        if pending is not None:
            emit(pending, 0.5 * (prev_mask + m))
            pending = None
        emit(frame, m)
        prev_mask = m
    else:
        pending = frame
    n += 1
    if n % 100 == 0:
        el = time.time() - t0
        print(f"{n}/{total} cuadros, {el / 60:.1f} min, faltan ~{el / n * (total - n) / 60:.1f} min", flush=True)
if pending is not None:
    emit(pending, prev_mask)
enc.stdin.close()
enc.wait()
dec.wait()
print(f"listo: {n} cuadros en {(time.time() - t0) / 60:.1f} min -> {dst}", flush=True)
