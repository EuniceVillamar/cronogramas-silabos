# Análisis de formatos de sílabos y calendarios

Documento del objetivo específico 1. Resume qué contienen los sílabos y los calendarios académicos reales y define qué se puede extraer de cada uno.

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

Por eso las fechas se extraen del **calendario académico del periodo** (ver [Calendarios académicos](#calendarios-académicos)) y se combinan con lo que sí trae el sílabo. La decisión está registrada en [decisiones.md](decisiones.md).

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

## Calendarios académicos

Muestra: los calendarios ordinarios CI y CII 2026-2027 de la Universidad de Guayaquil. Están en `tests/fixtures/calendarios/`, sin los metadatos de autor del PDF original, junto con su resultado etiquetado a mano.

### Estructura

Ambos son una tabla de dos columnas: **fecha** y **actividad**. Las filas sin actividad son títulos de sección, y las que empiezan con `NOTA` son aclaraciones.

| Sección | Uso para el estudiante |
|---|---|
| Cambio de carrera | Trámite |
| Matriculación | Matrículas, retiros |
| Clases, exámenes e ingreso de calificaciones | Inicio de cada parcial, exámenes, recuperación, fin del periodo |
| Otras actividades docentes, evaluación docente, capacitación docente | No se usan |
| Vacaciones y feriados | Días sin clases |

### Diferencias entre los dos formatos

| | CI 2026-2027 | CII 2026-2027 |
|---|---|---|
| Tablas | Una por sección, seis en total | Una sola tabla que continúa en la página 2 |
| Nombre de la sección de exámenes | Clases - Exámenes - Ingreso de calificaciones | Exámenes y actividades docentes |
| Fecha de portada | `01 DE ABRIL DE 2026` | `12 DE OCTUBRE DE 2026` |

El extractor no depende del número de tablas: recorre las filas en orden y recuerda la sección vigente aunque cambie de página.

### Formas de escribir fechas

| Forma | Ejemplo |
|---|---|
| Fecha única | `01 de abril de 2026`, `26 de mayo del 2026` |
| Rango en un mes | `Del 18 al 23 de mayo de 2026` |
| Rango entre meses | `Del 30 de noviembre al 05 de diciembre de 2026` |
| Rango entre años | `Del 01 de septiembre de 2026 al 25 de febrero de 2027` |
| Con día de la semana | `Lunes 16 al martes 17 de febrero de 2026`, `Del Miercoles 23 de septiembre…` |
| Días unidos por "y" | `Lunes 08 y martes 09 de febrero de 2027` |
| Con anotación | `… de 2027 (Durante todo el ciclo académico)` |

### Errores del propio documento

| Fila | Problema | Tratamiento |
|---|---|---|
| `Viernes 9 de octubre de 2025` en CII 2026-2027 | El año está fuera del periodo y el 9/10/2025 fue jueves | Se marca, se sugiere el 09/10/2026 y no entra al `.ics` |
| `Viernes 25 de diciembre de 2026` en CII | La fila quedó sin descripción al partirse entre páginas | Se incluye como "Feriado" y se marca para revisar |

### Precisión

Con el resultado etiquetado a mano, el extractor obtiene **29 de 29 fechas correctas en cada calendario**: 100 % de precisión y de cobertura. CI exige al menos 85 % en ambas medidas.

## Cómo se arma el calendario del estudiante

1. **Fechas de la universidad:** salen del calendario académico. Se descartan las actividades solo para docentes.
2. **Semanas de cada unidad:** los días de clase de cada parcial se reparten en proporción a las horas ACD de las unidades. Por ejemplo, en Estructura de Datos la unidad 3 tiene 18 de 48 horas, es decir, el 37,5 % de los días de clase.
3. **Temas de cada examen:** una unidad entra en el parcial donde cae la mitad de sus horas.
4. **Recordatorios de repaso:** una cantidad de días antes de cada semana de exámenes, configurable y de 7 por defecto, con los temas de las unidades que entran.
5. **Revisión:** las fechas estimadas se marcan como tales y la vista previa muestra todo antes de descargar el `.ics`.

## Formas de escribir fechas en el sílabo

| Forma | Ejemplo | Dónde aparece | Tratamiento |
|---|---|---|---|
| `dd/mm/aaaa` | `07/04/2026` | Pie de página | Descartar |
| `dd/mm/aaaa hh:mm:ss` | Fecha de una firma | Sección G | Descartar |
| Horas por unidad | `ACD: 18` | Sección D | Convertir en días estimados |

## Pendientes

- Ampliar la muestra con sílabos de otras carreras y facultades para confirmar que usan la misma plantilla.
- Conseguir calendarios de otros periodos para ampliar la medición de precisión.
