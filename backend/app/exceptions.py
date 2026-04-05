from fastapi import Request, status
from fastapi.responses import JSONResponse
from .logging_config import logger

async def global_exception_handler(request: Request, exc: Exception):
    """
    Captura qualquer erro não tratado no sistema e retorna uma resposta padronizada.
    Isso impede que o usuário veja erros internos (Stack Traces) e mantém a segurança.
    """
    logger.error(f"Erro inesperado na rota {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Ocorreu um erro interno no servidor de saúde. Nossa equipe técnica foi notificada.",
            "type": "InternalServerError"
        }
    )
