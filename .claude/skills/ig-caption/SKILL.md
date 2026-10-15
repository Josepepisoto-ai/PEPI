---
name: ig-caption
description: Escribe y revisa el texto (pie de foto) de una publicación de Instagram con un control automático — muestra exactamente los ~125 caracteres que el feed enseña antes de "más", y marca links no clickeables, hashtags de más, falta de llamado a la acción y marcas de IA. Úsalo cuando el usuario pida el texto, copy, caption, descripción o hashtags de un Reel, carrusel o foto, o quiera revisar uno que ya escribió.
argument-hint: <tema, transcripción o archivo de texto>
---

# ig-caption

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Humanizador: `../ig-human/scripts/`.
Salida: `~/Downloads/<nombre>-texto.txt`.

## Si el usuario trae un texto

1. Guardarlo y correr `python3 $I caption <archivo>` **antes de tocar nada**. Mostrarle el recuadro con lo
   que se ve en el feed: es lo que decide si alguien toca "más".
2. Explicar los ✗ (bloquean: largo, más de 5 hashtags, repetidos) y los ⚠ (estilo).
3. Proponer la versión corregida y volver a correr el control.

## Si hay que escribirlo

Basarse en la transcripción del Reel, el contenido del carrusel o el tema. Registro del usuario
(voseo si escribe con vos). Estructura:

1. **Gancho** (primera línea, < 125 caracteres, sin # ni @ ni emoji al inicio). No repetir el gancho del
   video palabra por palabra: complementarlo (el video promete, el texto profundiza o da contexto).
2. **Cuerpo**: párrafos de 1–2 líneas con un salto entre ellos. Valor concreto: el paso, el dato, la
   historia. Lo que el video no llegó a decir.
3. **Llamado a la acción**: uno solo y específico ("Comentá GUIA y te la mando", "Guardalo para tu
   próxima edición", "Mandáselo a quien siempre graba vertical"). Las preguntas abiertas funcionan si
   son fáciles de contestar.
4. **Hashtags**: hasta 5, al final: 2–3 del tema exacto, 1–2 del nicho. Nada de #love #instagood #viral.
5. Palabras clave del tema escritas naturalmente en el texto (el buscador de Instagram las lee).

Sin links en el texto (no son clickeables): "link en la bio" o palabra clave por DM.

## Control final

1. `python3 ../ig-human/scripts/fix.py <archivo> [--voseo] --in-place`
2. `python3 ../ig-human/scripts/detect.py <archivo> [--voseo]` → reescribir lo que marque hasta ≥ 85.
3. `python3 $I caption <archivo>` → sin ✗; resolver los ⚠ o justificar.

Mostrar el recuadro del feed, el texto completo y, si se pide, 2–3 ganchos alternativos.
Para publicar: `/instagram`.
