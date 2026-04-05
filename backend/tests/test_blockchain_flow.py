import pytest
import httpx
import asyncio
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

@pytest.mark.asyncio
async def test_full_blockchain_flow():
    # Retry logic no teste para aguardar o Uvicorn estar pronto
    max_retries = 5
    client = httpx.AsyncClient(base_url=API_URL, timeout=30.0)
    
    connected = False
    for i in range(max_retries):
        try:
            await client.get("/")
            connected = True
            break
        except Exception:
            print(f"Aguardando API subir... tentativa {i+1}/{max_retries}")
            await asyncio.sleep(2)
    
    if not connected:
        pytest.fail("A API não respondeu no endereço 127.0.0.1:8000")

    async with client:
        # 1. AUTENTICAÇÃO
        # Criar um médico para o teste
        username = f"medico_teste_{int(datetime.now().timestamp())}"
        await client.post("/auth/register", json={
            "username": username,
            "email": f"{username}@sus.gov.br",
            "password": "senha_segura_123",
            "role": "doctor"
        })
        
        # Login para obter JWT
        login_res = await client.post("/auth/login", data={
            "username": username,
            "password": "senha_segura_123"
        })
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("\n[OK] 1. Autenticação JWT funcionando.")

        # 2 & 3. REGISTRO DE BLOCO E CRIPTOGRAFIA (SHA-256)
        # Primeiro Registro
        rec1_res = await client.post("/records/", json={
            "patient_id": 123,
            "diagnosis": "Gripe Comum",
            "treatment": "Repouso e Hidratação"
        }, headers=headers)
        assert rec1_res.status_code == 200
        rec1 = rec1_res.json()
        assert "hash" in rec1
        print(f"[OK] 2. Primeiro bloco criado. Hash: {rec1['hash'][:10]}...")

        # 4. ENCADEAMENTO (CHURNING)
        # Segundo Registro (deve herdar o hash do primeiro)
        rec2_res = await client.post("/records/", json={
            "patient_id": 123,
            "diagnosis": "Retorno - Melhora",
            "treatment": "Alta médica"
        }, headers=headers)
        assert rec2_res.status_code == 200
        rec2 = rec2_res.json()
        
        # VALIDAÇÃO CRÍTICA: O previous_hash do segundo bloco DEVE ser o hash do primeiro
        assert rec2["previous_hash"] == rec1["hash"]
        print(f"[OK] 3 & 4. Encadeamento confirmado! Previous Hash do Bloco 2 coincide com Bloco 1.")

        # 5. PERSISTÊNCIA E VERIFICAÇÃO DE INTEGRIDADE
        verify_res = await client.get("/records/verify", headers=headers)
        assert verify_res.status_code == 200
        status = verify_res.json()
        assert status["is_valid"] is True
        print(f"[OK] 5. Integridade da rede verificada. Total de blocos: {status['total_records']}")

if __name__ == "__main__":
    asyncio.run(test_full_blockchain_flow())
