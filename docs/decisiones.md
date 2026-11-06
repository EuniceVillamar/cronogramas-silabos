# Decisiones técnicas

| # | Decisión | Motivo |
|---|---|---|
| 1 | Web con plantillas Django | Un solo proyecto, adecuado para un plazo de 6 semanas |
| 2 | GitHub Flow, sin rama `develop` | Menos trabajo de integración en un proyecto corto |
| 3 | Reglas primero, IA solo con baja confianza | Reproducible y con costo acotado |
| 4 | Extracción síncrona, sin Celery | Evita infraestructura adicional en esta etapa |
| 5 | `extractor/` separado de Django | Permite probarlo sin base de datos |
| 6 | Revisión del estudiante antes del calendario | Un error de extracción no debe llegar al calendario |

## Pendientes

- Elegir proveedor de IA y límite de gasto.
- Decidir si habrá despliegue.
