# Makefile para o Projeto SUS Blockchain

.PHONY: help install run-api run-frontend run-local docker-up docker-down docker-build test test-integrity test-blockchain reset-db

help:
	@echo "Comandos disponíveis:"
	@echo "  make install         - Instala dependências do backend e frontend"
	@echo "  make run-local       - Roda API e Frontend localmente (necessita 2 terminais ou roda em background)"
	@echo "  make run-api         - Roda apenas a API localmente"
	@echo "  make run-frontend    - Roda apenas o Frontend localmente"
	@echo "  make docker-up       - Sobe todos os serviços via Docker Compose"
	@echo "  make docker-down     - Para todos os serviços do Docker Compose"
	@echo "  make docker-build    - Reconstrói as imagens do Docker"
	@echo "  make test            - Executa os testes unitários/integração"
	@echo "  make test-integrity  - Executa o super teste de integridade da blockchain"
	@echo "  make test-blockchain - Executa o teste de fluxo completo (5 passos) no Docker"
	@echo "  make reset-db        - Reseta o banco de dados local (SQLite)"

install:
	pip install -r requirements.txt
	cd frontend && npm install

run-api:
	python -m uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run-local:
	@echo "Iniciando API em background..."
	python -m uvicorn app.main:app --port 8000 &
	@echo "Iniciando Frontend..."
	cd frontend && npm run dev

docker-up:
	docker-compose up -d
	@echo "API rodando em: http://localhost:8000"
	@echo "Swagger disponível em: http://localhost:8000/docs"
	@echo "Frontend rodando em: http://localhost:3000"

docker-down:
	docker-compose down

docker-build:
	docker-compose build

test:
	pytest

test-integrity:
	python super_test.py

test-blockchain:
	docker-compose exec -T api python -m pytest -s tests/test_blockchain_flow.py

reset-db:
	docker-compose exec -T api python reset_db.py
