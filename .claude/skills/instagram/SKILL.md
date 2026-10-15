---
name: instagram
description: Menú central de las skills de Instagram en español y la base que comparten — conectar la cuenta, editar un video grabado como Reel (vertical, subtítulos, audio a -14 LUFS, reusando video-tiktok), y publicar o programar con la API de Instagram. Úsalo cuando el usuario diga "Instagram", "Insta", "subilo", "publicalo", "programalo", "conectá mi cuenta" o pase un video para Reels; para tareas específicas derivá al /ig-* que corresponda.
argument-hint: [editar <video> | publicar | programar <fecha> | conectar]
---

# instagram

Script compartido: `scripts/instagram.py` (relativo a este archivo). En todas las skills `/ig-*`,
`$I` = ruta absoluta a ese script y `$S` = ruta absoluta a `../video-tiktok/scripts/tiktok.py`.
Ganchos: `references/ganchos.md`. Salidas en `~/Downloads/`.

## Qué skill usar

| Pedido | Skill |
|---|---|
| Idea → guion de Reel con ganchos, música, texto en pantalla y tiempos | `/ig-reel` |
| Qué funciona en mi nicho / buscar virales / armar archivo de ejemplos | `/ig-viral` |
| Escribir o revisar el texto de una publicación | `/ig-caption` |
| Carrusel (portada, textos, imágenes 1080x1350) | `/ig-carousel` |
| Historias del día, stickers, embudo a DM | `/ig-story` |
| Revisar y reescribir el perfil (bio, destacadas, fijados) | `/ig-profile` |
| Plan de la semana y cuentas para interactuar | `/ig-plan` |
| Que un texto no suene a IA | `/ig-human` |
| Comentar publicaciones de otros | `/ig-comment` |
| Responder los comentarios de mis publicaciones | `/ig-reply` |
| Mensajes directos: palabra clave, primer mensaje, colaboración, seguimientos | `/ig-dm` |
| Convertir un video, podcast o newsletter en una semana de contenido | `/ig-repurpose` |
| Analizar lo que ya publiqué | `/ig-audit` |
| Editar un video grabado, publicar o programar | esta skill (abajo) |

Todo texto que vaya a publicarse pasa por `/ig-human` (`detect.py`) antes de mostrarlo como final.

## Conectar la cuenta (una vez)

Hace falta una cuenta **profesional** (creador o empresa) y un token de "Instagram API with Instagram
Login" (developers.facebook.com → crear app → caso de uso Instagram → generar token) con los permisos
`instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_comments`,
`instagram_business_manage_insights` e `instagram_business_manage_messages`.
El usuario lo exporta como `IG_ACCESS_TOKEN` o lo guarda en `~/.config/instagram-skill/token`.
**Nunca pedir que pegue el token en el chat.** Verificar con `python3 $I whoami` (guarda el `IG_USER_ID`).
El token dura 60 días. Sin token igual funcionan todas las skills de escritura; solo no se publica
ni se leen métricas o comentarios automáticamente.

## Editar un video grabado como Reel

1. Pasos 1 y 2 de **video-tiktok** (espejo y transcripción), con los mismos criterios y flags.
2. Render con la zona segura de Reels (la interfaz tapa más abajo que en TikTok):
   `python3 $S render "<video>" [--flip] [--no-cut] [--upper] --margin-v 620 --out ~/Downloads/<nombre>-reels.mp4`
3. `python3 $I check-video ~/Downloads/<nombre>-reels.mp4`. Si falla, corregir y volver a renderizar.
4. Mostrar la transcripción, señalar palabras dudosas; las correcciones van a `transcript.json` y se
   repite solo el render. Ofrecer `/ig-caption` para el texto.

## Publicar o programar

**Contenido.** Reel: `--video <archivo local>` (se sube directo) o `--video-url`. Imagen y carrusel:
la API solo acepta **URLs públicas** de JPEG (`--image-url`, una por imagen, en orden). Si son locales,
pedir al usuario un link directo (su web, un bucket) o que las publique desde la app. No subirlas a
servicios de terceros sin que lo pida.

**Siempre** mostrar antes el resumen (tipo, archivos, texto completo, fecha) y esperar confirmación
explícita. Probar primero con `--dry-run`.

- Ahora: `python3 $I publish --type reel --video ~/Downloads/<nombre>-reels.mp4 --caption-file ~/Downloads/<nombre>-texto.txt --yes`
- Programar: `python3 $I schedule --type … --caption-file … --at "AAAA-MM-DD HH:MM"` (hora local).
  La API no programa sola: `publish-due` publica lo vencido. Para que corra solo, sugerir un cron en la
  máquina del usuario (que tiene que estar prendida):
  `*/15 * * * * IG_ACCESS_TOKEN=… python3 $I publish-due >> ~/.cache/instagram/cron.log 2>&1`
- Ver o quitar programadas: `python3 $I queue` / `python3 $I queue --remove <id>`.

## Referencia de comandos de `$I`

`check-video` · `caption` · `carousel` · `whoami` · `profile` · `publish` · `schedule` · `queue` ·
`publish-due` · `comments` · `reply` · `private-reply` · `audit` · `outliers` · `discover`.
`python3 $I <comando> -h` muestra las opciones. Los que publican o mandan algo exigen `--yes`,
que solo se pasa después de que el usuario aprobó ese contenido exacto.
