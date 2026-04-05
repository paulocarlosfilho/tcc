import asyncio
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .database import engine, Base
from .exceptions import global_exception_handler
from .logging_config import LoggingMiddleware, logger
from .routes import auth, records, test_aws, test_aws, test_aws, test_aws

description = """
🚀 **SUS Blockchain API** - Sistema de Prontuário Médico Profissional com Integridade Blockchain.

Esta API foi construída com **FastAPI** para oferecer uma experiência de gestão de saúde robusta, segura e em total conformidade com os princípios da **LGPD**.

### O que você será capaz de fazer:

*   **Gestão de Profissionais**: Registrar médicos e gerenciar permissões de acesso.
*   **Prontuários Imutáveis**: Criar registros de saúde onde cada novo bloco é encadeado ao anterior via SHA-256.
*   **Integridade Blockchain**: 
    *   Verificar a validade de toda a corrente de dados.
    *   Garantir que nenhum registro foi alterado ou deletado indevidamente.
*   **Segurança Avançada**: Autenticação via JWT (JSON Web Tokens) com proteção de rotas sensíveis.
*   **Conformidade LGPD**: Rastreabilidade total de quem criou cada registro (Auditoria).

---
"""

app = FastAPI(
    title="SUS Blockchain API 🏥⛓️",
    description=description,
    version="2.0.0",
    contact={
        "name": "Suporte Técnico SUS Blockchain",
        "url": "https://github.com/seu-repositorio",
    },
    license_info={
        "name": "MIT License",
    },
    openapi_tags=[
        {
            "name": "auth",
            "description": "🔐 **Segurança em primeiro lugar**. Obtenha seu token de acesso para desbloquear as operações.",
        },
        {
            "name": "health records",
            "description": "🩺 **Gestão de Prontuários**. Criação e consulta de registros médicos com garantia de imutabilidade.",
        },
    ]
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

# Middleware para Headers de Segurança
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Configuração de CORS para o Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra o Middleware de Observabilidade
app.add_middleware(LoggingMiddleware)

# Registra o Handler Global de Exceções
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth.router)
app.include_router(records.router)
app.include_router(test_aws.router)
app.include_router(test_aws.router)
app.include_router(test_aws.router)
app.include_router(test_aws.router)

@app.on_event("startup")
async def startup():
    # Tenta conectar ao banco com retentativas (resiliência sênior)
    retries = 5
    while retries > 0:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Conexão com o banco de dados estabelecida e tabelas criadas.")
            break
        except Exception as e:
            retries -= 1
            logger.warning(f"⚠️ Erro ao conectar no banco. Tentativas restantes: {retries}. Erro: {e}")
            if retries == 0:
                logger.error("❌ Não foi possível conectar ao banco de dados após várias tentativas.")
                raise e
            await asyncio.sleep(3)

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API do SUS Blockchain",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}