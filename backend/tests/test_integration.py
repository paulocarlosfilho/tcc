import pytest
from httpx import AsyncClient
from app.main import app
from app.database import engine, Base
import asyncio
import time

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_full_user_flow():
    unique_suffix = int(time.time())
    username = f"user_{unique_suffix}"
    email = f"email_{unique_suffix}@test.com"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Testar Registro
        register_data = {
            "username": username,
            "email": email,
            "password": "strongpassword123",
            "role": "Paciente"
        }
        response = await ac.post("/auth/register", json=register_data)
        assert response.status_code == 201
        assert response.json()["username"] == username

        # 2. Testar Login
        login_data = {
            "username": username,
            "password": "strongpassword123"
        }
        response = await ac.post("/auth/login", data=login_data)
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert token is not None

        # 3. Testar Acesso Protegido (Quem sou eu)
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.get("/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["username"] == username

@pytest.mark.asyncio
async def test_invalid_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        login_data = {
            "username": "nonexistentuser",
            "password": "wrongpassword"
        }
        response = await ac.post("/auth/login", data=login_data)
        # O FastAPI/OAuth2 costuma retornar 401 ou 400 para credenciais inválidas dependendo da implementação
        assert response.status_code in [401, 400]

@pytest.mark.asyncio
async def test_duplicate_registration():
    unique_suffix = int(time.time()) + 1000 # Diferente do anterior
    username = f"dup_{unique_suffix}"
    email = f"dup_{unique_suffix}@test.com"
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        register_data = {
            "username": username,
            "email": email,
            "password": "password123",
            "role": "Médico"
        }
        # Primeiro registro
        await ac.post("/auth/register", json=register_data)
        # Segundo registro (mesmo email/user)
        response = await ac.post("/auth/register", json=register_data)
        assert response.status_code == 400
