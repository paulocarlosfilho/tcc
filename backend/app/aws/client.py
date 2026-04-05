import os
import boto3
from botocore.client import Config

def get_aws_client(service_name: str):
    """
    Cria um cliente para um serviço da AWS.
    Em ambiente de desenvolvimento, aponta para o LocalStack.
    """
    if os.getenv("ENVIRONMENT") == "development":
        # Configurações para o LocalStack
        aws_endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
        return boto3.client(
            service_name,
            endpoint_url=aws_endpoint_url,
            aws_access_key_id="test",
            aws_secret_access_key="test",
            region_name="us-east-1",
            config=Config(signature_version='s3v4')
        )
    else:
        # Em produção, o boto3 usará as credenciais do ambiente (ex: IAM role)
        return boto3.client(service_name)