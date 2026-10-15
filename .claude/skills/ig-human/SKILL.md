---
name: ig-human
description: Humanizador para textos de Instagram en español — detecta lo que suena a IA (rayas, "no es X, es Y", frases de folleto, tuteo mezclado con voseo, emojis como viñetas, oraciones todas iguales) con un puntaje de 0 a 100, arregla lo mecánico con un script y reescribe el resto a mano. Úsalo cuando el usuario diga que un texto "suena a ChatGPT/IA", pida humanizarlo, o antes de entregar cualquier texto para publicar.
argument-hint: <archivo o texto> [voseo]
---

# ig-human

Dos scripts en `scripts/` (relativo a este archivo), sin dependencias:

- `detect.py <archivo|-> [--voseo] [--min 80] [--json]` → puntaje 0–100 y cada marca con su línea y
  cómo arreglarla. Sale con código 1 si queda por debajo de `--min`.
- `fix.py <archivo|-> [--voseo] [--in-place | --out nuevo.txt]` → arreglos seguros que no cambian el
  sentido: rayas → coma o punto, saca markdown y emojis-viñeta, borra muletillas de apertura,
  "!!!" → "!", y con `--voseo` pasa el tuteo a vos (podés, contame, guardá…). Muestra el diff.

Usar `--voseo` si el usuario escribe con vos (rioplatense). Si tutea, no usarlo.

## Pasos

1. Guardar el texto en un archivo (o usar `-` con stdin).
2. `python3 scripts/detect.py <archivo> [--voseo]` → anotar el puntaje inicial.
3. `python3 scripts/fix.py <archivo> [--voseo] --in-place`.
4. Volver a detectar y **reescribir a mano** lo que quede. Reglas:
   - "No es X, es Y" / "más que X, es Y" → afirmar Y directamente.
   - Verbos de folleto (transforma, potencia, desbloquea, eleva) → qué cambia concretamente, con un ejemplo.
   - "¿El secreto? …" → decir el secreto.
   - Enumeraciones de tres por reflejo → dejar las que de verdad existen.
   - Oraciones del mismo largo → mezclar frases de 2–4 palabras con otras largas. Una oración puede
     empezar con "Y" o "Pero".
   - Cambiar lo abstracto por algo concreto del usuario: un número, un nombre, una escena, un error real.
   - Mantener la voz del usuario: si tiene muletillas o expresiones propias en otros textos, usarlas.
5. Repetir hasta **≥ 85**. El puntaje es una ayuda, no la meta: leer el texto en voz alta; si suena a
   alguien hablando, está bien.

Mostrar: puntaje antes → después y el texto final. Si el usuario pidió solo detectar, no reescribir.
