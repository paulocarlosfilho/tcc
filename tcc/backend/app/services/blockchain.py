import hashlib
import json
from datetime import datetime
from typing import Optional

class BlockchainService:
    @staticmethod
    def calculate_hash(record_data: dict, previous_hash: Optional[str]) -> str:
        """
        Calcula o hash SHA-256 de um registro médico.
        Inclui o hash do registro anterior para garantir o encadeamento.
        """
        # Criamos um dicionário ordenado para garantir que o hash seja sempre o mesmo para os mesmos dados
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

    @staticmethod
    def verify_chain(records: list) -> bool:
        """
        Verifica se a corrente de registros médicos é válida.
        Útil para auditorias no TCC.
        """
        for i in range(1, len(records)):
            current = records[i]
            previous = records[i-1]
            
            # O previous_hash do atual deve ser igual ao hash do anterior
            if current.previous_hash != previous.hash:
                return False
                
        return True
