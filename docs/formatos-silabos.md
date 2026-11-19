# Análisis de formatos de sílabos

Documento del objetivo específico 1. Resume qué contienen los sílabos reales y define qué se puede extraer de ellos.

## Muestra

Cuatro sílabos de la carrera de Software de la Universidad de Guayaquil, periodo 2026. Los PDF no se suben al repositorio porque incluyen nombres de docentes.

| # | Asignatura | Código | Semestre | Páginas | Unidades | Horas ACD por unidad |
|---|---|---|---|---|---|---|
| 1 | Introducción a la Ingeniería de Software | 0311112 | 1 | 15 | 4 | 6 · 10 · 8 · 8 = 32 |
| 2 | Estructura de Datos | 0311313 | 3 | 14 | 4 | 4 · 12 · 18 · 14 = 48 |
| 3 | Construcción de Software | 0311611 | 6 | 12 | 3 | 27 · 11 · 10 = 48 |
| 4 | Gestión de la Configuración del Software | 0311911 | 9 | 12 | 3 | 10 · 20 · 18 = 48 |

Todos tienen texto seleccionable; ninguno necesita OCR.

## Hallazgo principal

**Ningún sílabo de la muestra contiene fechas de evaluaciones, entregas ni proyectos.** Las únicas fechas que aparecen son:

| Fecha | Dónde aparece | ¿Sirve para el calendario? |
|---|---|---|
| Fecha de impresión, por ejemplo `07/04/2026` | Pie de cada página, junto al número | No |
| Fechas de elaboración, revisión y aprobación | Sección G, firmas de responsabilidad | No |

El extractor debe descartar ambas para no crear actividades falsas.

Por eso las fechas del calendario saldrán del **calendario académico del periodo**, combinado con lo que sí trae el sílabo. La decisión está registrada en [decisiones.md](decisiones.md).

## Estructura común

Los cuatro sílabos usan la misma plantilla institucional, con estas secciones en este orden:

| Sección | Contenido | Uso en la herramienta |
|---|---|---|
| A: Datos informativos | Facultad, carrera, asignatura, código, semestre, créditos, horas y prerrequisitos | Crear la materia |
| B: Justificación | Texto libre y objetivo | No se usa |
| C: Propósitos y aportes al perfil de egreso | Tabla de competencias | No se usa |
| D: Unidades temáticas | Una tabla por unidad con número, nombre, objetivo, contenidos y horas ACD, APE y AA | Estimar en qué semanas se ve cada unidad |
| E: Evaluación de los aprendizajes | Componentes con ponderación y actividades marcadas con `X` | Tipos de actividad y ponderaciones |
| F: Bibliografía | Libros y sitios web | No se usa |
| G: Firmas de responsabilidad | Nombres de docentes y fechas de firma | Se descarta; contiene datos personales |

En los cuatro, la sección E usa los mismos componentes y pesos:

| Componente | Ponderación |
|---|---|
| Gestión formativa | 33 % |
| Gestión práctica y autónoma | 33 % |
| Acreditación y validación (sumativa) | 34 % |
| Evaluación diagnóstica | 0 % |

Las actividades marcadas con `X` cambian de una materia a otra. Algunos ejemplos son el trabajo participativo en clases, los talleres colaborativos, la lección teórica y práctica, la exposición de proyectos y el examen teórico y práctico.

## Problemas de lectura detectados

Se observaron con `pdfplumber`, el lector del proyecto.

| Problema | Ejemplo | Regla para resolverlo |
|---|---|---|
| Encabezado repetido en cada página | "UNIVERSIDAD DE GUAYAQUIL … SÍLABO" | Quitar las cuatro líneas del encabezado antes de analizar |
| Pie con número y fecha de impresión | `5 07/04/2026` | Quitar la última línea de cada página |
| Palabras cortadas en columnas angostas | `INTRODUC / CIÓN A / INGENIERÍ / A DE / SOFTWARE` | Unir los fragmentos de una celda sin espacio cuando el corte cae a mitad de palabra |
| Tablas que continúan en la página siguiente | Contenidos de una unidad o la tabla de evaluación | Unir las tablas de páginas seguidas cuando la segunda no tiene cabecera |
| Encabezado detectado como tabla | `UN / VICERR | IVERSIDAD / …` | Descartar las tablas cuyo texto coincide con el encabezado |
| Etiqueta y valor en filas distintas | `ACD / :` en una fila y las horas `APE` y `AA` en las siguientes | Leer las horas por etiqueta, no por posición fija |
| Texto de varias columnas mezclado | Párrafos de la sección C intercalados | Usar las tablas en lugar del texto plano para las secciones B a E |

## Reglas de extracción

| Dato | Dónde está | Regla |
|---|---|---|
| Asignatura | Sección A, fila `Asignatura:` | Celda siguiente a la etiqueta, con los fragmentos unidos |
| Código | Sección A, fila `Asignatura:` | Celda siguiente a `Código:`; siete dígitos |
| Semestre | Sección A, fila `Prerrequisitos` | Valor después de `Semestre:` |
| Unidades | Sección D | Cada tabla que empieza con `Unidad #:` |
| Horas por unidad | Sección D | Números junto a `ACD`, `APE` y `AA` |
| Componentes y pesos | Sección E | Filas con nombre de componente y un número entre 0 y 100 |
| Actividades evaluadas | Sección E | Filas cuya última celda es `X` |

### Comprobaciones

- La suma de las horas ACD de las unidades debe ser igual a las horas del componente de docencia de la sección A. Se cumple en los cuatro sílabos.
- La suma de las ponderaciones debe ser 100.

Si alguna comprobación falla, la extracción baja su confianza y pasa a revisión.

## Cómo se obtienen las fechas

1. **Inicio y fin del periodo:** el estudiante los registra en la herramienta.
2. **Fechas de evaluaciones:** salen del calendario académico del periodo y se registran una vez, para todas las materias.
3. **Semanas de cada unidad:** se estiman repartiendo las semanas de clase en proporción a las horas ACD. Por ejemplo, en Estructura de Datos la unidad 3 tiene 18 de 48 horas, es decir, el 37,5 % del periodo.
4. **Revisión:** toda fecha estimada se marca como tal y el estudiante la confirma antes de que entre al calendario.

## Formas de escribir fechas

| Forma | Ejemplo | Dónde aparece | Tratamiento |
|---|---|---|---|
| `dd/mm/aaaa` | `07/04/2026` | Pie de página | Descartar |
| `dd/mm/aaaa hh:mm:ss` | Fecha de una firma | Sección G | Descartar |
| Horas por unidad | `ACD: 18` | Sección D | Convertir en semanas estimadas |

## Pendientes

- Ampliar la muestra con sílabos de otras carreras y facultades para confirmar que usan la misma plantilla.
- Conseguir el calendario académico oficial del periodo y definir cómo se registra.
- Reformular el objetivo 2: la precisión del 85 % debe medirse sobre los campos extraídos del sílabo, porque el sílabo no contiene fechas.
