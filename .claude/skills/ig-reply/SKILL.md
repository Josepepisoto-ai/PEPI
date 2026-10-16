---
name: ig-reply
description: Responde los comentarios debajo de las publicaciones del usuario — los trae por API, los clasifica en palabra clave, presentación, contenido, pregunta, soporte o ruido, y escribe las respuestas en ese orden de prioridad (las palabras clave primero, con el DM de entrega). Úsalo cuando pida responder comentarios, "contestá las preguntas", "qué me comentaron" o atender a la comunidad.
argument-hint: [días hacia atrás] [palabra clave activa]
---

# ig-reply

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Necesita token (ver `/instagram`); sin token,
el usuario pega los comentarios y se responde igual (él publica).

## 1. Traer

`python3 $I comments [--days 7] [--posts 10]` → JSON con `comment_id`, usuario, texto, link y texto de la
publicación. Preguntar la palabra clave activa si no se sabe (puede estar en el texto de la publicación:
"comentá GUIA").

## 2. Clasificar (y responder en este orden)

| Orden | Clase | Cómo se reconoce | Qué hacer |
|---|---|---|---|
| 1 | **Palabra clave** | Contiene la palabra pedida (aunque esté mal escrita o en minúscula) | DM de entrega con `private-reply` (`/ig-dm`) + respuesta pública corta ("¡Te lo mandé por DM!") |
| 2 | **Pregunta** | Pregunta sobre el tema, precio, cómo, dónde | Responder de verdad en público (le sirve a todos). Si es sobre precio o datos personales: invitar a DM |
| 3 | **Soporte** | Problema con un pedido, producto o servicio | Empatía + pasar a DM con un dato concreto ("mandame tu número de pedido por DM"). Nunca discutir en público |
| 4 | **Contenido** | Opina, suma, discute o cuenta su experiencia | Seguir la conversación: una repregunta o un aporte; es lo que más alarga el hilo |
| 5 | **Presentación** | Se presenta o es su primer comentario ("¡Hola! Te sigo desde hoy") | Bienvenida con su nombre y una pregunta sobre qué busca |
| 6 | **Ruido** | Emojis sueltos, "🔥", spam, bots, ofensas | Emojis: respuesta mínima opcional o nada. Spam/ofensas: no responder; sugerir ocultar o borrar desde la app |

## 3. Escribir

- Corta (1–2 oraciones), con el nombre o @ cuando suma, en el tono del usuario.
- Respuestas distintas entre sí: nunca la misma frase copiada en 20 comentarios.
- Usar `post_caption` para responder con contexto. Si no se sabe algo (precio, fecha, stock), **no
  inventar**: marcarlo como "COMPLETAR" para que lo llene el usuario.
- Terminar con pregunta solo cuando invita a seguir de verdad.
- Pasar todas por `python3 ../ig-human/scripts/detect.py - [--voseo]`.

## 4. Aprobar y publicar

Mostrar una tabla por clase: `@usuario · comentario · respuesta propuesta (· DM si es palabra clave)`.
Solo con aprobación explícita, una por una:
- `python3 $I reply <comment_id> "<respuesta>" --yes`
- `python3 $I private-reply <comment_id> "<mensaje>" --yes` (solo para palabra clave; una vez por
  comentario y dentro de los 7 días del comentario).

Al final: cuántas respondidas por clase y las que quedaron para el usuario (COMPLETAR, soporte, spam).
