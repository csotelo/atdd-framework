# Formato de contrato de sprint

El contrato de sprint se crea en conversación con el usuario.
No se cierra hasta que el usuario lo aprueba explícitamente.

---

## sprints/sprint_NN/SPEC.md

```markdown
# Sprint NN — [Título] — SPEC

_Aprobado: YYYY-MM-DD_

## Entregable del sprint
Una oración: qué puede hacer el usuario al terminar este sprint.
Ejemplo: "El usuario puede registrarse, verificar su email, y hacer login."

## Funcionalidades incluidas
- Registro de usuario con email
- Verificación de email via token
- Login con JWT

## Contratos técnicos
- Endpoints nuevos: POST /api/auth/register/, POST /api/auth/login/
- Modelos nuevos: User (email, password_hash, is_verified, verification_token)
- Auth: JWT con access + refresh tokens
- Email: backend locmem + endpoint /api/dev/outbox/

## Criterios de calidad del sprint
- Todos los acceptance.feature de las historias asignadas pasan en ATF
- atdd_tester reporta 0 fallos en unit + integration tests
- ruff y mypy pasan sin errores
```

---

## sprints/sprint_NN/SCOPE.md

```markdown
# Sprint NN — [Título] — SCOPE

_Aprobado: YYYY-MM-DD_

## Historias incluidas
- US01 — User registration
- US02 — User login with JWT
- US03 — Email verification

## Explícitamente excluido de este sprint
- Password reset → sprint_02
- 2FA → sprint_03
- OAuth con Google/GitHub → fuera del alcance del proyecto

## Dependencias de entrada
- Requiere: sprint_00 done (proyecto inicializado, DB corriendo)

## Produce para el siguiente sprint
- Módulo auth completo y testado
- User model disponible para ser extendido
- JWT middleware listo para ser consumido por endpoints protegidos
```

---

## sprints/sprint_NN/STATE.md

Inicializado por atdd_architect al crear el contrato. Actualizado por atdd_developer y atdd_tester.

```markdown
# Sprint NN — STATE

_Última actualización: [quién] — YYYY-MM-DD_

## Estado del sprint
planning | ready | in-progress | done

## Historias

| Historia | Estado | Notas |
|---|---|---|
| US01-user-registration | draft | pendiente refinement |
| US02-user-login | draft | pendiente refinement |
| US03-email-verification | draft | pendiente refinement |

## Bloqueantes
ninguno

## Notas
[Notas del sprint]
```

---

## sprints/sprint_NN/stories.md

```markdown
# Sprint NN — Historias asignadas

Las historias viven en `.atdd/backlog/`. Este archivo es solo la referencia.

## Historias del sprint
- US01-user-registration
- US02-user-login
- US03-email-verification

## Orden de ejecución sugerido
1. US01-user-registration  (sin dependencias)
2. US03-email-verification (depende de US01 — necesita el modelo User)
3. US02-user-login         (depende de US01 — necesita el modelo User)

## Comando para ejecutar una historia
```bash
# Con Claude Code
claude -p "$(cat .atdd/backlog/US01-user-registration/prompt.md)" --dangerously-skip-permissions

# Verificar con ATF
atf run --sprint US01-user-registration --feedback
```
```
