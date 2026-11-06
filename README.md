# Cronogramas de sílabos

Extrae las fechas de sílabos en PDF, permite revisarlas y las reúne en un calendario con detección de conflictos.

## Requisitos

- Docker Desktop
- Git
- Python 3.13, solo para correr pruebas fuera del contenedor

## Puesta en marcha

1. Copia la configuración local:

   ```bash
   cp .env.example .env
   ```

2. Cambia `SECRET_KEY` y `POSTGRES_PASSWORD` en `.env`. La clave también aparece en `DATABASE_URL`, así que debe coincidir en ambos lugares.

3. Levanta la aplicación:

   ```bash
   docker compose up --build
   ```

4. Abre <http://localhost:8000>.

PostgreSQL se publica en el puerto 5433 para no chocar con una instalación local.

## Pruebas en Windows

Con el contenedor `db` en ejecución:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.lock
pytest
ruff check .
```

## Dependencias

Se declaran en `pyproject.toml`. Después de cambiarlas, regenera el bloqueo:

```bash
pip-compile --extra dev --output-file requirements.lock pyproject.toml
```

## Estructura

| Carpeta | Contenido |
|---|---|
| `config/` | Configuración de Django |
| `apps/` | Cuentas, sílabos, calendario y exportación |
| `extractor/` | Pipeline de extracción, sin dependencia de Django |
| `tests/` | Pruebas y muestra de sílabos |
| `docs/` | ECS, formatos de sílabos y decisiones |

Para colaborar, revisa [CONTRIBUTING.md](CONTRIBUTING.md).
