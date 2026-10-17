---
name: ig-viral
description: Encuentra lo que funciona en el nicho del usuario — junta publicaciones de cuentas del nicho, las rankea por múltiplo sobre la mediana de cada cuenta (no por números absolutos), nombra la fórmula detrás de cada outlier y escribe un archivo de ejemplos para reusar. Úsalo cuando pida "qué funciona en mi nicho", "buscá virales", "analizá estas cuentas", "ideas que ya funcionaron" o un swipe file.
argument-hint: <nicho> [@cuenta1 @cuenta2 …]
---

# ig-viral

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Fórmulas: `../instagram/references/ganchos.md`.
Salida: `~/Downloads/ig-viral-<nicho>.md`.

**Por qué el múltiplo:** un video con 50.000 vistas en una cuenta que siempre hace 500.000 fracasó; uno
con 15.000 en una que hace 1.000 es un outlier de 15x. Se compara cada publicación con la **mediana de
su propia cuenta**, así lo que se copia es la idea, no el tamaño de la cuenta.

## 1. Elegir cuentas (8–15)

Del usuario, o proponerlas buscando en la web ("<nicho> creadores instagram", listas, menciones en
prensa). Cuentas que **no** sean gigantes (10k–500k), del mismo idioma, activas. Confirmar la lista con el
usuario antes de juntar datos; no inventar @usuarios: solo los que aparezcan en una fuente.

## 2. Juntar datos (≥ 12 publicaciones recientes por cuenta)

- **Con token de Facebook Login** (`IG_FB_ACCESS_TOKEN` e `IG_FB_USER_ID`):
  `python3 $I discover @cuenta1 @cuenta2 … --posts 25 --out ~/Downloads/ig-viral-<nicho>.csv`
  (trae likes y comentarios; Instagram no da las vistas de cuentas ajenas, se usa likes + comentarios).
- **Sin token**: pedir al usuario un CSV (lo puede armar mirando cada perfil o con una herramienta de
  exportación) con columnas `account,url,views,caption` (o `likes,comments` si no hay vistas).
  Acepta "1,2K", "15 mil", "1.234".

## 3. Rankear

`python3 $I outliers ~/Downloads/ig-viral-<nicho>.csv --min 3 --top 20 --out ~/.cache/instagram/viral.json`
Si salen menos de 5, bajar a `--min 2`. Cuentas con menos de 3 publicaciones quedan afuera.

## 4. Nombrar la fórmula de cada outlier

Para cada uno del top (abrir el link o leer el texto que haya):
- **Fórmula de gancho**: número y nombre de `ganchos.md`. Si no encaja, inventarle un nombre corto y
  descriptivo (ej. "Confesión con número") y marcarlo como fórmula nueva.
- **Formato** (Reel hablado, tutorial en pantalla, carrusel lista, POV…), **tema**, **ángulo**
  (contrario, historia, dato) y **llamado a la acción**.
- **Por qué funcionó** en una línea, sin humo (ej. "promesa concreta + número + dolor del principiante").

Agrupar: qué fórmulas se repiten entre varias cuentas (eso es patrón, no suerte).

## 5. Archivo de ejemplos

`~/Downloads/ig-viral-<nicho>.md`:
1. Resumen: las 3–5 fórmulas que más se repiten, con cuántos outliers y múltiplo promedio.
2. Por fórmula: plantilla reusable + ejemplos reales (cuenta, múltiplo, link, gancho textual).
3. **Adaptaciones para el usuario**: 2 ganchos por fórmula escritos para su tema, listos para `/ig-reel`.
4. Lo que **no** funcionó (los de menor múltiplo): qué evitar.

Mostrar el resumen en el chat y la ruta del archivo.
