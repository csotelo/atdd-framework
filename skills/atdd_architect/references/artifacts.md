# Formato de artefactos — atdd_architect

---

## .atdd/SPEC.md (macro)

Especificación técnica completa del proyecto. Fuente de verdad. Inmutable post-aprobación.

Secciones:
- Descripción del proyecto y propósito
- Stack técnico (tabla: capa / tecnología / versión)
- Restricciones absolutas (prohibido u obligatorio)
- Arquitectura principal
- Modelos de datos principales
- Roles y permisos
- Límites del sistema
- Endpoints principales (si aplica)

---

## .atdd/SCOPE.md (macro)

Qué hace y qué NO hace el sistema. Inmutable post-aprobación.

Secciones:
- Qué incluye este proyecto
- Qué está fuera del alcance
- Integraciones externas previstas
- Integraciones explícitamente excluidas

---

## .atdd/STACK.md

Stack tecnológico con versiones y justificación.

Por tecnología:
- Nombre y versión
- Para qué se usa
- Por qué se eligió sobre alternativas

---

## .atdd/STATE.md (macro)

Estado global del proyecto. Actualizado después de cada sprint completado.

```markdown
# PROJECT STATE — [Nombre del Proyecto]
_Última actualización: [quién] — YYYY-MM-DD_

## Stack confirmado
- Tecnología 1
- Tecnología 2

## Sprints

| Sprint | Estado | Historias | Entregable |
|---|---|---|---|
| sprint_01 | done | US01, US02 | Auth básica |
| sprint_02 | in-progress | US03, US04 | Tenant management |

## Decisiones técnicas
- [Decisión] — [Razón]

## Notas
[Notas libres para el siguiente agente]
```

---

## .atdd/atf.config.json

Configuración para ATF tool. Generado una sola vez en la inicialización.

```json
{
  "baseURL": "http://localhost:8000",
  "promptsDir": ".atdd/backlog",
  "reportsDir": ".atdd/reports",
  "stateFile": ".atdd/atf-state.json",
  "headless": true,
  "timeout": 30000,
  "retries": 1,
  "screenshots": "only-on-failure",
  "docker": {
    "image": "mcr.microsoft.com/playwright/python:latest",
    "pull_policy": "if-not-present"
  }
}
```

El `baseURL` debe ajustarse al puerto real del proyecto.

---

## .atdd/sprints/sprint_NN/SPEC.md

Qué entrega técnicamente este sprint. Creado en sprint planning, inmutable post-aprobación.

```markdown
# Sprint NN — [Título] — SPEC

## Entregable
Una oración: qué puede hacer el usuario al terminar este sprint.

## Funcionalidades incluidas
- Funcionalidad 1
- Funcionalidad 2

## Criterios técnicos
- Endpoints nuevos: POST /api/..., GET /api/...
- Modelos nuevos: User, Tenant
- Integraciones: JWT, email backend dummy
```

---

## .atdd/sprints/sprint_NN/SCOPE.md

Límites del sprint. Creado en sprint planning, inmutable post-aprobación.

```markdown
# Sprint NN — [Título] — SCOPE

## Incluido en este sprint
- US01 — User registration
- US02 — User login with JWT

## Explícitamente excluido
- Password reset (sprint_02)
- 2FA (fuera del alcance del proyecto)
- OAuth con proveedores externos (fuera del alcance)

## Dependencias
- Requiere: base de datos inicializada (sprint_00)
- Produce: auth module listo para ser consumido por sprint_02
```

---

## .atdd/sprints/sprint_NN/STATE.md

Estado del sprint. Actualizado por atdd_developer y atdd_tester.

```markdown
# Sprint NN — STATE

_Última actualización: YYYY-MM-DD_

## Estado: planning | ready | in-progress | done

## Historias

| Historia | Estado | Responsable |
|---|---|---|
| US01-user-registration | ready | — |
| US02-user-login | in-progress | atdd_developer |

## Bloqueantes
ninguno | [descripción del bloqueante]

## Notas
[Notas libres]
```

---

## .atdd/sprints/sprint_NN/stories.md

Lista de historias asignadas al sprint. Referencia — los archivos viven en backlog/.

```markdown
# Sprint NN — Historias

## Historias asignadas
- US01-user-registration
- US02-user-login

## Orden de ejecución sugerido
1. US01-user-registration (base para US02)
2. US02-user-login (depende de US01)
```
