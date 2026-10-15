---
name: ig-carousel
description: Arma carruseles de Instagram que hacen deslizar — portada con gancho que obliga a pasar, texto de cada diapositiva (una idea por slide), cierre con llamado a guardar o compartir, y genera las imágenes 1080x1350. Úsalo cuando el usuario pida un carrusel, slides, "un post de varias imágenes", o convertir un tema, hilo o artículo en carrusel.
argument-hint: <tema> [cantidad de slides]
---

# ig-carousel

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Ganchos: `../instagram/references/ganchos.md`.
Salida: `~/Downloads/<tema>.json` y `~/Downloads/<tema>-carrusel/01.jpg …`.

## 1. Portada (lo más importante)

Proponer **tres portadas** de fórmulas distintas (sirven mejor: 4 lista con trampa, 21 señales, 3 dejá de,
1 error caro, 12 versus, 2 de A a B). Reglas:
- Título de ≤ 10 palabras, legible en miniatura. Un número concreto si se puede.
- Promete algo que **solo** se obtiene deslizando (la lista, el paso a paso, el final de la historia).
- Opcional: una línea chica de apoyo ("Guardalo para después", "→ deslizá").

## 2. Diapositivas

- 6–10 slides en total (máximo 10). Una idea por slide, **≤ 30 palabras**: título corto + 1–3 líneas.
- Slide 2 tiene que pagar algo de inmediato (no "introducción"); si no, se pierde a la mitad.
- Cada slide termina dejando ganas de la siguiente (lista numerada, pregunta, "pero…").
- Penúltima: resumen o el resultado. Última: llamado a la acción de **guardar o compartir** (los
  carruseles se miden por guardados y envíos) + @usuario.
- Registro del usuario; pasar todos los textos por `python3 ../ig-human/scripts/detect.py`.

## 3. Generar las imágenes

JSON en `~/Downloads/<tema>.json`:
```json
{
  "style": {"background": "#111111", "color": "#FFFFFF", "accent": "#FFD400", "handle": "@usuario"},
  "slides": [
    {"title": "Gancho de la portada", "title_size": 104},
    {"title": "1. Idea", "body": "Explicación breve."},
    {"image": "foto.jpg", "title": "Texto sobre una foto"},
    {"title": "Guardalo para tu próximo video", "body": "Y mandáselo a quien lo necesita.",
     "background": "#FFD400", "color": "#111111"}
  ]
}
```
Opcionales: `font`/`body_font` (ruta a .ttf/.otf; usar la tipografía de la marca si la hay),
`numbers: false`, y por slide `background`, `color`, `title_size`, `body_size`. Las fotos se recortan a 4:5
con degradé si llevan texto. Si el usuario tiene colores de marca, usarlos.

`python3 $I carousel ~/Downloads/<tema>.json`

## 4. Revisar

Mirar **cada** imagen con Read: texto cortado, líneas que se pisan, slides con demasiado texto (bajar
`body_size` o recortar texto), contraste. Corregir y regenerar. Mostrar la portada y la lista de rutas.

Después: texto de la publicación con `/ig-caption` y publicar con `/instagram` (necesita URLs públicas).
