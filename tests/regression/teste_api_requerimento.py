#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste de criação de requerimento via API"""

import requests
import json

API_URL = "http://localhost:5000/api"

# Testar criação de requerimento de declaração
print("=" * 80)
print("TESTE: Criar requerimento de declaração via API")
print("=" * 80)

payload = {
    "aluno_id": 1,
    "declaracao_tipo": "frequencia"
}

print(f"\nEnviando POST /api/requerimentos/declaracao com payload:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(
        f"{API_URL}/requerimentos/declaracao",
        json=payload,
        timeout=10
    )
    
    print(f"\nStatus: {response.status_code}")
    dados = response.json()
    print(f"\nResposta JSON:")
    print(json.dumps(dados, indent=2, ensure_ascii=False))
    
    # Verificar se pdf_path está presente
    if response.status_code == 201:
        req = dados
        if req.get('declaracao_info') and req['declaracao_info'].get('pdf_path'):
            print(f"\n PDF PATH ENCONTRADO: {req['declaracao_info']['pdf_path']}")
        else:
            print(f"\n PDF PATH NÃO ENCONTRADO")
            print(f"   declaracao_info: {req.get('declaracao_info')}")
except Exception as e:
    print(f"\n Erro: {e}")

# Agora testar a rota /auth/requerimentos para ver se retorna o pdf_path
print("\n\n" + "=" * 80)
print("TESTE: Listar requerimentos via /auth/requerimentos/1")
print("=" * 80)

try:
    response = requests.get(
        f"{API_URL}/auth/requerimentos/1",
        timeout=10
    )
    
    print(f"\nStatus: {response.status_code}")
    dados = response.json()
    
    requerimentos = dados.get('requerimentos', [])
    print(f"\nTotal de requerimentos: {len(requerimentos)}")
    
    # Procurar por requerimentos de declaração com pdf_path
    declaracoes = [r for r in requerimentos if r['tipo'] == 'declaracao']
    print(f"Total de declarações: {len(declaracoes)}")
    
    print(f"\nÚltimas 3 declarações:")
    for req in declaracoes[-3:]:
        print(f"\n   ID: {req['id']}")
        print(f"   Tipo declaração: {req.get('declaracao_info', {}).get('tipo')}")
        print(f"   PDF path: {req.get('declaracao_info', {}).get('pdf_path')}")
        
except Exception as e:
    print(f"\n Erro: {e}")
