---
name: ig-reel
description: Convierte una idea en un Reel promocional listo para grabar — tres ganchos de tres fórmulas distintas (de 26), música sugerida, guion, texto en pantalla y una hoja de ritmos con tiempos al segundo. Úsalo cuando el usuario pida un Reel, un guion de video, ganchos, "una idea para un video" o promocionar algo en video en Instagram.
argument-hint: <idea o producto> [duración en segundos]
---

# ig-reel

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Ganchos: `../instagram/references/ganchos.md` (leerlo).
Salida: `~/Downloads/<slug>-reel.md`.

## Antes de escribir

Si falta, preguntar en **una sola** pregunta: qué se promociona, para quién, qué acción se quiere
(comentar una palabra clave, ir al link de la bio, guardar, comprar) y si el usuario sale a cámara.
Duración por defecto: **20–35 s** (promocional). Si hay un `ig-viral-*.md` en `~/Downloads`, usar sus
fórmulas ganadoras primero.

## Qué entregar (en este orden)

1. **Tres ganchos** de tres fórmulas distintas, cada uno con: número y nombre de la fórmula, lo que se
   dice, el texto en pantalla (≤ 8 palabras) y la primera imagen. Marcar el recomendado y por qué
   (en una línea).
2. **Música**: mood, género y BPM aproximado que acompañen el ritmo de cortes (ej. "lo-fi 85 BPM,
   tranquilo" o "pop electrónico 120 BPM, enérgico"), y si conviene tema en tendencia o sonido original.
   No inventar nombres de canciones "en tendencia": indicar buscar en la biblioteca de audio de Reels
   con esos filtros. Si habla a cámara, música al 10–15 % debajo de la voz.
3. **Guion** completo palabra por palabra, en el registro del usuario (voseo si escribe con vos),
   frases de ≤ 12 palabras, una idea por frase. Sin "hola", sin presentarse.
4. **Texto en pantalla** por momento (lo que se lee sin sonido cuenta la historia completa).
5. **Hoja de ritmos** (tabla) con tiempos definidos:

   | Tiempo | Sección | Se ve | Se dice | Texto en pantalla | Corte/transición |
   |---|---|---|---|---|---|
   | 0:00–0:01 | Gancho | … | … | … | corte duro |
   | 0:01–0:04 | Promesa / contexto | … | … | … | … |
   | 0:04–0:20 | Desarrollo (un cambio visual cada 2–3 s) | … | … | … | … |
   | 0:20–0:25 | Prueba o resultado | … | … | … | … |
   | 0:25–0:30 | Llamado a la acción | … | … | … | … |

   Ajustar las filas a la duración. Cada 2–3 s cambia algo (plano, zoom, texto, b-roll).
6. **Llamado a la acción** final: uno solo. Si es palabra clave ("comentá GUIA"), avisar que
   `/ig-reply` + `/ig-dm` la entregan.
7. **Portada**: texto de la portada (≤ 5 palabras) y qué fotograma usar.
8. **Plano de grabación**: lista de tomas a grabar (A-roll y B-roll) para grabar todo de una vez.

Pasar el guion y el texto en pantalla por `python3 ../ig-human/scripts/detect.py - --voseo` (si usa vos)
y corregir lo que marque antes de mostrarlo. Guardar todo en el `.md` y mostrar un resumen.

## Después

Cuando el usuario grabe, editar con `/instagram` ("Editar un video grabado como Reel") y escribir el texto
con `/ig-caption`.
