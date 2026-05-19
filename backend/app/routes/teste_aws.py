from fastapi import APIRouter, HTTPException
from ..aws.client import get_aws_client
import logging

router = APIRouter(
    prefix="/aws-test",
    tags=["AWS Test"],
)
logger = logging.getLogger(__name__)

@router.post("/s3-upload", summary="Testa o upload de arquivo para o S3 com LocalStack")
def test_s3_upload():
    """
    Testa a conexão com o S3 do LocalStack criando um bucket e fazendo upload de um arquivo.
    """
    bucket_name = "meu-bucket-de-teste"
    file_content = "Olá, LocalStack S3!"
    file_key = "meu-arquivo-de-teste.txt"

    try:
        # 1. Obter o cliente S3
        s3_client = get_aws_client("s3")
        logger.info("Cliente S3 criado com sucesso.")

        # 2. Criar o bucket (operação idempotente)
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info(f"Bucket '{bucket_name}' criado ou já existente.")
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            logger.info(f"Bucket '{bucket_name}' já existe e pertence a você.")
            pass
        except Exception as e:
            logger.error(f"Erro ao criar o bucket '{bucket_name}': {e}")
            raise HTTPException(status_code=500, detail=f"Erro ao criar bucket: {e}")

        # 3. Fazer upload do arquivo
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_content.encode('utf-8')
        )
        logger.info(f"Arquivo '{file_key}' enviado para o bucket '{bucket_name}'.")

        return {
            "message": "Arquivo enviado com sucesso para o S3 (via LocalStack)!",
            "bucket": bucket_name,
            "file_key": file_key
        }
    except Exception as e:
        logger.error(f"Ocorreu um erro durante o teste do S3: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/s3-cleanup", summary="Limpa os recursos de teste do S3 (objeto e bucket)")
def test_s3_cleanup():
    """
    Exclui o objeto e o bucket criados pelo teste de upload do S3.
    """
    bucket_name = "meu-bucket-de-teste"
    file_key = "meu-arquivo-de-teste.txt"

    try:
        s3_client = get_aws_client("s3")
        logger.info("Cliente S3 criado para limpeza.")

        # 1. Excluir o objeto
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        logger.info(f"Objeto '{file_key}' excluído do bucket '{bucket_name}'.")

        # 2. Excluir o bucket
        s3_client.delete_bucket(Bucket=bucket_name)
        logger.info(f"Bucket '{bucket_name}' excluído com sucesso.")

        return {
            "message": "Recursos de teste (objeto e bucket) limpos com sucesso!",
            "bucket": bucket_name,
            "deleted_file": file_key
        }
    except Exception as e:
        logger.error(f"Ocorreu um erro durante a limpeza do S3: {e}")
        raise HTTPException(status_code=500, detail=str(e))