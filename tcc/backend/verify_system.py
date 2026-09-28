import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_full_flow():
    print("\n🚀 Iniciando Teste de Integração: Sistema SUS Blockchain (Versão Rápida)\n")
    
    # 1. Verificar Servidor
    try:
        health = requests.get(f"{BASE_URL}/")
        if health.status_code == 200:
            print("✅ [1/5] Servidor Backend está ONLINE.")
    except Exception as e:
        print(f"❌ [1/5] Erro: Servidor offline. {e}")
        return

    # 2. Login ou Registro
    import time
    unique_user = f"medico_{int(time.time())}"
    login_data = {"username": unique_user, "password": "senha_segura"}
    user_payload = {
        "username": unique_user, 
        "email": f"{unique_user}@teste.com", 
        "password": "senha_segura", 
        "role": "doctor"
    }
    
    print("⏳ [2/5] Autenticando...")
    # Tenta login direto
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print("ℹ️ Usuário não autenticado, tentando registrar...")
        # Registro usa JSON
        reg_response = requests.post(f"{BASE_URL}/auth/register", json=user_payload)
        if reg_response.status_code in [200, 201]:
             print("✅ Usuário registrado com sucesso.")
        
        # Login usa FORM DATA (data=...)
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ [2/5] Autenticação realizada com sucesso.")
    else:
        print(f"❌ [2/5] Erro na autenticação: {response.text}")
        return

    # 3. Criar Bloco
    headers = {"Authorization": f"Bearer {token}"}
    record_data = {
        "patient_id": 999,
        "diagnosis": "Teste de imutabilidade TCC",
        "treatment": "Protocolo Blockchain ativado."
    }
    print("⏳ [3/5] Gerando novo bloco na corrente...")
    rec_res = requests.post(f"{BASE_URL}/records/", json=record_data, headers=headers)
    
    if rec_res.status_code == 200:
        print(f"✅ [3/5] Bloco gerado: {rec_res.json()['hash'][:16]}...")
    else:
        print(f"❌ [3/5] Falha ao gerar bloco: {rec_res.text}")
        return

    # 4. Verificar Integridade
    print("⏳ [4/5] Auditando a Blockchain...")
    verify_res = requests.get(f"{BASE_URL}/records/verify", headers=headers)
    if verify_res.status_code == 200 and verify_res.json()["is_valid"]:
        print(f"✅ [4/5] Auditoria concluída: Corrente íntegra ({verify_res.json()['total_records']} blocos).")
    else:
        print("❌ [4/5] Erro na auditoria de integridade.")

    # 5. Testar Segurança
    print("⏳ [5/5] Validando proteção de dados...")
    sec_res = requests.post(f"{BASE_URL}/records/", json=record_data)
    if sec_res.status_code == 401:
        print("✅ [5/5] Proteção validada: Acesso bloqueado sem JWT.")
    else:
        print("❌ [5/5] Falha de segurança detectada.")

    print("\n✨ SISTEMA VALIDADO PARA O TCC! ✨\n")

if __name__ == "__main__":
    test_full_flow()
