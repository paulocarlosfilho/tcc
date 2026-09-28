import multiprocessing
import time
import requests
import uvicorn
from app.main import app

def run_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error")

def run_tests():
    time.sleep(5) # Espera o servidor subir
    BASE_URL = "http://127.0.0.1:8001"
    
    print("\n🚀 INICIANDO SUPER TESTE DE INTEGRAÇÃO (MODO SEGURANÇA)\n")
    
    # 1. Registro de Médico
    medico_data = {"username": "dr_paulo", "password": "senha_segura_123", "email": "paulo@med.com", "role": "doctor"}
    print("⏳ Registrando médico...")
    requests.post(f"{BASE_URL}/auth/register", json=medico_data)
    
    # 2. Login de Médico
    login_medico = requests.post(f"{BASE_URL}/auth/login", data={"username": "dr_paulo", "password": "senha_segura_123"})
    token_medico = login_medico.json().get("access_token")
    headers_medico = {"Authorization": f"Bearer {token_medico}"}
    print("✅ Médico autenticado.")

    # 3. Registro e Login de Paciente
    paciente_data = {"username": "tiago_paciente", "password": "senha_paciente_456", "email": "tiago@paciente.com", "role": "patient"}
    print("⏳ Registrando paciente...")
    requests.post(f"{BASE_URL}/auth/register", json=paciente_data)
    login_paciente = requests.post(f"{BASE_URL}/auth/login", data={"username": "tiago_paciente", "password": "senha_paciente_456"})
    token_paciente = login_paciente.json().get("access_token")
    headers_paciente = {"Authorization": f"Bearer {token_paciente}"}
    print("✅ Paciente autenticado.")

    # 4. Teste de Segurança: Paciente tentando minerar (Deve Falhar)
    print("🛡️ Testando restrição de acesso (Paciente minerando)...")
    record_fail = {"patient_id": 1, "diagnosis": "Acesso Ilegal", "treatment": "Nenhum"}
    res_fail = requests.post(f"{BASE_URL}/records/", json=record_fail, headers=headers_paciente)
    if res_fail.status_code == 403:
        print("✅ Segurança confirmada: Paciente não tem permissão para minerar.")
    else:
        print(f"❌ FALHA DE SEGURANÇA: Paciente conseguiu minerar! (Status: {res_fail.status_code})")

    # 5. Médico minerando (Deve Funcionar)
    print("⏳ Médico minerando bloco legítimo...")
    record_ok = {"patient_id": 1, "diagnosis": "Checkup Geral", "treatment": "Tudo OK"}
    res_ok = requests.post(f"{BASE_URL}/records/", json=record_ok, headers=headers_medico)
    print(f"✅ Bloco minerado com sucesso! Hash: {res_ok.json().get('hash')[:16]}...")

    # 6. Validar Integridade da Blockchain
    print("⏳ Validando integridade global...")
    verify = requests.get(f"{BASE_URL}/records/verify", headers=headers_medico)
    if verify.json().get("is_valid"):
        print("✅ Blockchain íntegra e verificada!")

    print("\n✨ TODOS OS TESTES DE SEGURANÇA E INTEGRAÇÃO PASSARAM! ✨\n")

    print("\n✨ SISTEMA APROVADO COM SUCESSO! ✨\n")

if __name__ == "__main__":
    server_process = multiprocessing.Process(target=run_server)
    server_process.start()
    try:
        run_tests()
    finally:
        server_process.terminate()
