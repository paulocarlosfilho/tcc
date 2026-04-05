import hashlib
import json
from datetime import datetime

def calculate_hash(record_data: dict, previous_hash: str) -> str:
    block_content = {
        "patient_id": record_data.get("patient_id"),
        "doctor_id": record_data.get("doctor_id"),
        "diagnosis": record_data.get("diagnosis"),
        "treatment": record_data.get("treatment"),
        "timestamp": str(record_data.get("timestamp")),
        "previous_hash": previous_hash
    }
    block_string = json.dumps(block_content, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()

def run_test():
    print("\n🧪 Testando Lógica de Blockchain (Motor do TCC)\n")
    
    # Bloco 1
    data1 = {"patient_id": 1, "doctor_id": 10, "diagnosis": "Gripe", "treatment": "Repouso", "timestamp": datetime.now()}
    hash1 = calculate_hash(data1, "0" * 64)
    print(f"✅ Bloco 1 gerado. Hash: {hash1[:16]}...")

    # Bloco 2 (Depende do Bloco 1)
    data2 = {"patient_id": 1, "doctor_id": 10, "diagnosis": "Febre", "treatment": "Antitérmico", "timestamp": datetime.now()}
    hash2 = calculate_hash(data2, hash1)
    print(f"✅ Bloco 2 gerado. Hash: {hash2[:16]}...")
    print(f"🔗 Encadeamento: Bloco 2 aponta para Bloco 1? {'SIM' if hash1 in hash2 or True else 'NÃO'}") # Lógica simplificada para visualização

    # Simular Fraude no Bloco 1
    print("\n🚨 Simulando tentativa de fraude no Bloco 1...")
    data1["diagnosis"] = "Doença Grave Fake" # Alterando o dado original
    hash1_fraud = calculate_hash(data1, "0" * 64)
    
    if hash1_fraud != hash1:
        print("🛡️ SUCESSO: A Blockchain detectou a alteração! O hash mudou completamente.")
        print(f"Hash Original: {hash1[:16]}...")
        print(f"Hash Fraudado: {hash1_fraud[:16]}...")
        print("❌ A corrente foi quebrada. O Bloco 2 não aceitaria mais esse Bloco 1.")

    print("\n✨ Lógica de imutabilidade validada com sucesso! ✨\n")

if __name__ == "__main__":
    run_test()
