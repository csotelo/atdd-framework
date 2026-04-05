# Definition of Ready — Checklist para atdd_developer

Antes de escribir una línea de código, verificar todos estos puntos.
Si alguno falla: reportar, actualizar story.md a `blocked`, detenerse.

---

## Checklist universal

### Del framework
- [ ] `.atdd/SPEC.md` existe y está completo
- [ ] `.atdd/STACK.md` existe con el stack definido
- [ ] `.atdd/atf.config.json` existe con baseURL configurada

### De la historia
- [ ] `story.md` tiene `status: ready` (no draft, no blocked, no in-progress)
- [ ] `story.md` tiene criterios de aceptación definidos
- [ ] `prompt.md` existe con todas las secciones: Sprint Goal, DoR, Contexto, Tarea, Archivos, Listo cuando, DoD
- [ ] `acceptance.feature` existe y usa solo steps del vocabulario ATF
- [ ] Cada criterio en "Listo cuando" apunta a un Scenario en el .feature

### Del sprint
- [ ] La historia está asignada a un sprint en `stories.md`
- [ ] El sprint tiene `SPEC.md` y `SCOPE.md` aprobados
- [ ] La historia anterior del sprint (si hay) tiene `status: tested` o no es prerequisito

### Del entorno (para historias con servidor)
- [ ] El servidor está corriendo en la baseURL de `atf.config.json`
- [ ] La base de datos está inicializada y las migraciones aplicadas
- [ ] Las variables de entorno requeridas están configuradas

---

## Checklist por stack

### Python / Django
- [ ] Entorno virtual activo con dependencias instaladas (`pip install -r requirements/dev.txt`)
- [ ] `python manage.py migrate` ejecutado sin errores
- [ ] `EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'` en settings de dev/test

### Node / Express o NestJS
- [ ] `npm install` ejecutado sin errores
- [ ] Variables de entorno en `.env.local` o `.env.test`
- [ ] Base de datos de test inicializada

---

## Qué hacer si un punto falla

1. Identificar exactamente qué falta
2. Actualizar `story.md`:
   ```yaml
   status: blocked
   ```
   Y agregar en `## Notas`:
   ```
   Bloqueado: [descripción exacta de qué falta y quién debe resolverlo]
   ```
3. Actualizar `sprint STATE.md` con el bloqueante
4. Reportar al usuario y detenerse

No intentar resolver el bloqueante si es responsabilidad de otro rol
(ej. si falta el contrato de sprint → atdd_architect, si falta infraestructura → usuario).
