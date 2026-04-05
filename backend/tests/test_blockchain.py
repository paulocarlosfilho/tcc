from app.services.blockchain import BlockchainService
from datetime import datetime

def test_calculate_hash():
    record_data = {
        "patient_id": 1,
        "doctor_id": 2,
        "diagnosis": "Gripe",
        "treatment": "Repouso",
        "timestamp": datetime(2024, 1, 1, 12, 0, 0)
    }
    previous_hash = "0" * 64
    
    hash1 = BlockchainService.calculate_hash(record_data, previous_hash)
    hash2 = BlockchainService.calculate_hash(record_data, previous_hash)
    
    # Hashes devem ser determinísticos (iguais para os mesmos dados)
    assert hash1 == hash2
    assert len(hash1) == 64

def test_verify_chain_valid():
    class MockRecord:
        def __init__(self, previous_hash, hash):
            self.previous_hash = previous_hash
            self.hash = hash

    r1 = MockRecord(None, "hash1")
    r2 = MockRecord("hash1", "hash2")
    r3 = MockRecord("hash2", "hash3")
    
    assert BlockchainService.verify_chain([r1, r2, r3]) == True

def test_verify_chain_invalid():
    class MockRecord:
        def __init__(self, previous_hash, hash):
            self.previous_hash = previous_hash
            self.hash = hash

    r1 = MockRecord(None, "hash1")
    r2 = MockRecord("hash_errado", "hash2") # Quebra a corrente
    
    assert BlockchainService.verify_chain([r1, r2]) == False
