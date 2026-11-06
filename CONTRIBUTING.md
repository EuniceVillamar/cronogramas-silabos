# Cómo contribuir

## Ramas

`main` siempre debe funcionar y nadie sube cambios directamente. Cada cambio nace de `main` en una rama corta:

| Prefijo | Uso |
|---|---|
| `feature/` | Funcionalidad nueva |
| `fix/` | Corrección |
| `docs/` | Documentación |
| `chore/` | Mantenimiento |

Ejemplo: `feature/parser-tablas`.

## Commits

Se usa [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/):

```text
feat(extractor): agrega parser de tablas
fix(schedule): corrige conflictos en ventana de 48 horas
docs: actualiza la lista de ECS
```

## Pull requests

1. Actualiza tu rama con `main`.
2. Abre el PR usando la plantilla y enlaza su issue.
3. Consigue al menos una aprobación de otro integrante.
4. Espera a que CI esté en verde y fusiona con *squash*.

## Protección de `main`

En GitHub, entra a **Settings → Branches** y exige en `main`:

- Pull request antes de fusionar, con una aprobación.
- El check `calidad` en verde.

## Versiones

Se usa [SemVer](https://semver.org/lang/es/) con etiquetas `vX.Y.Z`. Para publicar una versión:

1. Mueve lo pendiente de `CHANGELOG.md` a la nueva versión mediante un PR.
2. Crea la etiqueta anotada sobre `main`.
3. Publica el GitHub Release con esa etiqueta.
