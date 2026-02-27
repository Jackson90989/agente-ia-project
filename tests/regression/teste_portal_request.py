#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simular login e verificar resposta exata que o portal recebe"""

import requests
import json
from datetime import datetime, timedelta
import jwt

# Configurar
API_URL = "http://localhost:5000/api"
SECRET_KEY = "dev-secret"

print("=" * 80)
print("TESTE: Simular acesso do portal ao endpoint de requerimentos")
print("=" * 80)

# Step 1: Login
print("\n1⃣  Fazendo login para obter token JWT...")

payload_login = {
    "matricula": "2024/00001",
    "senha": "senha123"
}

response = requests.post(
    f"{API_URL}/auth/login",
    json=payload_login
)

print(f"   Status: {response.status_code}")
dados_login = response.json()
print(f"   Resposta: {json.dumps(dados_login, indent=2)[:200]}...")

if response.status_code != 200:
    print(" Falha no login!")
    exit(1)

token = dados_login.get('token')
# Tentar obter aluno_id de diferentes locais
aluno_id = dados_login.get('aluno_id') or dados_login.get('aluno', {}).get('id')

print(f"    Token obtido: {token[:30]}...")
print(f"    Aluno ID: {aluno_id}")

if not aluno_id:
    print(" Não consegui obter aluno_id da resposta de login!")
    print(f"Resposta completa: {json.dumps(dados_login, indent=2)}")
    exit(1)

# Step 2: Buscar requerimentos com token
print(f"\n2⃣  Buscando requerimentos com token JWT de autenticação...")

response = requests.get(
    f"{API_URL}/auth/requerimentos/{aluno_id}",
    headers={
        'Authorization': f'Bearer {token}'
    }
)

print(f"   Status: {response.status_code}")
dados_req = response.json()

requerimentos = dados_req.get('requerimentos', [])
print(f"   Total de requerimentos: {len(requerimentos)}")

# Procurar por declarações
declaracoes = [r for r in requerimentos if r['tipo'] == 'declaracao']
print(f"   Total de declarações: {len(declaracoes)}")

print(f"\n Todas as declarações do aluno:")
for req in declaracoes:
    print(f"\n   Requerimento #{req['id']}")
    print(f"    Tipo: {req['tipo']}")
    print(f"    Status: {req['status']}")
    print(f"    Declaração tipo: {req.get('declaracao_info', {}).get('tipo')}")
    
    pdf_path = req.get('declaracao_info', {}).get('pdf_path')
    if pdf_path:
        print(f"     PDF path: {pdf_path}")
        print(f"    Download link: {API_URL}/requerimentos/{req['id']}/pdf")
        print(f"    Visualizar link: {API_URL}/requerimentos/{req['id']}/visualizar-pdf")
    else:
        print(f"     PDF path: None")

# Step 3: Fazer request não autenticado como o portal pode fazer
print(f"\n3⃣  Buscando requerimentos SEM token (como portal faz se token expirou)...")

response = requests.get(
    f"{API_URL}/auth/requerimentos/{aluno_id}"
)

print(f"   Status: {response.status_code}")
dados_req = response.json()

requerimentos = dados_req.get('requerimentos', [])
print(f"   Total de requerimentos: {len(requerimentos)}")

declaracoes = [r for r in requerimentos if r['tipo'] == 'declaracao']
print(f"   Total de declarações: {len(declaracoes)}")

if declaracoes:
    print(f"\n   Última declaração:")
    req = declaracoes[-1]
    print(f"    ID: {req['id']}")
    print(f"    PDF path: {req.get('declaracao_info', {}).get('pdf_path')}")
