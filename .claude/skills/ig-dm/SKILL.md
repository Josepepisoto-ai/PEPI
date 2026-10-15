---
name: ig-dm
description: Escribe los mensajes directos de Instagram — la entrega por palabra clave a quien comentó, el primer mensaje a quien escribió, la propuesta de colaboración a otra cuenta o marca, y los dos seguimientos (solo dos). Úsalo cuando pida mensajes directos, DMs, "qué le respondo por privado", entregar un recurso por palabra clave, proponer una colaboración o hacer seguimiento a alguien que no contestó.
argument-hint: <tipo: palabra clave | primer mensaje | colaboración | seguimiento> <contexto>
---

# ig-dm

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`.

**Qué se puede mandar por API:** la entrega por palabra clave (`private-reply`, respuesta privada a un
comentario, una vez por comentario y dentro de 7 días) y respuestas a quien escribió en las últimas 24 h.
**Mensajes en frío** (colaboraciones, seguimientos a quien no escribió) Instagram no los permite por
API: Claude los escribe y el usuario los manda desde la app.

## Los cinco mensajes

### 1. Entrega de palabra clave
Para quien comentó la palabra (viene de `/ig-reply`). Estructura: saludo con nombre → **el recurso
prometido** (link o contenido, sin vueltas) → una pregunta corta que abra conversación y califique
("¿Lo vas a usar para tu negocio o para tu cuenta personal?"). Máx. 3 líneas.
Enviar: `python3 $I private-reply <comment_id> "<mensaje>" --yes`, tras aprobación.

### 2. Primer mensaje (a quien escribió primero)
Respuesta a historia, caja de preguntas o DM espontáneo. Responder **lo que dijo** (no un guion) →
aportar algo útil → una pregunta para entender qué busca. Nada de vender en el primer mensaje salvo
que haya preguntado precio.

### 3. Propuesta de colaboración
A otra cuenta o marca. Estructura en ≤ 6 líneas:
- Algo **específico** de su contenido (prueba de que lo mirás de verdad).
- Quién sos en una línea, con un número si suma (audiencia, resultado).
- La idea concreta (formato, tema, fecha aproximada) y **qué gana su audiencia**.
- Pedido chico y fácil de responder ("¿Te interesa que te mande un guion de 3 líneas?").
Sin "espero que estés bien", sin adjuntos, sin pedir favores grandes en el primer mensaje.

### 4. Seguimiento 1 (3–4 días después, sin respuesta)
Una línea que suma algo nuevo (un dato, una idea extra, un ejemplo), no "¿lo viste?".

### 5. Seguimiento 2 (7 días después del 1, el último)
Corto, sin culpa, con salida fácil: "Te dejo tranquilo/a. Si en algún momento te sirve, acá estoy."
**Después de este, no se manda nada más.** Dos seguimientos, nunca tres.

## Reglas

- Escribir como persona a persona: tono del usuario, sin plantillas evidentes ni mayúsculas de marketing.
- Personalizar con algo real del otro (su comentario, su último post); si no hay datos, pedirlos.
- Pasar por `python3 ../ig-human/scripts/detect.py - [--voseo]` antes de mostrar.
- Nunca mandar nada sin aprobación del texto exacto.

Entregar cada mensaje listo para copiar y, para los seguimientos, la fecha sugerida de envío.
