# Formato de historia de usuario

Las historias viven en `.atdd/backlog/US0N-nombre/`.
Existen en dos estados: draft y ready.

---

## story.md — DRAFT

Creado por atdd_architect durante el paso de generación de backlog.
No necesita sprint asignado para existir.

```markdown
---
id: US01
title: User registration
status: draft
sprint: null
created: YYYY-MM-DD
---

## Historia
Como [rol], quiero [acción] para [beneficio].

## Descripción
Párrafo corto explicando el propósito de la historia.
Sin criterios de aceptación detallados — eso viene en el refinement.

## Notas
- Dependencias conocidas: [US00, ninguna]
- Complejidad estimada: baja | media | alta
```

---

## story.md — READY

Actualizado por atdd_architect durante el refinement.
Solo se refina cuando la historia está asignada a un sprint con contrato aprobado.

```markdown
---
id: US01
title: User registration
status: ready
sprint: sprint_01
created: YYYY-MM-DD
refined: YYYY-MM-DD
---

## Historia
Como usuario no registrado, quiero crear una cuenta con mi email
para acceder al sistema.

## Descripción
Implementar el endpoint de registro con validación de email único,
hash seguro de contraseña, y envío de email de verificación.

## Criterios de aceptación
- [ ] El usuario puede registrarse con email y contraseña válidos → Scenario: "Usuario se registra con email válido"
- [ ] El email de verificación es enviado al registrar → Scenario: "Email de verificación es enviado al registrar"
- [ ] El registro falla si el email ya existe → Scenario: "Registro falla con email duplicado"

## Definition of Ready
- [ ] Sprint 00 tiene status: done (base de datos inicializada)
- [ ] STACK.md define el stack de auth (JWT, email backend)
- [ ] acceptance.feature usa solo steps del vocabulario ATF

## Definition of Done
El sprint cierra cuando ATF corre y registra status: accepted.
Comando: atf run --sprint [US01-user-registration] --feedback
Si falla, leer .atdd/backlog/US01-user-registration/feedback.md antes de reintentar.

## Notas técnicas
- Email backend: locmem en dev/test, endpoint /api/dev/outbox/ requerido
- Dependencias: ninguna
```

---

## prompt.md

Instrucciones para atdd_developer. Solo existe en historias ready.

```markdown
# US01 — User registration

## Sprint Goal
El usuario puede registrarse con email y recibir un email de verificación.

## Definition of Ready
- [ ] Sprint anterior done (o esta es US01 del proyecto)
- [ ] Base de datos inicializada y migraciones base aplicadas
- [ ] acceptance.feature usa solo steps del vocabulario ATF
- [ ] Servidor corriendo en baseURL de atf.config.json

## Contexto
[Qué existe en el proyecto en este punto. Qué construyeron las historias anteriores.]

## Tarea
[Instrucción clara y directa de lo que debe construirse. Un párrafo o lista corta.]

## Archivos a crear o modificar
- apps/users/models.py
- apps/users/serializers.py
- apps/users/views.py
- apps/users/urls.py

## No tocar
- apps/core/models.py
- config/settings/base.py

## Listo cuando
- [ ] Usuario se registra con email válido → Scenario: "Usuario se registra con email válido"
- [ ] Email de verificación enviado → Scenario: "Email de verificación es enviado al registrar"
- [ ] Registro falla con email duplicado → Scenario: "Registro falla con email duplicado"
- [ ] atf run --sprint US01-user-registration --feedback pasa todos los scenarios

## Definition of Done
El sprint cierra cuando ATF ejecuta y registra status: passed.
Comando: atf run --sprint US01-user-registration --feedback
Si falla, leer .atdd/backlog/US01-user-registration/feedback.md antes de reintentar.
```

---

## acceptance.feature

Contrato ejecutable para ATF tool. Solo existe en historias ready.
Usa ÚNICAMENTE steps del vocabulario ATF (ver references/gherkin.md).

```gherkin
Feature: [US01] User registration

  Scenario: Usuario se registra con email válido
    Given I am an ApiClient
    When I call POST "http://localhost:8000/api/auth/register/" with body:
      """
      {"email": "test@example.com", "password": "Secret123!"}
      """
    Then the response status should be 201

  Scenario: Email de verificación es enviado al registrar
    Given I am an ApiClient
    When I call POST "http://localhost:8000/api/auth/register/" with body:
      """
      {"email": "new@example.com", "password": "Secret123!"}
      """
    Then the response status should be 201
    When I call GET "http://localhost:8000/api/dev/outbox/"
    Then the response should contain "new@example.com"
    Then the response should contain "verify"

  Scenario: Registro falla con email duplicado
    Given I am an ApiClient
    When I call POST "http://localhost:8000/api/auth/register/" with body:
      """
      {"email": "existing@example.com", "password": "Secret123!"}
      """
    Then the response status should be 400
```

Cada Scenario mapea 1:1 a un criterio en story.md y en prompt.md Done when.
