# Elementos de configuración del software

| ID | Elemento | Ubicación | Responsable | Control |
|---|---|---|---|---|
| ECS-01 | Código de la aplicación | `apps/`, `config/`, `templates/` | EuniceVillamar | Git y PR |
| ECS-02 | Extractor | `extractor/` | EuniceVillamar | Git y PR |
| ECS-03 | Pruebas | `tests/` | EuniceVillamar | Git y PR |
| ECS-04 | Muestra de sílabos | `tests/fixtures/silabos/` | EuniceVillamar | Git y PR |
| ECS-05 | Migraciones | `apps/*/migrations/` | EuniceVillamar | Git, PR y CI |
| ECS-06 | Dependencias | `pyproject.toml`, `requirements.lock` | EuniceVillamar | Git y PR |
| ECS-07 | Infraestructura | `Dockerfile`, `docker-compose.yml`, `.env.example` | EuniceVillamar | Git y PR |
| ECS-08 | Pipeline de CI | `.github/workflows/` | EuniceVillamar | Git y PR |
| ECS-09 | Documentación | `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/` | EuniceVillamar | Git y PR |
| ECS-10 | Versiones | Etiquetas y GitHub Releases | EuniceVillamar | SemVer |

## Fuera de la línea base

No se versionan `.env`, claves de API, `media/` ni los datos de PostgreSQL.

## Control de cambios

Todo cambio a un ECS pasa por un issue, una rama, un pull request revisado y CI en verde. Cada versión etiquetada es una línea base.
