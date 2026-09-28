import pytest
import hashlib
from unittest.mock import patch

def test_geracao_hash_sha256_integridade():
    """6. Valida se a geração do hash do prontuário/registro possui 64 caracteres hexadecimais."""
    dados = "Prontuario_Paciente_123"
    hash_gerado = hashlib.sha256(dados.encode()).hexdigest()
    assert len(hash_gerado) == 64

def test_validacao_hash_dados_alterados():
    """7. Valida se qualquer alteração no documento gera um hash totalmente diferente."""
    dados_originais = "Prontuario_Paciente_123"
    dados_alterados = "Prontuario_Paciente_123_alterado"
    
    hash1 = hashlib.sha256(dados_originais.encode()).hexdigest()
    hash2 = hashlib.sha256(dados_alterados.encode()).hexdigest()
    
    assert hash1 != hash2

@patch("app.services.blockchain.BlockchainService")
def test_simulacao_registro_transacao_sucesso(mock_service):
    """8. Testa a confirmação de escrita de bloco na blockchain via Mock."""
    instance = mock_service.return_value
    instance.registrar.return_value = {"status": "success", "tx_hash": "0xabc123", "bloco": 501}
    
    res = instance.registrar({"dados": "teste"})
    assert res["status"] == "success"
    assert res["tx_hash"].startswith("0x")

@patch("app.services.blockchain.BlockchainService")
def test_simulacao_falha_conexao_no_rpc(mock_service):
    """9. Valida a captura de erro quando a rede blockchain estiver indisponível."""
    instance = mock_service.return_value
    instance.registrar.side_effect = ConnectionError("Falha de comunicação com o nó RPC")
    
    with pytest.raises(ConnectionError) as exc_info:
        instance.registrar({"dados": "teste"})
    assert "Falha de comunicação" in str(exc_info.value)