---
name: video-tiktok
description: Convierte un video hablado en español en un video vertical 1080x1920 listo para TikTok/Reels — corrige espejo, transcribe con Whisper sin duplicados, limpia y nivela el audio a -14 LUFS, corta pausas y quema subtítulos estilo TikTok con la palabra activa en amarillo. Úsalo cuando el usuario pase un video (.mp4/.mov) y pida editarlo para TikTok, subtitularlo, o diga "hacé lo mismo que el anterior" / "igual que el otro video".
argument-hint: <ruta-al-video> [sin cortes] [mayúsculas]
---

# video-tiktok

Script: `scripts/tiktok.py` (relativo a este archivo). Abajo, `$S` = ruta absoluta a ese script.
Archivos intermedios: `~/.cache/video-tiktok/<nombre>/` (`frame.jpg`, `transcript.json`, `subs.ass`).
Salida: `~/Downloads/<nombre>-final.mp4`.

## Requisitos (verificar una vez por sesión)

- `ffmpeg` y `ffprobe` con libass (`brew install ffmpeg`).
- `python3 -c "import faster_whisper"`; si falla: `pip install faster-whisper`.
- Opcional: fuente **Montserrat ExtraBold** instalada (si no, libass usa una sans en negrita).

## Pasos

El video es `$ARGUMENTS` (o el que haya pasado el usuario). Si dijo "sin cortes", usar `--no-cut`.
Si pidió mayúsculas, `--upper`.

1. **Espejo.** `python3 $S frame "<video>"` y mirar la imagen con Read. Está en espejo si hay
   texto invertido (carteles, remeras, logos) o elementos que se sabe que están del otro lado.
   Si no hay pistas claras, asumir que **no** está en espejo y mencionarlo. Si lo está → `--flip`.
2. **Transcribir.** `python3 $S transcribe "<video>"` (español, timestamps por palabra).
   Quita automáticamente segmentos repetidos y frases duplicadas que Whisper alucina, y agrega
   `¿`/`¡` de apertura. Modelo por defecto `large-v3-turbo`; si es lento o falla, `--model medium`.
3. **Render.** `python3 $S render "<video>" [--flip] [--no-cut] [--upper]`. Hace todo en una pasada:
   - limpieza de ruido (highpass + afftdn) y silencio en las pausas entre frases,
   - corte de pausas > 0,6 s (salvo `--no-cut`), dejando 0,15 s de margen,
   - loudnorm a **-14 LUFS** en dos pasadas (true peak -1 dB),
   - recorte/escala a **1080x1920**, subtítulos de hasta 3 palabras con la activa en amarillo.
4. **Revisión.** Mostrar al usuario la transcripción (`python3 $S text ~/.cache/video-tiktok/<nombre>/transcript.json`)
   y la ruta del video final, más cuánto se acortó. Señalar palabras dudosas (nombres propios,
   términos técnicos, signos de pregunta faltantes).
5. **Correcciones.** Si el usuario corrige algo, editar el campo `word` de las palabras en
   `transcript.json` (no tocar `start`/`end`; para borrar una palabra, quitar su objeto) y volver a
   correr solo el paso 3 con los mismos flags. No re-transcribir.

## "Lo mismo que el anterior"

Repetir los pasos con los mismos flags que se usaron en el video anterior de la conversación
(sin cortes, mayúsculas, etc.), pero siempre volviendo a revisar el espejo del video nuevo.

## Ajustes finos (`render`)

| Flag | Default | Para qué |
|---|---|---|
| `--max-pause` | 0.6 | pausas más largas se cortan |
| `--pad` | 0.15 | aire antes/después de cada frase |
| `--font` / `--font-size` | Montserrat ExtraBold / 86 | estilo del subtítulo |
| `--margin-v` | 520 | altura de los subtítulos desde abajo |
| `--out` | `~/Downloads/<nombre>-final.mp4` | otra ruta de salida |
| `--no-subs` | — | sin subtítulos |
| `--zoom "frase"` | — | primer plano (corte a zoom) mientras se dice esa frase; repetible |
| `--zoom-level` / `--zoom-y` | 1.3 / 0.42 | cuánto acerca y a qué altura está la cara (0 arriba, 1 abajo) |
| `--zoom-hold` | 0.3 | segundos extra de zoom después de la frase |
| `--music archivo` | — | música de fondo: se repite si es corta, fade in/out, baja sola cuando hay voz |
| `--music-lufs` | -30 | volumen de la música antes de mezclar (-34 más baja, -26 más alta) |

Si el usuario pide "primer plano" o "zoom cuando dice algo importante", elegir 3–5 frases clave
(el gancho, la idea central, el llamado a la acción), pasarlas con `--zoom` y decirle cuáles fueron.

Si pide música de fondo, la canción la tiene que pasar el usuario (mp3/wav/m4a); no inventarla.
Recordarle que la música con derechos puede hacer que TikTok/Instagram silencien el video, y que
los sonidos de la biblioteca de la app son la opción segura.
