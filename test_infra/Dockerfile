# Usar uma imagem Python slim como base
FROM python:3.10-slim

# Definir o diretório de trabalho
WORKDIR /app

# Instalar as dependências necessárias para os testes
RUN pip install requests docker

# Copiar o script executor e o plano de testes para dentro da imagem
# Usando o nome do arquivo que você criou: test_infra.py
COPY test_infra.py /app/test_infra.py
COPY test_infra.json /app/test_infra.json

# O comando que será executado quando o container iniciar
CMD ["python", "test_infra.py"]