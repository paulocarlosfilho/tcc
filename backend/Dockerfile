FROM python:3.10-slim

# Segurança: Criar usuário non-root
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY wait-for-it.sh .
RUN chmod +x wait-for-it.sh

# Garantir permissões para o usuário non-root
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["./wait-for-it.sh", "db", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]