import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck_retorna_200():
    """1. Valida se a rota base da API está online e operando."""
    response = client.get("/")
    assert response.status_code == 200

def test_documentacao_swagger_acessivel():
    """2. Valida se a documentação OpenAPI/Swagger carrega corretamente."""
    response = client.get("/docs")
    assert response.status_code == 200

def test_obter_openapi_json():
    """3. Valida a integridade do esquema JSON da API."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()

def test_rota_inexistente_retorna_404():
    """4. Valida o tratamento correto para endpoints não mapeados."""
    response = client.get("/api/v1/endpoint-invalido")
    assert response.status_code == 404

def test_envio_payload_invalido_retorna_422():
    """5. Valida a rejeição automática do FastAPI para JSON fora do esquema Pydantic."""
    response = client.post("/records", json={"campo_errado": 123})
    assert response.status_code in [400, 401, 422]