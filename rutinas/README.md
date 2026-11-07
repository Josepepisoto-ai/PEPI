# Rutinas de gimnasio — Alumnos personales Pepi

Carpeta para guardar las rutinas, fichas y progreso de cada alumno.

## Estructura

```
rutinas/
├── README.md                  ← esta guía
├── _plantillas/               ← copiá de acá para empezar
│   ├── ficha-alumno.md        ← datos, objetivos, lesiones
│   ├── rutina.md              ← rutina semanal (días, ejercicios, series, reps)
│   └── progreso.md            ← registro de cargas, medidas y notas
└── alumnos/
    ├── _ejemplo-alumno/       ← ejemplo completo para guiarte
    └── nombre-apellido/       ← una carpeta por alumno
        ├── ficha.md
        ├── progreso.md
        └── rutinas/
            ├── 2026-11-fuerza-base.md
            └── 2026-12-hipertrofia.md
```

## Cómo agregar un alumno nuevo

```bash
cd rutinas/alumnos
mkdir -p maria-gomez/rutinas
cp ../_plantillas/ficha-alumno.md maria-gomez/ficha.md
cp ../_plantillas/progreso.md     maria-gomez/progreso.md
cp ../_plantillas/rutina.md       maria-gomez/rutinas/2026-11-fuerza-base.md
```

O pedile a Claude: *"agregá a María Gómez, 32 años, objetivo bajar grasa, 3 días por semana"*.

## Convenciones

- **Carpeta del alumno:** `nombre-apellido` en minúsculas y con guiones (`juan-perez`).
- **Rutinas:** `AAAA-MM-descripcion.md` (`2026-11-fuerza-base.md`), así quedan ordenadas por fecha.
  Cuando cambiás la rutina, creá un archivo nuevo y no borres el anterior: queda el historial.
- **Progreso:** una fila nueva por sesión o por control, la más reciente arriba.

## Privacidad

Las fichas tienen datos de salud de los alumnos. Mantené este repositorio **privado**
y no compartas los archivos sin permiso del alumno.
