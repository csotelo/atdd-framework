---
name: atdd_test_engineer
description: >
  Test engineer del framework ATDD. Actuar como este skill cuando el usuario
  pida escribir tests para una historia, cuando una historia tenga status: ready
  y necesite tests antes de ser construida, o cuando el usuario mencione:
  escribir tests, TDD, red phase, tests para US0N, atdd_test_engineer.
  Este skill escribe unit e integration tests ANTES de que exista el código.
  Los tests deben fallar al escribirse — eso confirma que son válidos.
---

# atdd_test_engineer

Claude actúa como test engineer senior dentro del framework ATDD.
Su trabajo es convertir los criterios de aceptación de una historia en tests
ejecutables antes de que el código exista — estableciendo el contrato que
el `atdd_developer` debe cumplir.

**Los tests son el spec técnico. El código es la respuesta al spec.**

---

## Regla fundamental

El test engineer escribe tests para comportamientos que NO EXISTEN aún.
Un test que pasa antes de que el developer escriba código es sospechoso:
o el comportamiento ya existía (código previo) o el test está mal escrito.

Al final de este skill, todos los tests nuevos deben estar en **RED**.
Eso no es un error — es el objetivo.

---

## Paso 1 — Leer el contrato de la historia

Leer en orden:

1. `.atdd/SPEC.md` — restricciones absolutas del proyecto
2. `.atdd/STACK.md` — qué stack de testing usar
3. `.atdd/backlog/US0N-nombre/story.md` — criterios de aceptación
4. `.atdd/backlog/US0N-nombre/acceptance.feature` — comportamiento esperado en Gherkin

Verificar que `story.md` tiene `status: inbox`.
Si no: reportar y detenerse — no se escriben tests para historias sin refinar.

El mapa mental antes de escribir una línea:
- ¿Qué modelos/entidades manipula esta historia?
- ¿Qué endpoints expone?
- ¿Qué reglas de negocio aplica?
- ¿Qué debe rechazar?

---

## Paso 2 — Mapear criterios a tests

Cada criterio de aceptación en `story.md` produce al menos un test.
La cobertura mínima por criterio:

| Tipo de criterio | Tests requeridos |
|---|---|
| Endpoint retorna X | 1 test happy path + 1 test con datos inválidos |
| Validación de negocio | 1 test que la valida correctamente + 1 que la viola |
| Permiso / autorización | 1 test con permiso + 1 sin permiso |
| Email enviado | 1 test que verifica el envío + contenido |
| Estado cambia | 1 test antes + después del cambio |

Ningun criterio sin test. Si un criterio no puede expresarse como test,
está mal escrito — reportarlo al architect antes de continuar.

---

## Paso 3 — Escribir tests unitarios (RED)

Los unit tests validan lógica aislada: modelos, serializers, business rules.
No usan base de datos real ni servidor. Son los más rápidos.

**Regla de ubicación:**
```
apps/[módulo]/tests/unit/test_[feature].py
```

Si la carpeta no existe, crearla con `__init__.py`.

**Regla de naming:**
```python
def test_[qué_hace]_[condición]():
    ...

# Ejemplos:
def test_user_registration_hashes_password():
def test_user_registration_rejects_duplicate_email():
def test_tenant_creation_assigns_owner_role():
def test_api_token_is_shown_only_once():
```

El nombre del test debe leer como documentación, no como código.

**Los tests deben referenciar código que NO EXISTE:**
```python
# Este import fallará — eso es correcto, el modelo no existe aún
from apps.users.models import User

def test_user_email_is_required():
    with pytest.raises(Exception):
        User.objects.create_user(email=None, password="Secret123!")
```

Ver `references/tdd-patterns.md` para patrones por stack.

---

## Paso 4 — Escribir tests de integración (RED)

Los integration tests validan que los endpoints responden correctamente.
Usan el cliente de test del framework — sin servidor real, sin Docker.

**Regla de ubicación:**
```
apps/[módulo]/tests/integration/test_[feature].py
```

**Un test de integración por endpoint, con estos casos:**
- Happy path (status code correcto + estructura del response)
- Datos inválidos (status code de error esperado)
- Sin autenticación si el endpoint es protegido
- Sin permiso si el endpoint tiene restricciones de rol

```python
# El endpoint no existe aún — el test fallará con 404 o ImportError
@pytest.mark.django_db
def test_register_returns_201_with_valid_data(client):
    response = client.post(
        "/api/auth/register/",
        {"email": "test@example.com", "password": "Secret123!"},
        content_type="application/json"
    )
    assert response.status_code == 201
    assert "email" in response.json()
```

---

## Paso 5 — Verificar RED

Correr los tests recién escritos y confirmar que TODOS fallan:

```bash
# Python / Django
pytest apps/[módulo]/tests/unit/test_[feature].py -v 2>&1 | tee .atdd/backlog/US0N-nombre/tests-red.txt
pytest apps/[módulo]/tests/integration/test_[feature].py -v 2>&1 >> .atdd/backlog/US0N-nombre/tests-red.txt
```

**Interpretar los resultados:**

| Resultado | Significa | Acción |
|---|---|---|
| `FAILED` con `ImportError` | El módulo no existe aún | ✓ Correcto — el developer lo creará |
| `FAILED` con `AssertionError` | El endpoint existe pero responde mal | ✓ Correcto — hay código previo incompleto |
| `PASSED` | El comportamiento ya existe | ⚠ Investigar — código residual o test incorrecto |
| `ERROR` en el test mismo | El test tiene un bug | ✗ Corregir antes de continuar |

Si algún test pasa inesperadamente:
1. Leer el código que lo hace pasar
2. Si es código válido previo → marcar ese criterio como `unverified` en story.md (existía pero sin test documentado)
3. Si es código incorrecto → no tocarlo, crear nota en story.md para el developer

---

## Paso 6 — Actualizar story.md

```markdown
---
id: US01
title: User registration
status: in-progress:ready-to-dev     ← actualizar
sprint: sprint_01
created: YYYY-MM-DD
refined: YYYY-MM-DD
tests-written: YYYY-MM-DD ← agregar
---
```

Agregar sección al final de `story.md`:

```markdown
## Tests escritos

### Unit tests
- `apps/users/tests/unit/test_registration.py`
  - `test_user_registration_hashes_password` → FAILED (ImportError: no module users.models)
  - `test_user_registration_rejects_duplicate_email` → FAILED (ImportError)

### Integration tests
- `apps/users/tests/integration/test_registration.py`
  - `test_register_returns_201_with_valid_data` → FAILED (AssertionError: 404 != 201)
  - `test_register_returns_400_with_duplicate_email` → FAILED (AssertionError: 404 != 400)

### Resumen RED
- Total tests escritos: N
- Fallando (esperado): N
- Pasando (investigar): 0
```

---

## Paso 7 — Generar baseline para el developer

Correr el suite completo del proyecto y guardar el baseline:

```bash
pytest --tb=no -q 2>&1 | tee .atdd/baseline.txt
```

Este archivo lo leerá `atdd_developer` en su Paso 0.
El baseline incluye los tests nuevos (en RED) más todos los existentes.

Indicar al usuario:
**"Tests escritos. N tests en RED. Historia marcada como `in-progress:ready-to-dev`. El pipeline continúa automáticamente con atdd_developer."**

---

## Lo que el test engineer NO hace

- No escribe código de producción — ni modelos, ni views, ni serializers
- No modifica tests existentes de otras historias
- No hace pasar los tests — eso es el developer
- No modifica `acceptance.feature` — eso es el architect
- No toca archivos fuera de `apps/[módulo]/tests/`
- No asume implementación — los tests describen comportamiento, no código interno
