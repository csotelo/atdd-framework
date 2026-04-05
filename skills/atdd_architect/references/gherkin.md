# Vocabulario ATF — Steps disponibles

Los `acceptance.feature` deben usar ÚNICAMENTE estos steps.
ATF tool tiene implementaciones para cada uno.
Un step fuera de esta lista causará "step not found" en runtime.

---

## Steps disponibles

```gherkin
# Actores — primer Given de cada Scenario
Given I am a WebUser
Given I am an ApiClient
Given the state file exists

# Navegación web
When I navigate to "{url}"

# Formularios
When I fill in "{field}" with "{value}"
When I click the "{text}" button
When I click "{selector}"
When I select "{value}" from "{field}"

# Espera
When I wait for "{selector}"
When I wait {seconds} seconds

# API — HTTP
When I call GET "{url}"
When I call POST "{url}" with body:
  """
  { "campo": "valor" }
  """
When I call DELETE "{url}"
When I set header "{name}" to "{value}"

# Aserciones UI
Then I should see "{text}"
Then I should not see "{text}"
Then the element "{selector}" should be visible
Then the element "{selector}" should not be visible
Then the field "{field}" should have value "{value}"
Then there should be {count} "{selector}" elements

# Aserciones API
Then the response status should be {code}
Then the response should contain "{text}"
Then the response field "{field}" should equal "{value}"

# Aserciones de estado
Then sprint "{sprint}" should have status "{status}"

# Aserciones de archivos
Then a report file should exist at "{path}"
```

---

## Reglas para escribir acceptance.feature

- Cada Feature corresponde a una historia: `Feature: [US01] Nombre de la historia`
- No usar Background — el setup del entorno es responsabilidad del DoR en prompt.md
- Cada Scenario prueba exactamente una cosa
- Scenarios independientes entre sí — sin dependencia de orden
- El nombre de cada Scenario debe coincidir exactamente con el criterio
  referenciado en `## Listo cuando` del prompt.md
- Los selectors CSS deben ser reales — no inventarlos

---

## Convención de email (Python/Django)

Para verificar emails enviados, el agente debe exponer:
```
GET /api/dev/outbox/  →  lista de emails (solo DEBUG=True)
```

Gherkin para verificar email:
```gherkin
Scenario: Email de verificación es enviado al registrar
  Given I am an ApiClient
  When I call POST "http://localhost:8000/api/auth/register/" with body:
    """
    {"email": "test@example.com", "password": "Secret123!"}
    """
  Then the response status should be 201
  When I call GET "http://localhost:8000/api/dev/outbox/"
  Then the response should contain "test@example.com"
  Then the response should contain "verify"
```

---

## Sitios públicos para features de infraestructura

Cuando el feature no tiene un servidor de proyecto (ej. sprint de scaffolding):
- UI: `https://the-internet.herokuapp.com`
- API: `https://jsonplaceholder.typicode.com`
