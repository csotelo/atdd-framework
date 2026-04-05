# MIGRATION.md — legacy .atf/ → .atdd/
_Fecha: 2026-04-03_

## Origen
Formato legacy `.atf/` con 5 sprints lineales.

## Resultado
| Historia | Sprint legacy | Status legacy | Status nuevo |
|---|---|---|---|
| US01-scaffolding-cli | sprint_01 | failed | damaged |
| US02-docker-runner | sprint_02 | passed | accepted |
| US03-screenplay-actors-steps | sprint_03 | passed | accepted |
| US04-feedback-state-tracking | sprint_04 | passed | accepted |
| US05-reports-pipeline-pypi | sprint_05 | passed | accepted |

## Archivado
El directorio `.atf/` fue copiado a `.atdd/archive/legacy-2026-04-03/`.
El `.atf/` original no fue eliminado — puede borrarse manualmente.

## Pendiente
- US01-scaffolding-cli tiene status `damaged`.
  El scenario fallido era: *sprint_01 should have status pending*.
  Requiere revisar si el step debe actualizarse o si el test ya no aplica.
