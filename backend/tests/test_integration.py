import pytest
from httpx import AsyncClient
import time

@pytest.mark.asyncio
async def test_full_user_flow(client: AsyncClient):
    unique_suffix = int(time.time())
    username = f"user_{unique_suffix}"
    email = f"email_{unique_suffix}@test.com"
    
    # 1. Testar Registro
    register_data = {
        "username": username,
        "email": email,
        "password": "strongpassword123",
        "role": "Paciente"
    }
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 201, response.text
    assert response.json()["username"] == username

    # 2. Testar Login
    login_data = {
        "username": username,
        "password": "strongpassword123"
    }
    response = await client.post("/auth/login", data=login_data)
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert token is not None

    # 3. Testar Acesso Protegido (Quem sou eu)
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/auth/me", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["username"] == username

@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    login_data = {
        "username": "nonexistentuser",
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", data=login_data)
    # O FastAPI/OAuth2 costuma retornar 401 ou 400 para credenciais inválidas dependendo da implementação
    assert response.status_code in [401, 400], response.text

@pytest.mark.asyncio
async def test_duplicate_registration(client: AsyncClient):
    unique_suffix = int(time.time()) + 1000 # Diferente do anterior
    username = f"dup_{unique_suffix}"
    email = f"dup_{unique_suffix}@test.com"
    
    register_data = {
        "username": username,
        "email": email,
        "password": "password123",
        "role": "Médico"
    }
    # Primeiro registro
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 201, response.text
    
    # Segundo registro (mesmo email/user)
    response = await client.post("/auth/register", json=register_data)
    assert response.status_code == 400, response.text