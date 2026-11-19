# Decisiones técnicas

| # | Decisión | Motivo |
|---|---|---|
| 1 | Web con plantillas Django | Un solo proyecto, adecuado para un plazo de 6 semanas |
| 2 | GitHub Flow, sin rama `develop` | Menos trabajo de integración en un proyecto corto |
| 3 | Reglas primero, IA solo con baja confianza | Reproducible y con costo acotado |
| 4 | Extracción síncrona, sin Celery | Evita infraestructura adicional en esta etapa |
| 5 | `extractor/` separado de Django | Permite probarlo sin base de datos |
| 6 | Revisión del estudiante antes del calendario | Un error de extracción no debe llegar al calendario |
| 7 | Las fechas se extraen del PDF del calendario académico; el sílabo aporta materia, unidades, horas, temas y ponderaciones | Los sílabos no contienen fechas de evaluaciones y el calendario sí ([análisis](formatos-silabos.md)) |
| 8 | Las semanas de cada unidad se estiman según sus horas ACD y el estudiante las confirma | Es el único dato del sílabo que permite ubicar los temas en el tiempo |
| 9 | El `.ics` se genera al vuelo y se guarda solo en la sesión | Entrega el resultado sin esperar al modelo de calendario compartido |
| 10 | Los temas de un sílabo se leen recortando la columna "Contenidos" por coordenadas | Las tablas extraídas pierden esa columna en las páginas de continuación |
| 11 | Los PDF de calendario se versionan como muestra; los sílabos no | Los calendarios son públicos, y los sílabos tienen nombres de docentes |

## Pendientes

- Elegir proveedor de IA y límite de gasto.
- Decidir si habrá despliegue.
- Guardar el calendario académico compartido en la base de datos, para que se suba una sola vez por periodo.
- Conseguir sílabos sin datos personales para probar su extracción en CI.
