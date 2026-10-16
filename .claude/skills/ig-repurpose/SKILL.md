---
name: ig-repurpose
description: Convierte un contenido largo (video, podcast o newsletter) en una semana de Reels y carruseles de Instagram que se entienden solos, sin depender del original — con los recortes y tiempos exactos si es video. Úsalo cuando pida reciclar, reutilizar o "sacar contenido" de un video largo, un podcast, un en vivo, un newsletter, un blog o una charla.
argument-hint: <archivo de video/audio, texto o link>
---

# ig-repurpose

`$I` = `../instagram/scripts/instagram.py`, `$S` = `../video-tiktok/scripts/tiktok.py` (rutas absolutas).
Ganchos: `../instagram/references/ganchos.md`. Salida: `~/Downloads/<nombre>-semana.md`.

## 1. Obtener el texto

- **Video o audio** (.mp4, .mov, .mp3, .m4a, .wav): `python3 $S transcribe "<archivo>"` →
  `~/.cache/video-tiktok/<nombre>/transcript.json` (palabras con tiempos). Leerlo con
  `python3 $S text <transcript.json>`; para tiempos exactos, leer el JSON.
- **Newsletter / blog**: el texto pegado o el archivo. Si es un link, leer la página.

## 2. Encontrar las piezas (5–7)

Buscar momentos que funcionen **solos**: una opinión fuerte, un dato, una historia con final, un paso a
paso, una pregunta del público con su respuesta, un error. Descartar lo que necesita contexto previo.

Para cada pieza:
- **Formato**: Reel (si hay un momento hablado de 15–60 s con energía) o carrusel (listas, pasos,
  comparaciones, cosas que se guardan).
- **Gancho** nuevo con una fórmula de `ganchos.md` (no el arranque original de la frase).
- **Independencia**: nada de "como dije antes", "en el episodio", "en el newsletter de hoy". Quien lo ve
  no conoce el original. Si hace falta contexto, agregarlo en el texto en pantalla.
- Video: **entrada y salida exactas** (segundos del transcript, cortando en fin de frase) y qué decir o
  mostrar en el primer segundo si el momento no arranca fuerte.

## 3. Entregable

Tabla de la semana: día · formato · pieza · gancho (fórmula) · tiempos (si es video) · llamado a la acción.
Una sola pieza termina con "el episodio/video completo está en el link de la bio", no todas.

## 4. Producir (si el usuario quiere)

- Recorte de video: `ffmpeg -ss <inicio> -to <fin> -i "<original>" -c:v libx264 -c:a aac ~/Downloads/<nombre>-parte<N>.mp4`
  y después el flujo "Editar un video grabado como Reel" de `/instagram`. Si el original es horizontal,
  avisar que el recorte vertical centra la imagen (puede cortar a quien habla si no está en el centro).
- Carruseles: `/ig-carousel` con el contenido de la pieza.
- Textos: `/ig-caption`. Plan con fechas y horarios: `/ig-plan`.
