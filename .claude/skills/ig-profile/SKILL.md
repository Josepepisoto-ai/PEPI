---
name: ig-profile
description: Evalúa el perfil de Instagram del usuario con una rúbrica de 12 partes sobre 100 puntos (foto, nombre buscable, bio, prueba, llamado a la acción, link, destacadas, fijados, grilla…) y lo reescribe en orden de corrección, de lo que más puntos recupera con menos esfuerzo a lo que menos. Úsalo cuando pida revisar, auditar, optimizar o reescribir su perfil o su bio.
argument-hint: [@usuario o captura del perfil]
---

# ig-profile

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Salida: `~/Downloads/ig-perfil-<fecha>.md`.

## Datos

- Con token: `python3 $I profile` (nombre, usuario, bio, web, seguidores, publicaciones).
- Siempre pedir **una captura del perfil** completo (foto, bio, destacadas, primeras 9 publicaciones) y
  mirarla con Read: la API no da destacadas, fijados ni cómo se ve la grilla.
- Preguntar si no está claro: qué ofrece, a quién, y cuál es la única acción que quiere que haga un visitante.

## Rúbrica (100 puntos)

| # | Parte | Pts | 100 % cuando… |
|---|---|---|---|
| 1 | Foto | 6 | Cara (o logo si es marca) clara a tamaño miniatura, fondo con contraste |
| 2 | Nombre (campo buscable) | 10 | Incluye la palabra que su cliente buscaría ("Pepi · Edición de video") |
| 3 | @usuario | 5 | Corto, fácil de dictar, sin números ni guiones raros, igual en otras redes |
| 4 | Bio línea 1: qué y para quién | 12 | Se entiende en 3 s qué hace y para quién |
| 5 | Prueba / credibilidad | 8 | Un número o logro concreto (clientes, años, resultados, medios) |
| 6 | Personalidad / diferencial | 6 | Algo propio que lo distingue de 100 cuentas iguales |
| 7 | Llamado a la acción | 10 | Una acción clara apuntando al link o a una palabra clave por DM |
| 8 | Link | 8 | Un destino claro (no 12 botones), carga rápido en el celular |
| 9 | Destacadas | 10 | 3–5, portadas coherentes, la primera es "Empezá acá"/"Quién soy", ninguna vieja o vacía |
| 10 | Publicaciones fijadas | 10 | 3 fijadas con función: la que mejor funcionó, quién soy, la oferta |
| 11 | Grilla (primeras 9) | 10 | Temas coherentes con la bio, portadas con texto legible |
| 12 | Categoría, contacto y botones | 5 | Categoría correcta, botones de contacto/acción útiles y activos |

Puntaje parcial permitido (ej. 6/12). Justificar cada nota en una línea con lo que se ve.

## Reescritura en orden de corrección

Ordenar las partes por **puntos perdidos ÷ esfuerzo** (nombre, bio, llamado a la acción y link son de 5
minutos; destacadas y grilla llevan horas). Para cada una, en ese orden:
- Qué está mal (concreto) → versión nueva lista para copiar.
- Bio: **máx. 150 caracteres** contando saltos de línea; dar 2–3 opciones. Nombre: máx. 64 caracteres
  (Instagram permite cambiarlo 2 veces cada 14 días: avisar).
- Destacadas: lista con nombre (≤ 15 caracteres) y qué historias meter en cada una.
- Fijados: cuáles publicaciones fijar (si hay datos, usar `/ig-audit`) o qué crear.

Pasar la bio por `../ig-human/scripts/detect.py`. Mostrar: puntaje actual → puntaje estimado después,
tabla de la rúbrica y la lista de cambios ordenada. Guardar el `.md`.
