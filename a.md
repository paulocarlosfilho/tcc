# Tutorial: Integrando a Aplicação com LocalStack

Este tutorial guia você pelo processo de inicialização da aplicação e verificação da integração com o LocalStack para simular os serviços da AWS localmente.

## Pré-requisitos

- Docker e Docker Compose instalados.
- AWS CLI instalado e configurado (pode ser um perfil `default` básico, pois usaremos um endpoint local).

## Passo 1: Construir e Iniciar os Contêineres

Com todas as alterações salvas e os novos arquivos criados, o primeiro passo é construir as imagens Docker para cada serviço e iniciar os contêineres.

Execute o seguinte comando na raiz do seu projeto:

```bash
docker-compose up --build
```

- `--build`: Força a reconstrução das imagens. Isso é importante para garantir que as novas dependências (como o `boto3`) e as alterações no código sejam incluídas.
- `up`: Inicia os serviços definidos no `docker-compose.yml` (`localstack`, `db`, `api`, `frontend`).

Você verá um grande volume de logs de todos os serviços sendo iniciados. Aguarde até que os logs se estabilizem.

## Passo 2: Testar a Rota de Upload para o S3

Agora que a API está em execução e configurada para falar com o LocalStack, vamos chamar a rota de teste que criamos para verificar se o upload para o S3 funciona.

Você pode fazer isso de duas maneiras:

### A) Usando o `curl` no terminal

Abra um novo terminal e execute o seguinte comando:

```bash
curl -X POST http://localhost:8000/aws-test/s3-upload
```

### B) Usando a documentação interativa da API (Swagger)

Abra seu navegador e acesse: [http://localhost:8000/docs](http://localhost:8000/docs)

1.  Encontre a seção **AWS Test**.
2.  Clique no endpoint `/aws-test/s3-upload`.
3.  Clique em "Try it out" e depois em "Execute".

### Resultado Esperado

Em ambos os casos, você deve receber uma resposta `200 OK` com um JSON semelhante a este:

```json
{
  "message": "Arquivo enviado com sucesso para o S3 (via LocalStack)!",
  "bucket": "meu-bucket-de-teste",
  "file_key": "meu-arquivo-de-teste.txt"
}
```

Isso confirma que sua API conseguiu se comunicar com o serviço S3 do LocalStack, criar um bucket e enviar um arquivo.

## Passo 3: Verificar o Arquivo no S3 do LocalStack

A etapa final é confirmar que o arquivo realmente existe no bucket S3 que o LocalStack está gerenciando. Para interagir com o LocalStack, usaremos a `aws-cli`, mas apontando para o endpoint local.

Abra outro terminal e execute o seguinte comando para listar o conteúdo do bucket:

```bash
aws s3 ls s3://meu-bucket-de-teste --endpoint-url=http://localhost:4566
```

- `--endpoint-url=http://localhost:4566`: Este é o parâmetro crucial que direciona o comando da AWS CLI para o seu contêiner LocalStack em vez da AWS real.

Você deverá ver o arquivo que a API enviou: