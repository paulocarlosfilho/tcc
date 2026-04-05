# SUS Blockchain: Prontuário Médico Nacional Imutável 🏥⛓️

O **SUS Blockchain** é uma evolução digital do Sistema Único de Saúde, integrando a segurança da tecnologia Blockchain para garantir a imutabilidade e a transparência dos registros de saúde dos cidadãos brasileiros.

## 🎯 Objetivo do Projeto (TCC)
Este trabalho demonstra a viabilidade técnica de utilizar uma rede de registros distribuídos para proteger o histórico clínico do paciente, impedindo fraudes, alterações retroativas e garantindo que o prontuário acompanhe o cidadão em qualquer unidade de saúde do país, em total conformidade com a **LGPD (Lei Geral de Proteção de Dados)**.

---

## 🛠️ Tecnologias Utilizadas (Stack Sênior)
- **Backend:** Python FastAPI (Async) + SQLAlchemy 2.0.
- **Banco de Dados:** PostgreSQL 15 (Persistência robusta).
- **Frontend:** React (Vite) + Tailwind CSS + Lucide Icons.
- **Blockchain:** SHA-256 Chaining para imutabilidade.
- **Testes:** Pytest (Backend) + Vitest/Testing Library (Frontend).
- **CI/CD:** GitHub Actions (Automação de Testes e Builds).
- **DevOps:** Docker & Docker-Compose com **Hardening de Segurança**.

---

## 📂 Estrutura do Projeto
O sistema segue uma separação clara de responsabilidades (Clean Architecture):
```text
/
├── backend/            # API FastAPI, Lógica de Blockchain e Modelos
│   ├── app/            # Código fonte (Routes, Services, Models)
│   ├── tests/          # Testes de integração e unitários
│   └── Dockerfile      # Imagem Hardened (Non-root user)
├── aws/                # Infraestrutura Terraform para ECS Fargate, ALB, ECR e RDS
├── frontend/           # Interface React com Vite
│   ├── src/            # Componentes, Hooks e Testes
│   └── Dockerfile      # Servidor Nginx seguro (Non-root)
└── docker-compose.yml  # Orquestração de DB, API e Frontend
```

---

## 🛡️ Diferenciais de Segurança & Cloud-Ready
Este projeto foi construído seguindo os padrões de segurança da **AWS Security Specialist**:
- **Non-Root Containers:** Todos os serviços rodam com usuários sem privilégios administrativos.
- **Isolamento de Segredos:** Uso de variáveis de ambiente (.env) para chaves e URLs.
- **CORS Hardened:** Configuração restrita entre frontend e backend.
- **Imutabilidade Real:** Verificação constante da integridade da cadeia de blocos.

---

## 🚀 Entrega Profissional

| Funcionalidade | Requisito Básico (Comum) | Entrega (Este Projeto Sênior) |
| :--- | :--- | :--- |
| **Arquitetura** | Script único ou rotas simples | **Service Layer Pattern**: Separação total de responsabilidades. |
| **Banco de Dados** | SQLite ou Dados em Memória | **PostgreSQL 15**: Banco relacional de alta disponibilidade. |
| **Segurança** | Autenticação simples | **JWT + bcrypt + Docker Non-Root**: Proteção em múltiplas camadas. |
| **TDD** | Sem testes | **Full Coverage**: Testes no Backend (Pytest) e Frontend (Vitest). |
| **UX/UI** | Interface genérica | **Identidade SUS Oficial**: Foco total em acessibilidade e confiança. |

---

## 🚀 CI/CD e Qualidade

O projeto conta com uma pipeline de Integração Contínua (CI) via **GitHub Actions** que automatiza:
- **Testes de Backend:** Execução de testes unitários com Pytest.
- **Testes de Frontend:** Testes de componentes com Vitest e Testing Library.
- **Docker Build Check:** Verificação de integridade dos Dockerfiles em cada Push/PR.
- **Deploy AWS:** Workflow manual para provisionar infraestrutura e publicar containers no ECS Fargate.

---

## ☁️ Deploy na AWS: Otimização de Custos (S3 + CloudFront para Frontend)

O projeto agora possui uma pasta `aws/` com infraestrutura como código em **Terraform**. Realizamos otimizações significativas para reduzir os custos, especialmente para o contexto de um TCC, mantendo a API robusta no Fargate e movendo o Frontend para serviços de hospedagem estática.

### Arquitetura Otimizada:
- **Frontend (S3 + CloudFront):** O frontend é agora hospedado em um bucket **Amazon S3** e distribuído globalmente via **Amazon CloudFront**. Isso proporciona alta performance, baixa latência e, crucialmente, um custo significativamente menor, muitas vezes se encaixando no nível gratuito da AWS para tráfego básico.
- **Backend (ECS Fargate):** A API continua rodando em um cluster **ECS Fargate**, garantindo escalabilidade e alta disponibilidade para as operações da blockchain.
- **ECR:** Repositório **ECR** para armazenar as imagens Docker da API.
- **Application Load Balancer (ALB):** Um único ALB para expor a API. O Frontend agora é exposto diretamente pelo CloudFront.
- **RDS PostgreSQL:** Banco de dados **RDS PostgreSQL** para persistência em produção.

### Perfil econômico para TCC
- **Sem NAT Gateway** para evitar o principal custo fixo de rede.
- **Um único ALB** para reduzir custo mensal de balanceamento.
- **Tasks do ECS em subnets públicas** com IP público, mantendo o banco em subnets privadas.
- **RDS pequeno** para manter o projeto apresentável sem custo enterprise.
- **Frontend em S3/CloudFront:** Aproveitando o nível gratuito e a eficiência desses serviços para um custo quase zero ou muito reduzido para o frontend.

### Arquivos principais
- [main.tf](file:///c:/Users/paulo/Documents/Projetos/Teste/aws/main.tf)
- [variables.tf](file:///c:/Users/paulo/Documents/Projetos/Teste/aws/variables.tf)
- [outputs.tf](file:///c:/Users/paulo/Documents/Projetos/Teste/aws/outputs.tf)
- [terraform.tfvars.example](file:///c:/Users/paulo/Documents/Projetos/Teste/aws/terraform.tfvars.example)
- [deploy-fargate.yml](file:///c:/Users/paulo/Documents/Projetos/Teste/.github/workflows/deploy-fargate.yml)

### Fluxo recomendado
```bash
cd aws
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
```

Depois do primeiro `apply`, publique as imagens da API no ECR usando a workflow de deploy do GitHub Actions.
O frontend será acessível através do domínio do CloudFront e a API em `http://DNS_DO_ALB:8000`.

---

---

## 🛠️ Como Executar

### 1. Subir o Ambiente Completo (Docker)
Certifique-se de ter o **Docker** instalado e execute:
```bash
make docker-up
```
Ou manualmente:
```bash
docker-compose up --build -d
```

### 2. Acessar os Serviços
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Banco de Dados:** Porta 5432 (PostgreSQL)

---

## 🧪 Como Testar

### Testes do Backend (Blockchain & API)
```bash
make test-blockchain
```

### Testes do Frontend (Componentes React)
```bash
cd frontend && npm run test:run
```

---

## 🧠 Como o Sistema Funciona? (Fluxo Técnico)
1.  **Autenticação:** O usuário realiza login e recebe um token **JWT**.
2.  **Registro de Bloco:** O sistema captura o **Hash do bloco anterior** no PostgreSQL.
3.  **Criptografia:** O registro é processado pelo algoritmo **SHA-256** junto ao hash anterior.
4.  **Encadeamento:** O novo Hash sela o bloco, garantindo que o histórico não possa ser alterado sem quebrar a rede.
5.  **Auditabilidade:** Qualquer cidadão ou profissional pode verificar a validade da rede em tempo real.

---

*Trabalho focado em Inovação Tecnológica na Saúde Pública.*
