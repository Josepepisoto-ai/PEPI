---
name: ig-plan
description: Arma la semana de Instagram — qué publicar cada día, en qué formato (Reel, carrusel, foto, historias), a qué hora, con qué gancho y llamado a la acción, y las 10 cuentas con las que interactuar esa semana. Úsalo cuando pida un plan, calendario o cronograma de contenido, "qué publico esta semana" o una estrategia semanal.
argument-hint: [objetivo de la semana] [cuántas publicaciones]
---

# ig-plan

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Salida: `~/Downloads/ig-plan-<lunes AAAA-MM-DD>.md`.

## Insumos (usar lo que exista, preguntar lo mínimo)

- Objetivo de la semana (seguidores, leads por DM, ventas de algo concreto, lanzamiento).
- Capacidad real: cuántas publicaciones puede hacer (por defecto **4–5 + historias diarias**).
- `~/.cache/instagram/audit.json` (de `/ig-audit`): formatos, temas y días/horas que mejor le fueron.
- `~/Downloads/ig-viral-*.md` (de `/ig-viral`): fórmulas que funcionan en su nicho.
- Sin datos de horario: proponer franjas habituales (12–14 h y 19–22 h de su zona) y aclarar que se
  ajustan con `/ig-audit` en 3–4 semanas.

## Reglas del plan

- Mezcla de formatos: mayoría Reels (alcance a gente nueva), 1–2 carruseles (guardados y envíos),
  historias todos los días (relación con quien ya sigue).
- Pilares: ~40 % educar, ~25 % entretener/identificarse, ~20 % historia o detrás de escena,
  ~15 % vender. Nunca dos piezas de venta seguidas.
- Cada pieza con fórmula de gancho distinta; ninguna repetida en la semana.
- Una sola palabra clave de DM activa por semana (para que `/ig-reply` y `/ig-dm` sean simples).
- Grabación en bloque: agrupar todo lo que se graba en el mismo lugar.

## Entregable

1. Tabla: día · hora · formato · pilar · idea · gancho (fórmula) · llamado a la acción · skill para
   producirla (`/ig-reel`, `/ig-carousel`, `/ig-story`).
2. Lista de grabación agrupada.
3. **10 cuentas para interactuar** esta semana: del mismo nicho y tamaño parecido o algo mayor
   (comentar ahí es alcance gratis ante el público correcto). Fuente: las del usuario, las de
   `ig-viral` o búsqueda web; nunca @usuarios inventados, marcar "verificar" si no se confirmó.
   Para cada una: por qué (en una línea) y qué tipo de comentario dejar (`/ig-comment`), 2–3 por semana
   cada una, en los primeros 30–60 min de sus publicaciones si se puede.
4. Rutina diaria de 20 min: responder comentarios (`/ig-reply`), DMs (`/ig-dm`), comentar en 3–5 cuentas.

Al terminar, ofrecer producir la primera pieza y, si hay token, programar con `/instagram`.
