---
name: instagram
description: Prepara y publica contenido de Instagram en español — edita videos como Reels (vertical, subtítulos, audio a -14 LUFS, reusando video-tiktok), escribe el texto con hashtags, genera carruseles 1080x1350, publica o programa con la API de Instagram y responde las preguntas de los comentarios. Úsalo cuando el usuario hable de Instagram, Reels, carrusel, "subilo a Insta", "programalo", "escribí el copy" o "respondé los comentarios".
argument-hint: reel <video> | texto <tema> | carrusel <tema> | publicar | programar <fecha> | comentarios
---

# instagram

Script: `scripts/instagram.py` (relativo a este archivo). Abajo, `$I` = ruta absoluta a ese script y
`$S` = ruta absoluta a `../video-tiktok/scripts/tiktok.py` (la skill hermana que edita el video).
Salidas en `~/Downloads/`; cola de programadas en `~/.config/instagram-skill/queue.json`.

Elegir el flujo según `$ARGUMENTS` o lo que pida el usuario. Se pueden encadenar: reel → texto → publicar.

## 1. Reel

1. Seguir los pasos 1 y 2 de la skill **video-tiktok** (espejo y transcripción), con los mismos
   criterios y flags ("sin cortes", mayúsculas).
2. Render con la zona segura de Reels (la interfaz de Instagram tapa más abajo que TikTok):
   `python3 $S render "<video>" [--flip] [--no-cut] [--upper] --margin-v 620 --out ~/Downloads/<nombre>-reels.mp4`
3. `python3 $I check-video ~/Downloads/<nombre>-reels.mp4`. Si falla, corregir y volver a renderizar.
4. Mostrar la transcripción y señalar palabras dudosas, igual que en video-tiktok. Las correcciones
   se hacen en `transcript.json` y se repite solo el render.

## 2. Texto y hashtags

Escribir el texto en el español del usuario (rioplatense si escribe con "vos"), basado en la
transcripción del Reel o en el tema que dé:

- **Primera línea gancho** de menos de 125 caracteres (es lo único que se ve sin tocar "más").
- Cuerpo corto en párrafos de 1–2 líneas, con valor concreto. Sin relleno ni emojis en cada frase.
- **Llamado a la acción** que invite a comentar (una pregunta), guardar o compartir.
- **Hasta 5 hashtags** al final (es el límite de Instagram): 2–3 específicos del tema y 1–2 de nicho.
  Nada de hashtags genéricos tipo #love o #instagood.

Guardar en `~/Downloads/<nombre>-texto.txt`, validar con `python3 $I caption <archivo>` y mostrárselo
al usuario. Si pide variantes, ofrecer 2–3 ganchos alternativos.

## 3. Carrusel

1. Escribir el contenido: slide 1 = gancho (título grande), slides del medio = una idea por slide
   (título + 1–3 líneas), último = resumen + llamado a la acción. Máximo 10 slides.
2. Guardar el JSON en `~/Downloads/<tema>.json`:
   ```json
   {
     "style": {"background": "#111111", "color": "#FFFFFF", "accent": "#FFD400", "handle": "@usuario"},
     "slides": [
       {"title": "Gancho de la portada"},
       {"title": "Idea 1", "body": "Explicación breve."},
       {"image": "foto.jpg", "title": "Texto sobre una foto"}
     ]
   }
   ```
   Opcionales: `font`/`body_font` (ruta a .ttf/.otf), `numbers: false`, y por slide `background`,
   `color`, `title_size`, `body_size`. Las imágenes se recortan a 4:5 y llevan degradé si tienen texto.
3. `python3 $I carousel ~/Downloads/<tema>.json` → `~/Downloads/<tema>-carrusel/01.jpg …`.
4. Mirar las imágenes con Read para revisar que el texto no se corte ni se pise, y ajustar.
5. Escribir el texto de la publicación como en la sección 2.

## 4. Publicar o programar

**Conectar la cuenta (una vez).** Hace falta una cuenta de Instagram **profesional** (creador o empresa)
y un token de "Instagram API with Instagram Login" con permisos `instagram_business_basic`,
`instagram_business_content_publish` e `instagram_business_manage_comments` (se crea una app en
developers.facebook.com → caso de uso Instagram → generar token). El usuario lo exporta como
`IG_ACCESS_TOKEN` o lo guarda en `~/.config/instagram-skill/token`. Nunca pedir que pegue el token
en el chat. Verificar con `python3 $I whoami` (guarda el `IG_USER_ID`). El token dura 60 días.

**Contenido.**
- Reel: `--video <archivo local>` (se sube directo) o `--video-url <URL pública>`.
- Imagen y carrusel: la API solo acepta **URLs públicas** de JPEG (`--image-url`, una por imagen,
  en orden). Si las imágenes son locales, pedir al usuario que las suba a algún lado con link directo
  (su web, un bucket) o que las publique desde la app. No subirlas a servicios de terceros sin que lo pida.

**Siempre** mostrar antes el resumen (tipo, archivos, texto completo, fecha) y esperar confirmación
explícita del usuario. Probar primero con `--dry-run`.

- Ahora: `python3 $I publish --type reel --video ~/Downloads/<nombre>-reels.mp4 --caption-file ~/Downloads/<nombre>-texto.txt --yes`
- Programar: mismo comando con `schedule --at "AAAA-MM-DD HH:MM"` (hora local) en vez de `publish … --yes`.
  La API de Instagram no programa por su cuenta: `publish-due` publica lo vencido. Para que corra solo,
  sugerir al usuario un cron en su máquina (que tiene que estar prendida):
  `*/15 * * * * IG_ACCESS_TOKEN=… python3 $I publish-due >> ~/.cache/instagram/cron.log 2>&1`.
- Ver o quitar programadas: `python3 $I queue` / `python3 $I queue --remove <id>`.

## 5. Responder las preguntas de los comentarios

1. `python3 $I comments [--days 7]` → lista los comentarios sin respuesta de la cuenta.
2. Clasificar: **preguntas** (responder), elogios (agradecer breve, opcional), spam u ofensas (no
   responder; sugerir ocultarlos desde la app).
3. Redactar cada respuesta en el tono del usuario: corta, cálida, que responda de verdad usando el
   contexto de la publicación (`post_caption`). Si no se sabe la respuesta (precios, fechas, datos
   personales), no inventar: marcarla para que la complete el usuario.
4. Mostrar una tabla `@usuario · comentario · respuesta propuesta` y pedir aprobación. Solo después:
   `python3 $I reply <comment_id> "<respuesta>" --yes`, una por comentario aprobado.

Los mensajes directos (DMs) no están cubiertos: requieren otro permiso y revisión de Meta.
