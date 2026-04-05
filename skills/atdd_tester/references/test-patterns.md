# Patrones de test por stack

Referencia para atdd_tester al escribir unit e integration tests
para cada historia construida por atdd_developer.

---

## Python / Django

### Estructura de carpetas esperada

```
apps/[módulo]/
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── __init__.py
    │   ├── test_models.py
    │   └── test_serializers.py
    └── integration/
        ├── __init__.py
        └── test_views.py
```

### Correr tests

```bash
# Todos los tests del módulo
pytest apps/[módulo]/tests/ -v --tb=short

# Solo unitarios
pytest apps/[módulo]/tests/unit/ -v

# Solo integración
pytest apps/[módulo]/tests/integration/ -v

# Con cobertura
pytest apps/[módulo]/tests/ --cov=apps/[módulo] --cov-report=term-missing
```

### Patrón: test de modelo

```python
import pytest
from apps.users.models import User

@pytest.mark.django_db
class TestUserModel:
    def test_email_is_username_field(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="Secret123!"
        )
        assert user.email == "test@example.com"
        assert user.USERNAME_FIELD == "email"

    def test_password_is_hashed(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="Secret123!"
        )
        assert user.password != "Secret123!"
        assert user.check_password("Secret123!")

    def test_duplicate_email_raises_error(self):
        User.objects.create_user(email="dup@example.com", password="pass")
        with pytest.raises(Exception):
            User.objects.create_user(email="dup@example.com", password="pass")
```

### Patrón: test de serializer

```python
import pytest
from apps.users.serializers import UserRegistrationSerializer

class TestUserRegistrationSerializer:
    def test_valid_data_passes(self):
        data = {"email": "test@example.com", "password": "Secret123!"}
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()

    def test_invalid_email_fails(self):
        data = {"email": "not-an-email", "password": "Secret123!"}
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_short_password_fails(self):
        data = {"email": "test@example.com", "password": "123"}
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
```

### Patrón: test de view (integration)

```python
import pytest
from django.test import Client

@pytest.mark.django_db
class TestRegistrationView:
    def setup_method(self):
        self.client = Client()

    def test_registration_returns_201(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        assert response.status_code == 201

    def test_registration_returns_email_in_response(self):
        response = self.client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        assert response.json()["email"] == "test@example.com"

    def test_duplicate_email_returns_400(self):
        data = {"email": "dup@example.com", "password": "Secret123!"}
        self.client.post("/api/auth/register/", data, content_type="application/json")
        response = self.client.post("/api/auth/register/", data, content_type="application/json")
        assert response.status_code == 400
```

### Patrón: test de email (locmem backend)

```python
import pytest
from django.core import mail
from django.test import Client

@pytest.mark.django_db
class TestEmailSending:
    def test_registration_sends_verification_email(self):
        client = Client()
        client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["test@example.com"]
        assert "verify" in mail.outbox[0].subject.lower()

    def test_verification_email_contains_token(self):
        client = Client()
        client.post(
            "/api/auth/register/",
            {"email": "test@example.com", "password": "Secret123!"},
            content_type="application/json"
        )
        body = mail.outbox[0].body
        assert "token=" in body or "verify/" in body
```

### Configuración de pytest (conftest.py)

```python
# conftest.py en la raíz del proyecto
import pytest
from django.conf import settings

@pytest.fixture(autouse=True)
def use_test_email_backend(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

---

## Python / FastAPI

### Correr tests

```bash
pytest tests/ -v --tb=short
```

### Patrón: test de endpoint con ASGI client

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register_returns_201():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "Secret123!"
        })
    assert response.status_code == 201
```

---

## Node / Express o NestJS

### Correr tests

```bash
# Jest
npm test

# Con cobertura
npm test -- --coverage

# Un archivo específico
npm test -- src/auth/auth.service.spec.ts
```

### Patrón: test de servicio (unit)

```typescript
describe('AuthService', () => {
  it('should hash password on registration', async () => {
    const result = await authService.register({
      email: 'test@example.com',
      password: 'Secret123!'
    });
    expect(result.password).not.toBe('Secret123!');
  });
});
```

### Patrón: test de endpoint (integration con supertest)

```typescript
import * as request from 'supertest';

describe('POST /api/auth/register', () => {
  it('should return 201 with valid data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'Secret123!' });
    expect(response.status).toBe(201);
    expect(response.body.email).toBe('test@example.com');
  });
});
```

---

## Calidad de código por stack

### Python
```bash
ruff check apps/          # linting
mypy apps/                # type checking
```

### Node / TypeScript
```bash
npm run lint              # eslint
npm run type-check        # tsc --noEmit
```
