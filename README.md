# PEPI

## Skill `/video-tiktok`

Convierte un video hablado en español en un video vertical 1080x1920 para TikTok:
corrige espejo, transcribe (Whisper, sin duplicados), limpia el audio a -14 LUFS,
corta pausas y quema subtítulos con la palabra activa en amarillo.

Dentro de este repo ya está disponible en `.claude/skills/video-tiktok/`. Para usarlo en
**cualquier** sesión de Claude Code, copialo a tus skills personales:

```bash
mkdir -p ~/.claude/skills && cp -R .claude/skills/video-tiktok ~/.claude/skills/
brew install ffmpeg            # si no lo tenés
pip install faster-whisper
```

Uso:

```
/video-tiktok ~/Downloads/otro-video.mp4
/video-tiktok ~/Downloads/otro-video.mp4 sin cortes
```

O pasale un video a Claude y decile "hacé lo mismo que el anterior".
El resultado queda en `~/Downloads/<nombre>-final.mp4`.

## Skill `/instagram`

Prepara y publica contenido de Instagram en español:

- **Reel**: edita el video con `video-tiktok`, con los subtítulos más arriba para la interfaz de Reels, y verifica que cumpla los requisitos.
- **Texto**: gancho, llamado a la acción y hasta 5 hashtags, validado.
- **Carrusel**: genera las imágenes 1080x1350 a partir de un JSON (texto o fotos).
- **Publicar o programar** con la API de Instagram (cuenta profesional y token en `IG_ACCESS_TOKEN`).
- **Comentarios**: lista las preguntas sin responder, propone respuestas y las publica cuando las aprobás.

Para usarla en cualquier sesión, copiá las dos skills (Reels usa `video-tiktok`):

```bash
cp -R .claude/skills/instagram .claude/skills/video-tiktok ~/.claude/skills/
pip install pillow
```

Uso:

```
/instagram reel ~/Downloads/video.mp4
/instagram carrusel 5 errores que arruinan tus Reels
/instagram comentarios
```

Nada se publica ni se responde sin que lo confirmes.
