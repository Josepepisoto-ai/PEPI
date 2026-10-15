---
name: ig-story
description: Planifica las historias de Instagram del día — la secuencia de 4 a 7 historias, qué sticker cumple qué función (encuesta, quiz, slider, caja de preguntas, link, cuenta regresiva) y el embudo a mensajes directos donde el seguidor escribe primero. Úsalo cuando el usuario pida historias, stories, "qué subo hoy a historias", stickers, o vender/captar por DM desde historias.
argument-hint: <objetivo del día o tema> [producto/oferta]
---

# ig-story

Salida: `~/Downloads/historias-<fecha>.md`. Las historias se suben y los stickers se agregan desde la
app: la API de Instagram no publica stickers interactivos.

## Qué sticker cumple qué función

| Sticker | Función | Cuándo |
|---|---|---|
| Encuesta (2 opciones) | Interacción de un toque: calienta la secuencia y le avisa al algoritmo | Historia 2 o 3, siempre fácil de contestar |
| Slider de emoji | Medir intensidad ("¿cuánto te pasa?") | Para validar un dolor antes de ofrecer algo |
| Quiz | Educar y corregir un mito | Contenido de valor |
| Caja de preguntas | Materia prima para contenido y **abre DMs** (podés responder por privado) | Cerca del final |
| Link | Tráfico afuera (la gente se va: va **última**) | Solo con un destino claro |
| Cuenta regresiva | Lanzamientos, en vivo, cierres de inscripción | Días previos a una fecha |
| Mención / colab | Alcance cruzado | Cuando hay otra cuenta involucrada |
| "Agregá la tuya" | Contenido de la comunidad | Retos, temas ligeros |

## La secuencia del día (4–7 historias)

1. **Gancho**: qué pasa hoy / pregunta / escena en movimiento. Texto ≤ 10 palabras.
2. **Contexto o valor**: el dato, el detrás de escena, el aprendizaje.
3. **Interacción fácil**: encuesta o slider (un toque).
4. **Desarrollo**: respuesta a la encuesta, ejemplo, prueba social (captura de un mensaje con permiso).
5. **Puente a DM**: "Respondé esta historia con PALABRA y te mando X" o caja de preguntas.
6. (opcional) **Link** o recordatorio de la oferta.

Regla: una idea por historia, texto en la zona segura (ni los 250 px de arriba ni los 340 de abajo),
caras y movimiento le ganan a placas de texto. No más de 2 historias seguidas solo de texto.

## Embudo a DM (el seguidor escribe primero)

El objetivo es que **ellos** manden el primer mensaje: así la conversación es legítima, Instagram
permite responder (también por API dentro de las 24 h) y el lead ya mostró interés.

1. Historia con disparador: palabra clave para responder, caja de preguntas o slider.
2. Responden → conversación abierta.
3. Respuesta con `/ig-dm` (entrega de palabra clave y primer mensaje), calificar con una pregunta.
4. Si hay interés, oferta o link. Si no responde, los dos seguimientos de `/ig-dm`.

## Entregable

Tabla por historia: número · tipo (video/foto/texto) · se ve · texto en pantalla · sticker y su opción
exacta · objetivo. Al final: palabra clave del día y el mensaje que se manda al que la escriba
(derivar a `/ig-dm`). Pasar los textos por `../ig-human/scripts/detect.py`.
Si piden la semana, variar: no repetir la misma encuesta ni la misma palabra clave dos días seguidos.
