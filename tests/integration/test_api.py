"""Basic API connectivity checks."""

import requests

base_url = "http://localhost:5000"


def _print_json_or_text(label, response):
	try:
		data = response.json()
		print(f"{label}:", data)
	except requests.exceptions.JSONDecodeError:
		print(f"{label}: Non-JSON response (status {response.status_code})")
		print(response.text[:200])

# Testar health
response = requests.get(f"{base_url}/health")
_print_json_or_text("Health", response)

# Listar tabelas (se existir rota)
response = requests.get(f"{base_url}/api/tables")
_print_json_or_text("Tabelas", response)

# Consultar alunos (precisamos criar as rotas primeiro)
# Por enquanto, vamos consultar direto no banco