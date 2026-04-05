# Patrones TDD — escribir tests en RED

El test engineer escribe tests para código que no existe.
Estos patrones muestran cómo estructurar esos tests por stack.

---

## Python / Django

### Estructura de carpetas

```
apps/[módulo]/
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   └── test_[feature].py
    └── integration/
        ├── __init__.py
        └── test_[feature].py
```

### conftest.py mínimo en raíz

```python
# conftest.py
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')

import pytest

@pytest.fixture(autouse=True)
def reset_email_outbox():
    from django.core import mail
    mail.outbox = []
    yield
```

### Patrón: modelo que no existe aún

```python
import pytest

# Este import fallará con ImportError — correcto en RED
def test_user_model_uses_email_as_identifier():
    from apps.users.models import User
    assert User.USERNAME_FIELD == "email"

def test_user_password_is_hashed_on_creation():
    from apps.users.models import User
    # Si User no existe, el test falla aquí — correcto
    user = User(email="test@example.com")
    user.set_password("Secret123!")
    assert user.password != "Secret123!"
    assert user.check_password("Secret123!")

@pytest.mark.django_db
def test_duplicate_email_raises_integrity_error():
    from apps.users.models import User
    User.objects.create_user(email="dup@example.com", password="pass")
    with pytest.raises(Exception):  # IntegrityError o ValidationError
        User.objects.create_user(email="dup@example.com", password="pass")
```

### Patrón: endpoint que no existe aún

```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestRegistrationEndpoint:

    def setup_method(self):
        self.client = Client()
        self.url = "/api/auth/register/"
        self.valid_payload = {
            "email": "test@example.com",
            "password": "Secret123!"
        }

    def test_returns_201_with_valid_data(self):
        # Fallará con 404 si el endpoint no existe — correcto
        response = self.client.post(
            self.url,
            self.valid_payload,
            content_type="application/json"
        )
        assert response.status_code == 201

    def test_response_contains_email(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            content_type="application/json"
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == self.valid_payload["email"]

    def test_returns_400_with_invalid_email(self):
        response = self.client.post(
            self.url,
            {"email": "not-an-email", "password": "Secret123!"},
            content_type="application/json"
        )
        assert response.status_code == 400
        assert "email" in response.json()

    def test_returns_400_with_duplicate_email(self):
        self.client.post(self.url, self.valid_payload, content_type="application/json")
        response = self.client.post(self.url, self.valid_payload, content_type="application/json")
        assert response.status_code == 400

    def test_unauthenticated_request_allowed(self):
        # Registro no requiere auth
        response = self.client.post(self.url, self.valid_payload, content_type="application/json")
        assert response.status_code != 401
        assert response.status_code != 403
```

### Patrón: email que no se envía aún

```python
import pytest
from django.test import Client
from django.core import mail

@pytest.mark.django_db
class TestVerificationEmail:

    def setup_method(self):
        self.client = Client()

    def test_registration_sends_one_email(self):
        self.client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        # Fallará con AssertionError: 0 != 1 si email no se envía — correcto
        assert len(mail.outbox) == 1

    def test_email_is_sent_to_registered_address(self):
        self.client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["test@example.com"]

    def test_email_contains_verification_link(self):
        self.client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        assert len(mail.outbox) == 1
        body = mail.outbox[0].body
        assert "verify" in body.lower()
        assert "token" in body.lower()
```

### Patrón: permisos y autenticación

```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestTenantPermissions:

    def setup_method(self):
        self.client = Client()
        # Crear usuarios de prueba — si el modelo no existe, falla aquí (RED)
        from apps.users.models import User
        self.owner = User.objects.create_user(email="owner@example.com", password="pass")
        self.member = User.objects.create_user(email="member@example.com", password="pass")

    def test_unauthenticated_cannot_create_tenant(self):
        response = self.client.post(
            "/api/tenants/",
            {"name": "Test Tenant"},
            content_type="application/json"
        )
        assert response.status_code in [401, 403]

    def test_owner_can_delete_member(self):
        # Login como owner (endpoint de login puede no existir aún — RED)
        self.client.force_login(self.owner)
        response = self.client.delete(
            f"/api/tenants/1/members/{self.member.id}/",
        )
        assert response.status_code in [200, 204]

    def test_member_cannot_delete_other_member(self):
        self.client.force_login(self.member)
        response = self.client.delete(
            f"/api/tenants/1/members/{self.owner.id}/",
        )
        assert response.status_code == 403
```

### Patrón: regla de negocio aislada

```python
class TestApiTokenBusinessRules:

    def test_only_one_active_token_per_owner_tenant(self):
        from apps.api_tokens.models import APIToken
        # Si el modelo no existe — ImportError (RED)
        # Si existe pero no tiene la restricción — AssertionError (RED)

        # El test describe la regla, no la implementación
        token1 = APIToken(owner_id=1, tenant_id=1, is_active=True)
        token1.save()

        # El segundo token debería desactivar el primero o lanzar excepción
        token2 = APIToken(owner_id=1, tenant_id=1, is_active=True)
        token2.save()

        active_tokens = APIToken.objects.filter(
            owner_id=1, tenant_id=1, is_active=True
        ).count()
        assert active_tokens == 1  # Solo uno puede estar activo

    def test_token_value_not_returned_after_creation(self):
        from apps.api_tokens.serializers import APITokenResponseSerializer
        # El serializer no debería exponer el token en gets subsecuentes
        # Este test describe que el token plain text no está en el serializer de GET
        import inspect
        source = inspect.getsource(APITokenResponseSerializer)
        # El token value no debe aparecer en el serializer de respuesta normal
        # (solo en la respuesta de creación)
        assert "token" not in [
            field for field in APITokenResponseSerializer().fields
            if field != "created_at"
        ]
```

---

## Python / FastAPI

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_process_endpoint_requires_valid_token():
    # La app no existe aún — ImportError (RED)
    from app.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/process",
            headers={"Authorization": "Bearer invalid-token"}
        )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_process_endpoint_returns_429_when_rate_limited():
    from app.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Enviar muchos requests para triggear rate limit
        for _ in range(100):
            await client.post(
                "/api/v1/process",
                headers={"Authorization": "Bearer valid-test-token"}
            )
        response = await client.post(
            "/api/v1/process",
            headers={"Authorization": "Bearer valid-test-token"}
        )
    assert response.status_code == 429
    assert "retry_after" in response.json()
```

---

## Node / TypeScript (Jest)

```typescript
// test-engineer escribe en RED — el módulo no existe aún

describe('AuthService - Registration', () => {
  let authService: AuthService;  // Fallará en runtime si la clase no existe

  beforeEach(async () => {
    const module = await Test.createTestingModule({
      providers: [AuthService],
    }).compile();
    authService = module.get<AuthService>(AuthService);
  });

  it('should hash password before storing', async () => {
    const result = await authService.register({
      email: 'test@example.com',
      password: 'Secret123!'
    });
    // Si authService no existe: TypeError (RED) — correcto
    expect(result.password).not.toBe('Secret123!');
  });

  it('should throw on duplicate email', async () => {
    await authService.register({ email: 'dup@example.com', password: 'pass' });
    await expect(
      authService.register({ email: 'dup@example.com', password: 'pass' })
    ).rejects.toThrow();
  });
});

// Integration test con supertest
describe('POST /api/auth/register', () => {
  it('returns 201 with valid data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'Secret123!' });
    // Si el endpoint no existe: 404 != 201 (RED) — correcto
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('email', 'test@example.com');
  });
});
```

---

## Señales de un test mal escrito en RED

```python
# ❌ Test que siempre pasa aunque no haya código
def test_algo():
    assert True

# ❌ Test que prueba la implementación, no el comportamiento
def test_uses_bcrypt():
    import bcrypt  # No nos importa cómo se hashea, sino que se hashea

# ❌ Test tan amplio que no documenta nada
def test_registro():
    # hace 10 cosas distintas
    ...

# ✅ Test que falla por razón correcta y documenta un comportamiento claro
@pytest.mark.django_db
def test_registration_with_valid_email_creates_unverified_user():
    from apps.users.models import User  # ImportError si no existe — RED válido
    User.objects.create_user(email="test@example.com", password="Secret123!")
    user = User.objects.get(email="test@example.com")
    assert user.is_verified is False  # El usuario comienza sin verificar
```
