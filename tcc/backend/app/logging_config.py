import logging
import sys
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configuração de Logs Estruturados
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("sus_blockchain")

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para medir o tempo de resposta e logar cada requisição.
    Essencial para observabilidade em nível Sênior.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição chegando
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)
        
        # Log do tempo de resposta e status
        logger.info(
            f"Completed: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Time: {formatted_process_time}ms"
        )
        
        response.headers["X-Process-Time"] = formatted_process_time
        return response
