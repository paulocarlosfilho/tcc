import json
import os
import socket
import sys
import time
import requests
import docker

# --- Funções de Teste ---

def check_port(target, port, timeout=3):
    """Verifica se uma porta está aberta em um host."""
    try:
        with socket.create_connection((target, port), timeout=timeout):
            return True, f"Porta {port} está aberta em '{target}'."
    except Exception as e:
        return False, f"Falha ao conectar em {target}:{port}. Erro: {e}"

def http_request(method, target, expectedStatusCode, headers=None, body=None, expectJsonField=None, expectedHeaders=None, **kwargs):
    """Executa uma requisição HTTP e valida o resultado."""
    try:
        # Determina o serviço de destino com base na porta
        if ":3000" in target:
            target_url = target.replace("localhost", "frontend")
        else:
            target_url = target.replace("localhost", "api")

        response = requests.request(method, target_url, headers=headers, json=body if isinstance(body, dict) else None, data=body if isinstance(body, str) else None, timeout=10)
        
        # Validação do Status Code
        if response.status_code != expectedStatusCode:
            return False, f"{method} {target_url} retornou {response.status_code} (Esperado: {expectedStatusCode}). Resposta: {response.text[:100]}", None

        # Validação de Campo no JSON de resposta
        if expectJsonField:
            try:
                json_response = response.json()
                if expectJsonField not in json_response:
                    return False, f"Campo esperado '{expectJsonField}' não encontrado na resposta JSON.", None
                # Retorna o valor do campo para ser usado depois (ex: token)
                return True, f"Status {response.status_code} OK e campo '{expectJsonField}' encontrado.", json_response[expectJsonField]
            except json.JSONDecodeError:
                return False, "Falha ao decodificar a resposta JSON.", None

        # Validação de Cabeçalhos de Resposta
        if expectedHeaders:
            for key, value in expectedHeaders.items():
                if response.headers.get(key) != value:
                    return False, f"Cabeçalho '{key}' com valor '{response.headers.get(key)}' não corresponde ao esperado '{value}'.", None
            return True, f"Status {response.status_code} OK e cabeçalhos de segurança validados.", None

        return True, f"{method} {target_url} retornou {response.status_code} (Esperado: {expectedStatusCode}).", None

    except requests.RequestException as e:
        return False, f"Falha na requisição para {target_url}. Erro: {e}", None

def docker_exec(container, command, expectedOutput, **kwargs):
    """Executa um comando dentro de um container Docker."""
    try:
        client = docker.from_env()
        container_name = f"blockchain_{container}"
        container_obj = client.containers.get(container_name)
        exit_code, output = container_obj.exec_run(cmd=command)
        output_str = output.decode('utf-8').strip()
        
        if expectedOutput in output_str:
            return True, f"Comando '{command}' em '{container_name}' retornou a saída esperada."
        else:
            return False, f"Comando '{command}' em '{container_name}' não retornou '{expectedOutput}'. Saída: '{output_str}'"
    except docker.errors.NotFound:
        return False, f"Container '{container_name}' não encontrado."
    except Exception as e:
        return False, f"Erro ao executar docker exec: {e}"

# --- Engine de Testes ---

def run_tests(test_file):
    """Lê o arquivo JSON e executa os testes."""
    try:
        with open(test_file, 'r') as f:
            suite = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de teste '{test_file}' não encontrado.")
        sys.exit(1)

    print(f"Iniciando suíte de testes: {suite['testSuite']}\n")
    
    print("Aguardando 10 segundos para os serviços dependentes iniciarem...")
    time.sleep(10)

    results = {"passed": 0, "failed": 0}
    auth_token = None

    # Ordena os testes para garantir que a autenticação ocorra primeiro
    all_tests = sorted(suite['tests'], key=lambda t: t.get('testId') == 'API-AUTH-001', reverse=True)

    for test in all_tests:
        if not test.get("enabled", True):
            continue

        print(f"Executando: [{test['testId']}] {test['testName']}...")
        
        success = True
        for step in test['steps']:
            action = step['action']
            params = {k: v for k, v in step.items() if k != 'action'}

            # Injeta o token de autenticação nos headers
            if 'headers' in params and auth_token:
                for h_key, h_value in params['headers'].items():
                    if h_value == "${AUTH_TOKEN}":
                        params['headers'][h_key] = f"Bearer {auth_token}"
            
            action_function = {
                'checkPort': check_port,
                'httpRequest': http_request,
                'dockerExec': docker_exec
            }.get(action)

            if not action_function:
                print(f"  -> Ação '{action}' desconhecida. Pulando.")
                continue

            # A função http_request pode retornar um valor (o token)
            step_success, message, return_value = (action_function(**params) + (None,))[:3]

            print(f"  -> {message}")
            if not step_success:
                success = False
                break
            
            # Se for o teste de autenticação, armazena o token
            if test['testId'] == 'API-AUTH-001' and return_value:
                auth_token = return_value
                print(f"  -> Token de autenticação capturado com sucesso!")

        if success:
            print(f"  [PASSOU]\n")
            results["passed"] += 1
        else:
            print(f"  [FALHOU]\n")
            results["failed"] += 1

    print("-" * 30)
    print(f"Resultado: {results['passed']} passaram, {results['failed']} falharam.")
    print("-" * 30)

    if results["failed"] > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests("/app/test_infra.json")