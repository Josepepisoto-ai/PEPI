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

## Proyecto Remotion `mi-video/`

Proyecto [Remotion](https://www.remotion.dev) (plantilla Blank + TailwindCSS) para crear
videos con código pidiéndoselos a Claude. Las Skills oficiales de Remotion están en
`.claude/skills/remotion-*`.

```bash
cd mi-video
npm install
npm run dev            # abre Remotion Studio en el navegador
npx remotion render    # exporta el MP4 a out/
```

Para usar tus propios videos o imágenes, ponelos en `mi-video/public/` y decile a Claude la ruta.
