#!/usr/bin/env python3
"""Detecta marcas de texto escrito por IA en un texto en español para Instagram.

Uso:
  python3 detect.py texto.txt [--voseo] [--min 80] [--json]
  cat texto.txt | python3 detect.py - --voseo

Da un puntaje de 0 a 100 (100 = suena humano) y lista cada marca con su línea y
cómo arreglarla. Sale con código 1 si el puntaje queda por debajo de --min.
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

# (patrón, peso, qué es, cómo arreglarlo)
PHRASES = [
    (r"\bsin lugar a dudas\b", 4, "muletilla", "borrala"),
    (r"\ben el (mundo|panorama) (actual|de hoy|digital)\b", 5, "apertura genérica", "arrancá con el dato o la escena"),
    (r"\ben la era (digital|de la ia|actual)\b", 5, "apertura genérica", "arrancá con el dato o la escena"),
    (r"\b(es importante|cabe) (destacar|mencionar|resaltar|señalar)\b", 5, "relleno", "decilo directo"),
    (r"\ben (resumen|conclusión|definitiva)\b", 4, "cierre de redacción escolar", "cerrá con el llamado a la acción"),
    (r"\b(sum[eé]rgete|desbloque[aá]|potenci[aá]|transform[aá]|eleva|elev[aá]) (tu|tus)\b", 5,
     "verbo de folleto", "decí qué cambia concretamente"),
    (r"\b(un|este|tu) viaje\b", 3, "metáfora del viaje", "nombrá el proceso real"),
    (r"\b(crucial|fundamental|imprescindible|esencial|clave)\b", 2, "adjetivo inflado", "mostrá por qué importa"),
    (r"\b(revolucionari[oa]|game.?changer|disruptiv[oa]|innovador[a]?)\b", 4, "exageración", "da el resultado concreto"),
    (r"\b(panorama|ecosistema|sinergia|tapiz|hol[ií]stic[oa]|robust[oa])\b", 4, "vocabulario corporativo", "palabra común"),
    (r"\bnavegar (por )?(el|los|la|las)\b", 3, "\"navegar\" metafórico", "usá manejar, entender, atravesar"),
    (r"\baprovech(a|ar|á) al m[aá]ximo\b", 3, "frase hecha", "decí qué hacer"),
    (r"\b(d[eé]jame|perm[ií]teme) (contarte|decirte|explicarte)\b", 4, "anuncio vacío", "contalo directamente"),
    (r"\by lo mejor de todo\b", 3, "remate de infomercial", "borralo"),
    (r"\bal final del d[ií]a\b", 3, "calco del inglés", "\"al final\" o borralo"),
    (r"\bhace sentido\b", 3, "calco del inglés", "\"tiene sentido\""),
    (r"\bspoiler:", 3, "remate gastado", "borralo"),
    (r"\b(aqu[ií]|ac[aá]) est[aá] (la cosa|el truco|el secreto)\b", 4, "suspenso fabricado", "andá al punto"),
    (r"\bno (es|se trata de) [^.,;!?\n]{1,40}[,;] (es|sino)\b", 6, "\"no es X, es Y\"", "afirmá Y solo"),
    (r"\bm[aá]s (que|all[aá] de) (un|una) [^.,\n]{1,25}, es\b", 5, "\"más que X, es Y\"", "afirmá Y solo"),
]

TU_FORMS = r"\b(puedes|tienes|quieres|sabes|eres|haces|necesitas|imaginas|piensas|buscas|sientes|" \
           r"crees|vienes|dices|cuéntame|dime|descubre|aprende|imagina|piensa)\b"
VOS_FORMS = r"\b(podés|tenés|querés|sabés|sos|hacés|necesitás|imaginás|pensás|buscás|sentís|" \
            r"creés|venís|decís|contame|decime|descubrí|aprendé|imaginá|pensá)\b"
EMOJI_BULLET = re.compile(r"^\s*[✅✔➡✨\U0001F449\U0001F680\U0001F4A1\U0001F4CC"
                          r"\U0001F525\U0001F3AF\U0001F31F\U0001F4AA⭐\U0001F447\U0001F539\U0001F538]")
RHETORICAL = re.compile(r"¿(?:y )?(?:el|la|lo|los|las|mi|un|una)\s[^?\n]{1,25}\?\s+(?=[A-ZÁÉÍÓÚÑ¡])", re.I)


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if len(p.strip().split()) >= 2]


def analyze(text, voseo=False):
    lines = text.split("\n")
    hits = []

    def add(line_no, weight, what, fix, sample):
        hits.append({"line": line_no, "weight": weight, "what": what, "fix": fix, "sample": sample.strip()[:80]})

    for i, line in enumerate(lines, 1):
        low = line.lower()
        for pat, weight, what, fix in PHRASES:
            for m in re.finditer(pat, low):
                add(i, weight, what, fix, line[max(0, m.start() - 15):m.end() + 15])
        if "—" in line or " – " in line:
            add(i, 4 * (line.count("—") + line.count(" – ")), "raya (—)", "coma, punto o paréntesis", line)
        if EMOJI_BULLET.match(line):
            add(i, 2, "emoji como viñeta", "sacalo o usá un guion", line)
        if "**" in line or "__" in line:
            add(i, 3, "negrita markdown", "Instagram no la muestra: sacá los asteriscos", line)
        if re.match(r"^\s*#{1,3}\s", line):
            add(i, 3, "título markdown", "Instagram no lo muestra", line)
        for m in RHETORICAL.finditer(line):
            add(i, 3, "pregunta y respuesta propia (\"¿El secreto? …\")", "decí la respuesta directo", m.group(0))
        if line.count("!") >= 3 or "!!" in line:
            add(i, 2, "exceso de signos de exclamación", "uno alcanza, o ninguno", line)
        if len(re.findall(r"\b\w+, \w+ y \w+\b", line)) >= 1 and len(line) > 40:
            add(i, 1, "enumeración de tres", "si no son tres cosas reales, dejá una o dos", line)

    tu = re.findall(TU_FORMS, text, re.I)
    vos = re.findall(VOS_FORMS, text, re.I)
    if voseo and tu:
        add(0, 3 * len(tu), f"tuteo en un texto con voseo ({', '.join(sorted(set(t.lower() for t in tu)))})",
            "pasalo a vos (fix.py --voseo)", "")
    elif tu and vos:
        add(0, 6, "mezcla tú y vos", "elegí una sola forma", f"tú: {tu[0]} / vos: {vos[0]}")

    sents = sentences(text)
    if len(sents) >= 6:
        lens = [len(s.split()) for s in sents]
        spread = statistics.pstdev(lens) / max(1, statistics.mean(lens))
        if spread < 0.35:
            add(0, 6, f"oraciones todas del mismo largo (variación {spread:.2f})",
                "mezclá frases cortas de 2–4 palabras con otras más largas", "")
    endings = [s.split()[-1].lower().strip(".!?") for s in sents if s.split()]
    if len(endings) > 4 and len(set(endings)) < len(endings) * 0.6:
        add(0, 2, "muchas oraciones terminan igual", "variá los cierres", "")

    score = max(0, 100 - sum(h["weight"] for h in hits))
    return {"score": score, "hits": sorted(hits, key=lambda h: (h["line"], -h["weight"]))}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="archivo de texto, o - para leer de stdin")
    p.add_argument("--voseo", action="store_true", help="el texto debe ir con vos (rioplatense)")
    p.add_argument("--min", type=int, default=80, help="puntaje mínimo aceptable")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    text = sys.stdin.read() if args.file == "-" else Path(args.file).expanduser().read_text(encoding="utf-8")
    r = analyze(text, args.voseo)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"Puntaje humano: {r['score']}/100" + ("  ✓" if r["score"] >= args.min else f"  ✗ (mínimo {args.min})"))
        for h in r["hits"]:
            where = f"L{h['line']}" if h["line"] else "global"
            print(f"  [{where:>6}] -{h['weight']:<2} {h['what']} → {h['fix']}")
            if h["sample"]:
                print(f"           «{h['sample']}»")
    sys.exit(0 if r["score"] >= args.min else 1)


if __name__ == "__main__":
    main()
