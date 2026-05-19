#!/bin/sh
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

# Tenta conectar ao banco de dados usando psql.
# As variáveis de ambiente como PGPASSWORD, POSTGRES_USER, etc.,
# são injetadas pelo docker-compose.yml no contêiner da API.
until PGPASSWORD=$DB_PASSWORD psql -h "$host" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
# Executa o comando principal da aplicação (o CMD do Dockerfile)
exec $cmd
