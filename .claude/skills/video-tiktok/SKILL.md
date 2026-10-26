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

## Zooms y efectos de sonido (opcional)

Si el usuario pide zoom en momentos importantes o sonidos en palabras clave, escribir
`~/.cache/video-tiktok/<nombre>/fx.json` (índices = posición de la palabra en `transcript.json`)
y volver a correr el paso 3; `render` lo aplica solo si existe (`--no-fx` lo ignora):

```json
{"zooms": [{"from": 12, "to": 14, "scale": 1.2, "focus": [0.5, 0.3]}],
 "sfx":   [{"word": 12, "sound": "whoosh"}, {"word": 16, "sound": "pop"}, {"word": 43, "sound": "ding"}]}
```

- Zoom: entra suave sobre la frase y vuelve al terminar; `focus` (x, y en 0..1) es hacia dónde
  apunta (cara, pizarrón…). Después del render, sacar un fotograma a mitad de cada zoom y revisar
  que el encuadre no corte la cara; si la corta, ajustar `focus`.
- Sonidos (sintetizados, sin archivos): `whoosh` al empezar un zoom, `pop` para ítems de una
  lista, `ding` para la idea fuerte. No más de uno cada ~2 s.
- Si se borran palabras de `transcript.json`, corregir los índices de `fx.json`.

## Logo

El logo de José (JS Personal Trainer, círculo con fondo transparente) está en
`assets/logo-js.png`. Para sus videos agregar siempre `--logo <ruta al skill>/assets/logo-js.png`:
va arriba a la derecha, a 200 px, donde no lo tapan los botones de TikTok/Instagram.
Para Instagram usar `--margin-v 330` (subtítulos más abajo, pero fuera de la zona del caption).

## Título gancho (opcional, para videos "virales")

`render ... --hook "Frase corta|segunda línea" --hook-dur 3` muestra arriba, al inicio, un título
en mayúsculas (texto negro sobre caja amarilla, con un pequeño rebote). Elegir la frase más fuerte
del video (máx. ~6 palabras). Para un pedido de "video viral": `--hook`, `--trim-silence`,
zooms y sonidos en `fx.json`, `--music auto` y `--enhance`.

## Pausas más cortas (opcional)

Whisper a veces estira palabras sobre los silencios, así que algunas pausas no se ven en la
transcripción. Si el usuario pide pausas más cortas: `render ... --trim-silence --max-pause 0.3 --pad 0.12`
(corta también los silencios que detecta en el audio, a -38 dB). Después volver a transcribir el
resultado y comparar con la transcripción original para confirmar que no se comió finales de palabra;
si pasa, subir `--pad`.

## Cambiar el fondo (opcional)

`python3 scripts/replace_bg.py <video> <salida.mp4>` reemplaza el fondo por azul oscuro con un leve
degradé (segmentación de personas con `pip install "rembg[cpu]"`, ~0,3 s por cuadro). Correrlo en
segundo plano sobre el video original y después hacer el `render` de la salida con
`--transcript` y `--fx` de la carpeta del video original (mismos tiempos) y los mismos flags.

## HD (opcional)

Si el usuario pide "HD" o mejor calidad, agregar `--enhance` al render: reduce el ruido de
compresión de WhatsApp, escala con lanczos, enfoca y realza un poco el color, y codifica con
`-preset slow -crf 17`. La salida ya es 1080x1920; esto mejora la nitidez, no inventa detalle.

## Música de fondo (opcional)

`render ... --music auto` genera una base instrumental simple (Am-F-C-G, ~100 BPM);
`--music <archivo.mp3>` usa un tema del usuario (se repite si es corto). La música se normaliza a
`--music-volume` LUFS (default -27; la voz va a -14), entra y sale con fade y baja sola cuando hay
voz (sidechain). Si suena fuerte o floja, mover `--music-volume` de a 3. Recordar al usuario que
para temas con derechos conviene agregar el audio desde la app de TikTok.

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
