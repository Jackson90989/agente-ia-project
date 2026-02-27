#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Teste das rotas de PDF"""

import requests
import os

API_URL = "http://localhost:5000/api"

print("=" * 80)
print("TESTE: Acessando endpoints de PDF")
print("=" * 80)

# Testar os requerimentos com PDF
requerimento_ids = [17, 16, 14]

for req_id in requerimento_ids:
    print(f"\n Testando requerimento #{req_id}:")
    
    # Teste 1: Baixar PDF
    print(f"   GET /api/requerimentos/{req_id}/pdf")
    response = requests.get(f"{API_URL}/requerimentos/{req_id}/pdf")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"    PDF descargável (tamanho: {len(response.content)} bytes)")
        # Salvar uma cópia para teste
        filename = f"test_pdf_{req_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        print(f"    Salvo como: {filename}")
    else:
        print(f"    Erro: {response.json()}")
    
    # Teste 2: Visualizar PDF
    print(f"   GET /api/requerimentos/{req_id}/visualizar-pdf")
    response = requests.get(f"{API_URL}/requerimentos/{req_id}/visualizar-pdf")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"    PDF visualizável (tamanho: {len(response.content)} bytes)")
    else:
        print(f"    Erro: {response.json()}")

print("\n" + "=" * 80)
print("TESTES CONCLUÍDOS")
print("=" * 80)
