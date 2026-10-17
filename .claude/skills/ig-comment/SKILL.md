---
name: ig-comment
description: Escribe comentarios para dejar en publicaciones de otras cuentas de Instagram — elige entre nueve tipos según el contenido de la publicación (aporte, experiencia, pregunta, desacuerdo respetuoso, resumen, aplicación, recurso, humor, elogio específico) para sumar a la conversación y ganar visibilidad, nunca "🔥🔥🔥" ni "¡Gran post!". Úsalo cuando pida comentar en otras cuentas, interactuar con creadores del nicho o "qué le comento a este post".
argument-hint: <link, texto o captura de la publicación>
---

# ig-comment

Instagram no permite comentar publicaciones ajenas por API: Claude escribe, el usuario pega.
Si pasa una captura, mirarla con Read; si pasa un link, leer el texto que haya o pedir que lo pegue.

## Los nueve tipos

| # | Tipo | Qué hace | Ejemplo |
|---|---|---|---|
| 1 | Aporte | Suma un dato, matiz o paso que faltó | "Sumo uno: si exportás en 1080x1920 antes de subir, se ve mucho menos comprimido." |
| 2 | Experiencia | Cuenta brevemente que le pasó lo mismo y qué aprendió | "Me pasó con mi primer cliente: cobré por video y terminé editando 14 versiones." |
| 3 | Pregunta específica | Una duda real sobre un punto puntual (invita a responder) | "¿El punto 3 lo aplicás también en carruseles o solo en Reels?" |
| 4 | Desacuerdo respetuoso | Otra mirada con argumento, sin atacar | "Coincido salvo en lo de publicar diario: a mí me rindió más 3 veces por semana con mejor gancho." |
| 5 | Resumen | Destila la idea en una línea (útil para el resto) | "Para mí la clave es: primer segundo con la promesa, el resto es cumplirla." |
| 6 | Aplicación | Dice cómo lo va a usar | "Lo pruebo mañana con el video del lanzamiento y te cuento." |
| 7 | Recurso | Menciona un recurso complementario **sin link ni autopromoción** | "Para el paso 2, la función de subtítulos de CapCut lo hace sola." |
| 8 | Humor | Chiste del contexto del post, solo si el post es liviano | "La toma 17 siempre es la buena y siempre tiene a tu perro de fondo." |
| 9 | Elogio específico | Qué parte puntual le sirvió y por qué | "El ejemplo del antes y después de la bio me hizo ver que la mía no dice a quién ayudo." |

## Elegir según la publicación

- Educativa / tutorial → 1, 3, 6 (o 5 si es larga).
- Historia personal o vulnerable → 2 o 9. Nunca 4 ni 8.
- Opinión / polémica → 4 o 1.
- Humor / meme → 8 o 2.
- Logro / anuncio → 9 (mencionando el logro concreto).
- Lista de recursos → 7 o 3.

## Reglas

- Hace referencia a **algo concreto** de esa publicación: si sirve para cualquier post, no sirve.
- 1–3 oraciones. Sin links, sin "pasá por mi perfil", sin hashtags. Máximo un emoji y solo si suma.
- Registro del usuario (voseo si escribe con vos), tono de colega, no de fan.
- Nunca: "🔥🔥🔥", "¡Gran post!", "¡Excelente contenido!", "Totalmente de acuerdo", "Me encanta".

## Entregable

Para cada publicación: el tipo elegido y por qué (en media línea) + **2 opciones** de comentario de tipos
distintos. Pasarlas por `python3 ../ig-human/scripts/detect.py - [--voseo]`. Si son varias publicaciones
(ej. las 10 cuentas de `/ig-plan`), una tabla: cuenta · tipo · comentario.
