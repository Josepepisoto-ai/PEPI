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

## Skills de Instagram

`/instagram` es el menú central. Además conecta la cuenta, edita un video grabado como Reel y publica o
programa. Las 13 skills `/ig-*` comparten su script (`.claude/skills/instagram/scripts/instagram.py`).

| Skill | Qué hace |
|---|---|
| `/ig-reel` | Convierte una idea en un video promocional: tres ganchos de las 26 fórmulas, música, guion, texto en pantalla y una hoja de ritmos con tiempos |
| `/ig-viral` | Busca lo que funciona en tu nicho, lo rankea por cuántas veces supera la mediana de cada cuenta, nombra la fórmula y escribe el archivo de ejemplos |
| `/ig-caption` | Escribe y controla el texto de la publicación; muestra los ~125 caracteres que se ven en el feed antes de tocar nada |
| `/ig-carousel` | Arma el carrusel: portada que hace deslizar, texto de cada slide y las imágenes 1080x1350 |
| `/ig-story` | Planifica las historias del día, qué sticker cumple qué función y el embudo a DM donde el seguidor escribe primero |
| `/ig-profile` | Evalúa tu perfil con una rúbrica de 12 partes sobre 100 y lo reescribe en orden de corrección |
| `/ig-plan` | Arma la semana: qué publicar, en qué formato y cuándo, y las 10 cuentas con las que interactuar |
| `/ig-human` | Humanizador con dos scripts: `detect.py` (puntaje de 0 a 100 con las marcas de IA) y `fix.py` (arreglos seguros, también pasa el tuteo a vos) |
| `/ig-comment` | Comentarios para publicaciones de otras cuentas: nueve tipos, elegidos según el contenido. Nunca "🔥🔥🔥" |
| `/ig-reply` | Responde los comentarios de tus publicaciones: los clasifica en palabra clave, presentación, contenido, pregunta, soporte o ruido, y los responde en ese orden |
| `/ig-dm` | Mensajes directos: entrega por palabra clave, primer mensaje, propuesta de colaboración y dos seguimientos (solo dos) |
| `/ig-repurpose` | Convierte un video, podcast o newsletter en una semana de Reels y carruseles que se entienden solos |
| `/ig-audit` | Analiza lo que ya publicaste: rankea por múltiplo de alcance y por envíos cada mil de alcance, no por vistas |

Para usarlas en cualquier sesión, copiá todas las skills:

```bash
cp -R .claude/skills/* ~/.claude/skills/
pip install pillow faster-whisper
```

Las skills que escriben funcionan sin conectar nada. Para publicar, leer métricas o responder comentarios
hace falta una cuenta profesional y un token en `IG_ACCESS_TOKEN` (los pasos están en `/instagram`).
Nada se publica ni se manda sin que lo apruebes.
