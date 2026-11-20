# Cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/) y las versiones siguen [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Agregado

- Base del proyecto con Django, PostgreSQL y Docker Compose.
- Registro e inicio de sesión de estudiantes.
- Modelos de periodos, materias, sílabos, actividades y conflictos.
- Lectura de PDF y contratos del extractor.
- Integración continua, plantillas de colaboración y documentación de ECS.
- Análisis de formatos de sílabos y reglas de extracción.
- Extracción de fechas del calendario académico, con advertencias para años o días de la semana incorrectos.
- Extracción de materia, unidades, temas y evaluación del sílabo.
- Generación del calendario `.ics` con exámenes, inicio estimado de unidades y recordatorios de repaso.
- Pantalla para subir el calendario y los sílabos, con vista previa, y comando `generar_calendario`.
- Medición de precisión del extractor de calendarios en CI.
- Nueva interfaz con la paleta del proyecto: portada pública, semana destacada del calendario generado y formularios rediseñados.

### Eliminado

- Contratos de clasificador y parsers por formato de sílabo, reemplazados por los extractores de calendario y sílabo.
