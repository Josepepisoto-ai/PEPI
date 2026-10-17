---
name: ig-audit
description: Analiza lo que el usuario ya publicó en Instagram — rankea cada publicación por múltiplo de alcance sobre su propia mediana y por envíos (compartidos) cada mil de alcance, no por vistas, y saca qué repetir, qué dejar y qué probar. Úsalo cuando pida analizar sus publicaciones, métricas, estadísticas, "qué me funcionó", "por qué no crezco" o un informe de resultados.
argument-hint: [cantidad de publicaciones]
---

# ig-audit

`$I` = ruta absoluta a `../instagram/scripts/instagram.py`. Salida: `~/Downloads/ig-audit-<fecha>.md`.

**Por qué así:** las vistas cuentan repeticiones y suben solas en los Reels; el **alcance** cuenta
personas. Comparar con la **mediana propia** muestra qué funcionó *para esta cuenta* sin que una
publicación gigante distorsione el promedio. Y los **envíos** (compartir por DM) son la señal más fuerte
de que algo vale: alguien lo eligió para mandárselo a otra persona.

## 1. Datos

- Con token: `python3 $I audit --posts 30` → tabla y `~/.cache/instagram/audit.json` con alcance, vistas,
  guardados, envíos, `multiple` (alcance ÷ mediana) y `sends_per_1k` / `saves_per_1k`.
- Sin token: pedir la exportación de métricas (Panel profesional o Meta Business Suite → Contenido →
  exportar CSV) y correr `python3 $I outliers <csv> --metric reach --min 0 --top 50`. Calcular envíos/1000
  con las columnas de compartidos y alcance.
- Menos de 10 publicaciones: avisar que las conclusiones son débiles.

## 2. Análisis

1. **Ganadoras por alcance**: múltiplo ≥ 2x. **Perdedoras**: ≤ 0,5x.
2. **Ranking por envíos/1000 de alcance**: el top 5 es el contenido que más vale aunque no sea el de más
   alcance. Igual con guardados/1000 para carruseles.
3. Para cada ganadora y perdedora, etiquetar: formato, tema/pilar, fórmula de gancho (de
   `../instagram/references/ganchos.md`), duración si es Reel, llamado a la acción, día y hora.
4. Buscar patrones que se repiten en **al menos 2–3** publicaciones (uno solo es anécdota): formato,
   tema, fórmula, horario. Comparar medianas por formato.

## 3. Informe

- Números clave: alcance mediano, envíos/1000 mediano, mejor y peor publicación (con link).
- Tabla top 5 por múltiplo y top 5 por envíos/1000.
- **Hacer más (3)**, **dejar de hacer (2)**, **probar (1)** — cada una apoyada en publicaciones concretas.
- Si hay patrón de horario, pasarlo a `/ig-plan`. Las mejores 3 son candidatas a fijar en el perfil
  (`/ig-profile`) o a rehacer con otro gancho.

No inventar causas sin datos: si no hay patrón claro, decirlo.
