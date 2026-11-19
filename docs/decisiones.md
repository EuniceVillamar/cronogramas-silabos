# Decisiones técnicas

| # | Decisión | Motivo |
|---|---|---|
| 1 | Web con plantillas Django | Un solo proyecto, adecuado para un plazo de 6 semanas |
| 2 | GitHub Flow, sin rama `develop` | Menos trabajo de integración en un proyecto corto |
| 3 | Reglas primero, IA solo con baja confianza | Reproducible y con costo acotado |
| 4 | Extracción síncrona, sin Celery | Evita infraestructura adicional en esta etapa |
| 5 | `extractor/` separado de Django | Permite probarlo sin base de datos |
| 6 | Revisión del estudiante antes del calendario | Un error de extracción no debe llegar al calendario |
| 7 | Las fechas salen del calendario académico; el sílabo aporta materia, unidades, horas y ponderaciones | Los sílabos de la muestra no contienen fechas de evaluaciones ([análisis](formatos-silabos.md)) |
| 8 | Las semanas de cada unidad se estiman según sus horas ACD y el estudiante las confirma | Es el único dato del sílabo que permite ubicar los temas en el tiempo |

## Pendientes

- Elegir proveedor de IA y límite de gasto.
- Decidir si habrá despliegue.
- Reformular el objetivo 2 para medir la precisión sobre los campos extraídos del sílabo.
- Definir cómo se registra el calendario académico del periodo.
