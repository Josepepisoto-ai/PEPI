#!/usr/bin/env python3
"""Pipeline para convertir un video hablado en un video vertical estilo TikTok.

Subcomandos (se ejecutan en este orden desde el skill):

  frame       Extrae un fotograma para revisar si el video está en espejo.
  transcribe  Transcribe en español con timestamps por palabra y quita duplicados de Whisper.
  render      Limpia audio, corta pausas, quema subtítulos y exporta 1080x1920.
  text        Muestra la transcripción (texto plano) para revisarla.

Requisitos: ffmpeg/ffprobe con libass y `pip install faster-whisper`.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

WIDTH, HEIGHT = 1080, 1920
TARGET_LUFS = -14.0
TRUE_PEAK = -1.0


# ---------------------------------------------------------------- utilidades

def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, cwd=None, capture=False):
    print("+ " + " ".join(str(c) for c in cmd[:6]) + (" ..." if len(cmd) > 6 else ""), file=sys.stderr)
    res = subprocess.run([str(c) for c in cmd], cwd=cwd, text=True,
                         stdout=subprocess.PIPE if capture else None,
                         stderr=subprocess.PIPE if capture else None)
    if res.returncode != 0:
        if capture:
            sys.stderr.write(res.stderr[-4000:])
        die(f"falló el comando: {cmd[0]}")
    return res


def require_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            die(f"no encuentro {tool}. Instálalo (macOS: `brew install ffmpeg`).")


def probe(path):
    out = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams",
               "-show_format", path], capture=True).stdout
    info = json.loads(out)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    if video is None:
        die("el archivo no tiene pista de video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    w, h = int(video["width"]), int(video["height"])
    # Videos de celular guardan la rotación como metadato; ffmpeg la aplica al decodificar.
    rotation = 0
    for sd in video.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotation = int(float(sd["rotation"]))
    rotation = int(video.get("tags", {}).get("rotate", rotation))
    if abs(rotation) % 180 == 90:
        w, h = h, w
    num, den = (video.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    fps = min(60, max(24, round(fps))) if fps else 30
    duration = float(info["format"].get("duration") or video.get("duration") or 0)
    return {"width": w, "height": h, "fps": fps, "duration": duration, "has_audio": has_audio}


def work_dir(video):
    d = Path.home() / ".cache" / "video-tiktok" / Path(video).stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_output(video):
    downloads = Path.home() / "Downloads"
    base = downloads if downloads.is_dir() else Path(video).resolve().parent
    return base / f"{Path(video).stem}-final.mp4"


# ---------------------------------------------------------------- frame

def cmd_frame(args):
    require_ffmpeg()
    info = probe(args.video)
    t = args.at if args.at is not None else min(2.0, info["duration"] / 2)
    out = Path(args.out) if args.out else work_dir(args.video) / "frame.jpg"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", args.video,
         "-frames:v", "1", "-q:v", "2", out])
    print(out)


# ---------------------------------------------------------------- transcripción

def normalize(word):
    return re.sub(r"[^\w]", "", word.lower())


def dedupe_segments(segments):
    """Whisper a veces repite el mismo segmento (o lo alucina dos veces seguidas)."""
    kept = []
    for seg in segments:
        text = normalize(" ".join(w["word"] for w in seg["words"]))
        if not text:
            continue
        if kept:
            prev = kept[-1]
            prev_text = normalize(" ".join(w["word"] for w in prev["words"]))
            if text == prev_text or (len(text) > 12 and text in prev_text):
                continue
        kept.append(seg)
    return kept


def dedupe_words(words, min_n=3, max_n=12):
    """Quita n-gramas (n>=3) repetidos inmediatamente: 'vamos a ver vamos a ver' -> 'vamos a ver'.

    Repeticiones cortas ('no, no') se respetan porque suelen ser intencionales.
    """
    out = list(words)
    changed = True
    while changed:
        changed = False
        keys = [normalize(w["word"]) for w in out]
        for n in range(max_n, min_n - 1, -1):
            i = 0
            while i + 2 * n <= len(out):
                if keys[i:i + n] == keys[i + n:i + 2 * n] and all(keys[i:i + n]):
                    del out[i + n:i + 2 * n]
                    del keys[i + n:i + 2 * n]
                    changed = True
                else:
                    i += 1
    return out


def fix_spanish_questions(words):
    """Añade '¿' / '¡' de apertura cuando Whisper solo puso el cierre."""
    start = 0
    for i, w in enumerate(words):
        txt = w["word"]
        for close, open_ in (("?", "¿"), ("!", "¡")):
            if txt.endswith(close):
                # La pregunta empieza después del último signo de puntuación fuerte.
                j = i
                while j > start and not re.search(r"[.,;:?!]$", words[j - 1]["word"]):
                    j -= 1
                if open_ not in "".join(x["word"] for x in words[j:i + 1]):
                    words[j]["word"] = open_ + words[j]["word"]
        if re.search(r"[.;:?!]$", txt):
            start = i + 1
    return words


def cmd_transcribe(args):
    require_ffmpeg()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        die("falta faster-whisper. Instálalo con: pip install faster-whisper")

    wd = work_dir(args.video)
    audio = wd / "audio16k.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", args.video, "-vn", "-ac", "1", "-ar", "16000", audio])

    print(f"Transcribiendo con el modelo '{args.model}' (la primera vez lo descarga)...", file=sys.stderr)
    model = WhisperModel(args.model, device="auto", compute_type="auto")
    segs, _ = model.transcribe(
        str(audio), language=args.language, word_timestamps=True, vad_filter=True,
        condition_on_previous_text=False,  # evita bucles de repetición
        beam_size=5,
    )
    segments = []
    for s in segs:
        words = [{"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)}
                 for w in (s.words or []) if w.word.strip()]
        if words:
            segments.append({"words": words})

    before = sum(len(s["words"]) for s in segments)
    segments = dedupe_segments(segments)
    words = [w for s in segments for w in s["words"]]
    words = dedupe_words(words)
    # Timestamps monótonos (los duplicados a veces se solapan).
    clean, last_end = [], 0.0
    for w in words:
        if w["end"] <= last_end:
            continue
        w["start"] = max(w["start"], last_end)
        clean.append(w)
        last_end = w["end"]
    words = fix_spanish_questions(clean)
    removed = before - len(words)

    out = Path(args.out) if args.out else wd / "transcript.json"
    out.write_text(json.dumps({"video": str(Path(args.video).resolve()), "words": words},
                              ensure_ascii=False, indent=1))
    print(f"{len(words)} palabras ({removed} duplicadas eliminadas) -> {out}", file=sys.stderr)
    print(out)


def load_words(path):
    data = json.loads(Path(path).read_text())
    words = [w for w in data["words"] if w["word"].strip()]
    if not words:
        die("la transcripción está vacía")
    return words


def cmd_text(args):
    words = load_words(args.transcript)
    lines, cur = [], []
    for w in words:
        cur.append(w["word"])
        if re.search(r"[.?!]$", w["word"]):
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    print("\n".join(lines))


# ---------------------------------------------------------------- cortes

def speech_islands(words, max_pause):
    islands = [[words[0]["start"], words[0]["end"]]]
    for w in words[1:]:
        if w["start"] - islands[-1][1] <= max_pause:
            islands[-1][1] = max(islands[-1][1], w["end"])
        else:
            islands.append([w["start"], w["end"]])
    return islands


def keep_segments(words, duration, cut, max_pause, pad):
    if not cut:
        return [(0.0, duration)]
    segs = []
    for s, e in speech_islands(words, max_pause):
        s, e = max(0.0, s - pad), min(duration, e + pad)
        if segs and s <= segs[-1][1]:
            segs[-1] = (segs[-1][0], max(segs[-1][1], e))
        else:
            segs.append((s, e))
    return segs


def silence_ranges(video, min_dur, noise_db=-38):
    """Silencios reales del audio (Whisper a veces estira palabras sobre las pausas)."""
    res = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn", "-af",
               f"highpass=f=80,afftdn=nr=12:nf=-30,silencedetect=noise={noise_db}dB:d={min_dur}",
               "-f", "null", "-"], capture=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", res.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", res.stderr)]
    return list(zip(starts, ends))


def subtract_silences(segs, silences, pad):
    """Quita de cada tramo los silencios largos, dejando `pad` de aire a cada lado."""
    out = []
    for s, e in segs:
        cur = s
        for a, b in silences:
            a, b = a + pad, b - pad
            if b <= cur or a >= e or b - a <= 0:
                continue
            if a > cur:
                out.append((cur, a))
            cur = max(cur, b)
        if e - cur > 0.05:
            out.append((cur, e))
    return out


def mute_ranges(words, pad, min_gap=0.35):
    """Rangos (en tiempo original) entre frases donde se silencia el audio."""
    ranges = []
    for a, b in zip(words, words[1:]):
        s, e = a["end"] + pad, b["start"] - pad
        if e - s >= min_gap:
            ranges.append((s, e))
    return ranges


def remap(t, segs):
    """Tiempo original -> tiempo en el video cortado."""
    acc = 0.0
    for s, e in segs:
        if t < s:
            return acc
        if t <= e:
            return acc + (t - s)
        acc += e - s
    return acc


# ---------------------------------------------------------------- subtítulos

def ass_time(t):
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_escape(text):
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def group_words(words, max_words, max_chars, max_gap=0.6):
    groups, cur = [], []
    for w in words:
        if cur:
            chars = len(" ".join(x["word"] for x in cur + [w]))
            gap = w["start"] - cur[-1]["end"]
            if len(cur) >= max_words or chars > max_chars or gap > max_gap \
                    or re.search(r"[.,;:?!]$", cur[-1]["word"]):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    return groups


def build_ass(words, segs, path, font, font_size, margin_v, upper):
    mapped = []
    for w in words:
        s, e = remap(w["start"], segs), remap(w["end"], segs)
        if e - s < 0.05:
            e = s + 0.05
        text = w["word"].upper() if upper else w["word"]
        mapped.append({"word": ass_escape(text), "start": s, "end": e})

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTok,{font},{font_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,2,80,80,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    yellow = r"{\c&H00FFFF&\fscx110\fscy110}"   # ASS usa BGR: 00FFFF = amarillo
    reset = r"{\c&HFFFFFF&\fscx100\fscy100}"
    lines = []
    groups = group_words(mapped, max_words=3, max_chars=22)
    for gi, g in enumerate(groups):
        group_end = g[-1]["end"]
        if gi + 1 < len(groups):
            # Mantener el texto en pantalla hasta la siguiente frase si la pausa es corta.
            nxt = groups[gi + 1][0]["start"]
            group_end = nxt if nxt - group_end < 0.5 else group_end + 0.2
        else:
            group_end += 0.4
        for i, w in enumerate(g):
            start = w["start"] if i else min(w["start"], g[0]["start"])
            end = g[i + 1]["start"] if i + 1 < len(g) else group_end
            parts = [(yellow + x["word"] + reset) if j == i else x["word"] for j, x in enumerate(g)]
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},TikTok,,0,0,0,,{' '.join(parts)}")
    Path(path).write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- efectos (fx.json)

SFX_KINDS = ("pop", "whoosh", "ding")
SR = 48000


def synth_sfx(kind, path):
    """Genera un efecto de sonido simple en WAV mono 48 kHz (sin archivos externos)."""
    import math
    import random
    import struct
    import wave

    random.seed(7)
    if kind == "pop":
        n = int(SR * 0.09)
        out, phase = [], 0.0
        for i in range(n):
            t = i / SR
            phase += 2 * math.pi * (1100 * math.exp(-t * 40) + 250) / SR
            out.append(0.8 * math.sin(phase) * math.exp(-t * 45))
    elif kind == "ding":
        n = int(SR * 0.7)
        out = [0.5 * math.exp(-i / SR * 6) * (math.sin(2 * math.pi * 1568 * i / SR)
                                               + 0.4 * math.sin(2 * math.pi * 3136 * i / SR))
               for i in range(n)]
    elif kind == "whoosh":
        n = int(SR * 0.4)
        out, y = [], 0.0
        for i in range(n):
            x = i / n
            env = math.sin(math.pi * x) ** 2
            a = 0.02 + 0.25 * env          # filtro pasabajos que se abre y se cierra
            y += a * (random.uniform(-1, 1) - y)
            out.append(2.2 * env * y)
    else:
        die(f"efecto desconocido: {kind} (usar {', '.join(SFX_KINDS)})")
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32000)) for v in out))


def load_fx(path, words, segs):
    """Lee fx.json y convierte índices de palabras a tiempos del video cortado.

    Formato:
      {"zooms": [{"from": 12, "to": 14, "scale": 1.2, "focus": [0.5, 0.45]}],
       "sfx":   [{"word": 12, "sound": "pop"}]}
    `from`/`to`/`word` son índices de palabras de transcript.json; `focus` es el punto
    (x, y en 0..1) hacia el que se hace el zoom.
    """
    fx = json.loads(Path(path).read_text(encoding="utf-8"))
    zooms = []
    for z in fx.get("zooms", []):
        s = remap(words[z["from"]]["start"], segs) - 0.05
        e = remap(words[z["to"]]["end"], segs) + 0.25
        zooms.append({"s": max(0.0, s), "e": e, "scale": z.get("scale", 1.2),
                      "focus": z.get("focus", [0.5, 0.45])})
    zooms.sort(key=lambda z: z["s"])
    for a, b in zip(zooms, zooms[1:]):   # sin superposición
        a["e"] = min(a["e"], b["s"])
    sfx = []
    for x in fx.get("sfx", []):
        t = remap(words[x["word"]]["start"], segs)
        if x["sound"] == "whoosh":
            t -= 0.2                          # el pico del whoosh cae sobre la palabra
        sfx.append({"t": max(0.0, t), "sound": x["sound"], "gain": x.get("gain", 1.0)})
    return zooms, sfx


def zoom_filter(zooms, fps, ramp_in=0.12, ramp_out=0.2):
    def ease(x):
        c = f"clip({x},0,1)"
        return f"({c}*{c}*(3-2*{c}))"
    z_terms, fx_terms, fy_terms = [], [], []
    for z in zooms:
        s, e = z["s"], z["e"]
        env = f"{ease(f'(it-{s:.3f})/{ramp_in}')}*{ease(f'({e:.3f}-it)/{ramp_out}')}"
        z_terms.append(f"{z['scale'] - 1:.3f}*{env}")
        on = f"between(it,{s:.3f},{e:.3f})"
        fx_terms.append(f"{z['focus'][0] - 0.5:.3f}*{on}")
        fy_terms.append(f"{z['focus'][1] - 0.5:.3f}*{on}")
    zexpr = "1+" + "+".join(z_terms)
    fxe, fye = "0.5+" + "+".join(fx_terms), "0.5+" + "+".join(fy_terms)
    return (f"zoompan=z='{zexpr}':x='clip(({fxe})*iw-iw/zoom/2,0,iw-iw/zoom)'"
            f":y='clip(({fye})*ih-ih/zoom/2,0,ih-ih/zoom)':d=1:s={WIDTH}x{HEIGHT}:fps={fps}")


def synth_music(path, duration, bpm=100):
    """Base instrumental simple (Am-F-C-G, bombo, palmas, hi-hat, bajo y arpegio) en WAV estéreo."""
    import wave
    import numpy as np

    rng = np.random.default_rng(3)
    n = int(SR * duration)
    beat = 60 / bpm
    bar = 4 * beat
    t = np.arange(n) / SR
    left, right = np.zeros(n), np.zeros(n)

    def hz(m):
        return 440 * 2 ** ((m - 69) / 12)

    def add(sig, at, pan=0.0):
        i = int(at * SR)
        if i >= n:
            return
        sig = sig[: n - i]
        left[i:i + len(sig)] += sig * (1 - pan)
        right[i:i + len(sig)] += sig * (1 + pan)

    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
    for b in range(int(duration / bar) + 1):
        start, ch = b * bar, chords[b % 4]
        tt = np.arange(int(bar * SR)) / SR
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar - tt) / 0.3)
        pad = sum(np.sin(2 * np.pi * hz(m) * tt) + 0.3 * np.sin(4 * np.pi * hz(m) * tt) for m in ch)
        add(0.05 * env * pad, start)
        for k in range(8):                                   # bajo en corcheas
            d = np.arange(int(beat / 2 * SR)) / SR
            add(0.18 * np.sin(2 * np.pi * hz(ch[0] - 12) * d) * np.exp(-d * 6), start + k * beat / 2)
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12]
        for k in range(8):                                   # arpegio
            d = np.arange(int(0.4 * SR)) / SR
            note = np.sin(2 * np.pi * hz(arp[k % 4]) * d) * np.exp(-d * 9)
            add(0.07 * note, start + k * beat / 2, pan=0.4 if k % 2 else -0.4)
        for k in range(4):
            d = np.arange(int(0.25 * SR)) / SR
            kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-d * 30)) * d) * np.exp(-d * 14)
            add(0.45 * kick, start + k * beat)
            if k % 2:
                d = np.arange(int(0.15 * SR)) / SR
                add(0.12 * rng.uniform(-1, 1, len(d)) * np.exp(-d * 30), start + k * beat)
        for k in range(8):                                   # hi-hat
            d = np.arange(int(0.05 * SR)) / SR
            hat = np.diff(rng.uniform(-1, 1, len(d) + 1)) * np.exp(-d * 80)
            add(0.04 * hat, start + k * beat / 2, pan=0.2)

    fade = np.minimum(1, np.minimum(t / 1.0, (duration - t) / 1.5))
    st = np.stack([left, right], 1) * fade[:, None]
    st /= max(1e-9, np.abs(st).max()) / 0.8
    with wave.open(str(path), "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((st * 32000).astype("<i2").tobytes())


# ---------------------------------------------------------------- render

def audio_chain(mutes):
    chain = ["highpass=f=80", "lowpass=f=12000", "afftdn=nr=12:nf=-30:tn=1"]
    if mutes:
        expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in mutes)
        chain.append(f"volume=0:enable='{expr}'")
    return ",".join(chain)


def build_filter(info, segs, flip, mutes, ass_name, loudnorm, zooms=(), sfx=(), sfx_inputs=None,
                 music_input=None, music_lufs=-27.0, enhance=False):
    fps = info["fps"]
    vpre = [f"fps={fps}"]
    if flip:
        vpre.append("hflip")
    vpost = []
    if enhance:
        vpost.append("hqdn3d=1.5:1.5:6:6")              # quita el ruido de compresión de WhatsApp
    vpost += [
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase:flags=lanczos",
        f"crop={WIDTH}:{HEIGHT}",
        "setsar=1",
    ]
    if enhance:
        vpost += ["unsharp=5:5:0.7:5:5:0.0", "eq=contrast=1.04:saturation=1.08"]
    if zooms:
        vpost.append(zoom_filter(zooms, fps))
    if ass_name:
        vpost.append(f"ass={ass_name}")
    vpost.append("format=yuv420p")

    apre = audio_chain(mutes)
    apost = f"{loudnorm},aresample=48000"
    n = len(segs)
    parts = [f"[0:v]{','.join(vpre)},split={n}" + "".join(f"[v{i}]" for i in range(n)),
             f"[0:a]{apre},asplit={n}" + "".join(f"[a{i}]" for i in range(n))]
    for i, (s, e) in enumerate(segs):
        parts.append(f"[v{i}]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[vt{i}]")
        parts.append(f"[a{i}]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS,"
                     f"afade=t=in:d=0.01,afade=t=out:st={max(0, e - s - 0.01):.3f}:d=0.01[at{i}]")
    parts.append("".join(f"[vt{i}][at{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    parts.append(f"[vc]{','.join(vpost)}[vout]")
    if not sfx and music_input is None:
        parts.append(f"[ac]{apost}[aout]")
        return ";".join(parts)
    parts.append(f"[ac]{apost}[voice]")
    labels = []
    if music_input is not None:
        # La música baja sola cuando hay voz (ducking con sidechain).
        parts.append("[voice]asplit[voice][vsc]")
        parts.append(f"[{music_input}:a]aformat=sample_rates=48000:channel_layouts=mono,"
                     f"loudnorm=I={music_lufs:.1f}:TP=-3:LRA=11,aresample=48000,afade=t=in:d=1,"
                     f"afade=t=out:st={max(0, sum(e - s for s, e in segs) - 1.5):.2f}:d=1.5[mus]")
        parts.append("[mus][vsc]sidechaincompress=threshold=0.03:ratio=6:attack=30:release=500[duck]")
        labels.append("[duck]")
    for i, x in enumerate(sfx):
        ms = int(x["t"] * 1000)
        parts.append(f"[{sfx_inputs[x['sound']]}:a]volume={x['gain']:.2f},adelay={ms}:all=1,"
                     f"aformat=sample_rates=48000:channel_layouts=mono[s{i}]")
        labels.append(f"[s{i}]")
    parts.append("[voice]aformat=sample_rates=48000:channel_layouts=mono[vm]")
    parts.append(f"[vm]{''.join(labels)}amix=inputs={len(labels) + 1}:normalize=0:duration=first,"
                 "alimiter=limit=0.89:level=false[aout]")
    return ";".join(parts)


def measure_loudness(video, segs, mutes, cwd):
    """Primera pasada de loudnorm sobre el audio ya limpio y cortado."""
    n = len(segs)
    parts = [f"[0:a]{audio_chain(mutes)},asplit={n}" + "".join(f"[a{i}]" for i in range(n))]
    for i, (s, e) in enumerate(segs):
        parts.append(f"[a{i}]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[at{i}]")
    parts.append("".join(f"[at{i}]" for i in range(n)) +
                 f"concat=n={n}:v=0:a=1,loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:print_format=json[out]")
    res = run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-filter_complex", ";".join(parts),
               "-map", "[out]", "-f", "null", "-"], cwd=cwd, capture=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", res.stderr, re.S)
    if not m:
        return f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11"
    d = json.loads(m.group(0))
    if d["input_i"] in ("-inf", "inf"):
        return f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11"
    return (f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=11:measured_I={d['input_i']}:"
            f"measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:"
            f"measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")


def cmd_render(args):
    require_ffmpeg()
    video = str(Path(args.video).resolve())
    info = probe(video)
    if not info["has_audio"]:
        die("el video no tiene audio")
    wd = work_dir(video)
    transcript = Path(args.transcript) if args.transcript else wd / "transcript.json"
    if not transcript.exists():
        die(f"no existe {transcript}; corre primero `transcribe`")
    words = load_words(transcript)

    segs = keep_segments(words, info["duration"], not args.no_cut, args.max_pause, args.pad)
    if args.trim_silence and not args.no_cut:
        segs = subtract_silences(segs, silence_ranges(video, args.max_pause), args.pad)
    mutes = mute_ranges(words, args.pad)

    ass_name = None
    if not args.no_subs:
        ass_name = "subs.ass"
        build_ass(words, segs, wd / ass_name, args.font, args.font_size, args.margin_v, args.upper)

    zooms, sfx, sfx_inputs, extra = [], [], {}, []
    fx_path = Path(args.fx) if args.fx else wd / "fx.json"
    if not args.no_fx and fx_path.exists():
        zooms, sfx = load_fx(fx_path, words, segs)
        for kind in sorted({x["sound"] for x in sfx}):
            wav = wd / f"sfx_{kind}.wav"
            synth_sfx(kind, wav)
            sfx_inputs[kind] = len([x for x in extra if x == "-i"]) + 1
            extra += ["-i", str(wav)]
        print(f"Efectos: {len(zooms)} zooms, {len(sfx)} sonidos ({fx_path})", file=sys.stderr)

    music_input = None
    if args.music:
        kept = sum(e - s for s, e in segs)
        if args.music == "auto":
            music = wd / "music.wav"
            synth_music(music, kept + 0.5)
            extra += ["-i", str(music)]
        else:
            music = Path(args.music).expanduser().resolve()
            if not music.exists():
                die(f"no existe {music}")
            extra += ["-stream_loop", "-1", "-i", str(music)]   # se repite si es más corta
        music_input = len([x for x in extra if x == "-i"])
        print(f"Música: {music.name} a {args.music_volume} LUFS", file=sys.stderr)

    loud = measure_loudness(video, segs, mutes, wd)
    graph = build_filter(info, segs, args.flip, mutes, ass_name, loud, zooms, sfx, sfx_inputs,
                         music_input, args.music_volume, args.enhance)
    out = Path(args.out).expanduser().resolve() if args.out else default_output(video)
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats", "-i", video, *extra,
         "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "slow" if args.enhance else "medium",
         "-crf", "17" if args.enhance else "18", "-r", str(info["fps"]),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out], cwd=wd)

    kept = sum(e - s for s, e in segs)
    print(f"Duración: {info['duration']:.1f}s -> {kept:.1f}s ({len(segs)} tramos)", file=sys.stderr)
    print(out)


# ---------------------------------------------------------------- CLI

def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("frame", help="extrae un fotograma para revisar el espejo")
    f.add_argument("video")
    f.add_argument("--at", type=float, help="segundo del fotograma")
    f.add_argument("--out")
    f.set_defaults(func=cmd_frame)

    t = sub.add_parser("transcribe", help="transcribe con timestamps por palabra")
    t.add_argument("video")
    t.add_argument("--model", default=os.environ.get("TIKTOK_WHISPER_MODEL", "large-v3-turbo"))
    t.add_argument("--language", default="es")
    t.add_argument("--out")
    t.set_defaults(func=cmd_transcribe)

    x = sub.add_parser("text", help="imprime la transcripción en texto plano")
    x.add_argument("transcript")
    x.set_defaults(func=cmd_text)

    r = sub.add_parser("render", help="genera el video final 1080x1920")
    r.add_argument("video")
    r.add_argument("--transcript")
    r.add_argument("--out")
    r.add_argument("--flip", action="store_true", help="voltear horizontalmente (video en espejo)")
    r.add_argument("--no-cut", action="store_true", help="conservar las pausas (\"sin cortes\")")
    r.add_argument("--no-subs", action="store_true")
    r.add_argument("--max-pause", type=float, default=0.6, help="pausas mayores a esto se cortan (s)")
    r.add_argument("--pad", type=float, default=0.15, help="margen alrededor de cada frase (s)")
    r.add_argument("--font", default="Montserrat ExtraBold")
    r.add_argument("--font-size", type=int, default=86)
    r.add_argument("--margin-v", type=int, default=520, help="distancia de los subtítulos al borde inferior")
    r.add_argument("--fx", help="archivo de efectos (default: fx.json en la carpeta de trabajo)")
    r.add_argument("--no-fx", action="store_true", help="ignorar fx.json (sin zooms ni sonidos)")
    r.add_argument("--music", help="música de fondo: ruta a un .mp3/.wav, o `auto` para una base generada")
    r.add_argument("--music-volume", type=float, default=-27.0,
                   help="volumen de la música en LUFS (la voz va a -14; antes de bajar con la voz)")
    r.add_argument("--trim-silence", action="store_true",
                   help="cortar también los silencios detectados en el audio (pausas más cortas)")
    r.add_argument("--enhance", action="store_true",
                   help="mejora para videos de baja resolución (WhatsApp): reduce ruido, enfoca y realza color")
    r.add_argument("--upper", action="store_true", help="subtítulos en MAYÚSCULAS")
    r.set_defaults(func=cmd_render)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
