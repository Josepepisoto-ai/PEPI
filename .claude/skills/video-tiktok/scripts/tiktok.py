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


# ---------------------------------------------------------------- zoom

def find_phrase(words, phrase, used):
    """Índices (i, j) de la primera aparición de `phrase` que no se haya usado."""
    target = [normalize(x) for x in phrase.split() if normalize(x)]
    norm = [normalize(w["word"]) for w in words]
    for i in range(len(norm) - len(target) + 1):
        if norm[i:i + len(target)] == target and (i, phrase) not in used:
            used.add((i, phrase))
            return i, i + len(target) - 1
    return None


def zoom_ranges(words, segs, phrases, hold):
    """Rangos (en tiempo del video cortado) con primer plano, uno por frase importante."""
    ranges, used = [], set()
    for phrase in phrases:
        hit = find_phrase(words, phrase, used)
        if not hit:
            die(f"no encontré la frase para el zoom: {phrase!r}")
        i, j = hit
        ranges.append((remap(words[i]["start"], segs), remap(words[j]["end"], segs) + hold))
    return ranges


# ---------------------------------------------------------------- render

def audio_chain(mutes):
    chain = ["highpass=f=80", "lowpass=f=12000", "afftdn=nr=12:nf=-30:tn=1"]
    if mutes:
        expr = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in mutes)
        chain.append(f"volume=0:enable='{expr}'")
    return ",".join(chain)


def build_filter(info, segs, flip, mutes, ass_name, loudnorm, zooms=(), zoom=1.3, zoom_y=0.42):
    fps = info["fps"]
    vpre = [f"fps={fps}"]
    if flip:
        vpre.append("hflip")
    vframe = [
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase",
        f"crop={WIDTH}:{HEIGHT}",
        "setsar=1",
    ]
    vpost = []
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
    if zooms:
        # Primer plano: corte duro a una versión ampliada, anclada en la cara (zoom_y).
        zw, zh = round(WIDTH * zoom / 2) * 2, round(HEIGHT * zoom / 2) * 2
        enable = "+".join(f"between(t,{s:.3f},{e:.3f})" for s, e in zooms)
        parts.append(f"[vc]{','.join(vframe)},split=2[vn][vz]")
        parts.append(f"[vz]scale={zw}:{zh},crop={WIDTH}:{HEIGHT}:{(zw - WIDTH) // 2}:"
                     f"{round((zh - HEIGHT) * zoom_y)}[vzz]")
        parts.append(f"[vn][vzz]overlay=0:0:enable='{enable}',{','.join(vpost)}[vout]")
    else:
        parts.append(f"[vc]{','.join(vframe + vpost)}[vout]")
    parts.append(f"[ac]{apost}[aout]")
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
    mutes = mute_ranges(words, args.pad)

    ass_name = None
    if not args.no_subs:
        ass_name = "subs.ass"
        build_ass(words, segs, wd / ass_name, args.font, args.font_size, args.margin_v, args.upper)

    loud = measure_loudness(video, segs, mutes, wd)
    zooms = zoom_ranges(words, segs, args.zoom, args.zoom_hold) if args.zoom else []
    graph = build_filter(info, segs, args.flip, mutes, ass_name, loud, zooms, args.zoom_level, args.zoom_y)
    out = Path(args.out).expanduser().resolve() if args.out else default_output(video)
    out.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats", "-i", video,
         "-filter_complex", graph, "-map", "[vout]", "-map", "[aout]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(info["fps"]),
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
    r.add_argument("--upper", action="store_true", help="subtítulos en MAYÚSCULAS")
    r.add_argument("--zoom", action="append", default=[], metavar="FRASE",
                   help="primer plano mientras se dice esta frase (repetible)")
    r.add_argument("--zoom-level", type=float, default=1.3, help="cuánto acerca el primer plano")
    r.add_argument("--zoom-y", type=float, default=0.42,
                   help="altura de la cara (0 = arriba, 1 = abajo) para anclar el zoom")
    r.add_argument("--zoom-hold", type=float, default=0.3, help="segundos extra de zoom tras la frase")
    r.set_defaults(func=cmd_render)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
