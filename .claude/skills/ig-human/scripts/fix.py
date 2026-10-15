#!/usr/bin/env python3
"""Arregla de forma segura las marcas mecánicas de texto de IA (español, Instagram).

Uso:
  python3 fix.py texto.txt [--voseo] [--in-place | --out nuevo.txt]
  cat texto.txt | python3 fix.py - --voseo

Qué hace (solo cambios que no alteran el sentido):
  - rayas (—, –) entre palabras → coma o punto,
  - saca negritas/títulos markdown y emojis usados como viñetas,
  - borra muletillas de apertura ("Es importante destacar que", "En resumen,", …),
  - "!!!" → "!" y emojis repetidos seguidos → uno,
  - con --voseo, pasa el tuteo a vos (puedes → podés, cuéntame → contame, …).
Lo que requiere reescribir ideas (no es X, es Y; frases de folleto) queda para Claude:
volver a correr detect.py después.
"""

import argparse
import difflib
import re
import sys
from pathlib import Path

FILLERS = [
    r"es importante (destacar|mencionar|resaltar|señalar) que\s*",
    r"cabe (destacar|mencionar|resaltar|señalar) que\s*",
    r"sin lugar a dudas,?\s*",
    r"en el mundo (actual|de hoy),?\s*",
    r"en la era (digital|actual),?\s*",
    r"en (resumen|conclusión|definitiva),\s*",
    r"(d[eé]jame|perm[ií]teme) (contarte|decirte) (algo|una cosa)?:?\s*",
    r"y lo mejor de todo(\s*es)?( que)?:?\s*",
    r"spoiler:\s*",
]

# Formas de tú inequívocas → vos. Los imperativos ambiguos con la 3.ª persona
# (mira, guarda, deja…) solo se cambian a inicio de oración (ver IMPERATIVES).
VOSEO = {
    "puedes": "podés", "tienes": "tenés", "quieres": "querés", "sabes": "sabés", "eres": "sos",
    "haces": "hacés", "necesitas": "necesitás", "imaginas": "imaginás", "piensas": "pensás",
    "buscas": "buscás", "sientes": "sentís", "crees": "creés", "vienes": "venís", "dices": "decís",
    "debes": "debés", "estás": "estás", "vas": "vas", "has": "has", "conoces": "conocés",
    "entiendes": "entendés", "prefieres": "preferís", "usas": "usás", "publicas": "publicás",
    "cuéntame": "contame", "dime": "decime", "escríbeme": "escribime", "mándame": "mandame",
    "sígueme": "seguime", "avísame": "avisame", "pruébalo": "probalo", "guárdalo": "guardalo",
    "compártelo": "compartilo", "pruébala": "probala", "guárdala": "guardala", "compártela": "compartila",
    "contigo": "con vos", "tú": "vos",
}
IMPERATIVES = {
    "mira": "mirá", "guarda": "guardá", "deja": "dejá", "comenta": "comentá", "comparte": "compartí",
    "escribe": "escribí", "sigue": "seguí", "prueba": "probá", "empieza": "empezá", "descubre": "descubrí",
    "aprende": "aprendé", "imagina": "imaginá", "piensa": "pensá", "toca": "tocá", "manda": "mandá",
    "etiqueta": "etiquetá", "busca": "buscá", "haz": "hacé", "ven": "vení", "ten": "tené", "di": "decí",
    "sal": "salí", "pon": "poné", "elige": "elegí", "responde": "respondé", "lee": "leé", "usa": "usá",
    "planifica": "planificá", "graba": "grabá", "analiza": "analizá", "edita": "editá", "publica": "publicá",
    "crea": "creá", "revisa": "revisá", "cambia": "cambiá", "agrega": "agregá", "sube": "subí",
    "escucha": "escuchá", "pregunta": "preguntá", "anota": "anotá", "evita": "evitá", "olvida": "olvidá",
    "recuerda": "recordá", "intenta": "intentá", "fíjate": "fijate", "anímate": "animate",
}
EMOJI = "[\U0001F300-\U0001FAFF☀-➿⭐]"
BULLET = re.compile(r"^(\s*)(?:[✅✔➡✨\U0001F449\U0001F680\U0001F4A1\U0001F4CC"
                    r"\U0001F525\U0001F3AF\U0001F31F\U0001F4AA⭐\U0001F447\U0001F539\U0001F538]️?\s*)+")


def match_case(src, dst):
    if src.isupper() and len(src) > 1:
        return dst.upper()
    if src[0].isupper():
        return dst[0].upper() + dst[1:]
    return dst


def capitalize_starts(text):
    return re.sub(r"(^|[.!?]\s+|\n\s*)([¿¡]?)([a-záéíóúñ])",
                  lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)


def fix_dashes(line):
    # inciso entre dos rayas → entre comas
    line = re.sub(r"\s*[—–]\s*([^—–\n]{1,80}?)\s*[—–]\s*", r", \1, ", line)
    # raya suelta antes del final de la idea → punto si lo que sigue es largo, si no coma
    def single(m):
        rest = m.group(2)
        return f"{m.group(1)}. {rest[0].upper()}{rest[1:]}" if len(rest.split()) >= 4 else f"{m.group(1)}, {rest}"
    line = re.sub(r"(\w[\w)»\"']*)\s*[—–]\s*(\S.*)", single, line)
    return re.sub(r",\s*([.!?])", r"\1", line)


def fix(text, voseo=False):
    out = []
    for line in text.split("\n"):
        line = BULLET.sub(r"\1", line)
        line = re.sub(r"^\s*#{1,3}\s+", "", line)
        line = line.replace("**", "").replace("__", "")
        if re.search(r"\w\s*[—–]\s*\w", line):
            line = fix_dashes(line)
        for pat in FILLERS:
            line = re.sub(r"(^|(?<=[.!?¡¿]\s))" + pat, r"\1", line, flags=re.I)
        line = re.sub(r"!{2,}", "!", line)
        line = re.sub(r"\?{2,}", "?", line)
        line = re.sub(f"({EMOJI})(️?)(?:\\s*\\1️?)+", r"\1\2", line)
        if voseo:
            line = re.sub(r"\b(" + "|".join(VOSEO) + r")\b",
                          lambda m: match_case(m.group(1), VOSEO[m.group(1).lower()]), line, flags=re.I)
            line = re.sub(r"(^|[.!?]\s+|[¡¿])(" + "|".join(IMPERATIVES) + r")\b",
                          lambda m: m.group(1) + match_case(m.group(2), IMPERATIVES[m.group(2).lower()]),
                          line, flags=re.I)
        out.append(re.sub(r"[ \t]{2,}", " ", line).rstrip())
    return capitalize_starts("\n".join(out))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="archivo de texto, o - para leer de stdin")
    p.add_argument("--voseo", action="store_true", help="pasar el tuteo a vos")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--in-place", action="store_true", help="sobrescribir el archivo")
    g.add_argument("--out", help="guardar en otro archivo")
    args = p.parse_args()
    src = sys.stdin.read() if args.file == "-" else Path(args.file).expanduser().read_text(encoding="utf-8")
    new = fix(src, args.voseo)
    changed = sum(1 for a, b in zip(src.split("\n"), new.split("\n")) if a != b)
    if args.in_place and args.file != "-":
        Path(args.file).expanduser().write_text(new + ("\n" if src.endswith("\n") else ""), encoding="utf-8")
    elif args.out:
        Path(args.out).expanduser().write_text(new + ("\n" if src.endswith("\n") else ""), encoding="utf-8")
    else:
        print(new)
    if args.in_place or args.out:
        for line in difflib.unified_diff(src.split("\n"), new.split("\n"), "antes", "después", lineterm="", n=0):
            print(line, file=sys.stderr)
    print(f"{changed} líneas cambiadas", file=sys.stderr)


if __name__ == "__main__":
    main()
