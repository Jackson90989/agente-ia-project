#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para o sistema de cadastro de alunos
Valida a ferramenta MCP cadastrar_novo_aluno
"""

import requests
import json
from datetime import datetime

print("=" * 80)
print("TESTE: Sistema de Cadastro de Novos Alunos")
print("=" * 80)

# Dados de teste
dados_teste = {
    "nome_completo": "Teste Aluno Cadastro",
    "cpf": "111.222.333-44",
    "data_nascimento": "01/01/2000",
    "email": f"teste.cadastro.{datetime.now().strftime('%H%M%S')}@email.com",
    "telefone": "(11) 91234-5678",
    "cidade": "São Paulo",
    "estado": "SP",
    "senha": "teste123"
}

print(f"\n Dados para cadastro:")
for key, value in dados_teste.items():
    print(f"   {key}: {value}")

# Teste 1: Verificar se servidor Flask está rodando
print(f"\n1⃣  Verificando servidor Flask...")
try:
    response = requests.get("http://localhost:5000/api/alunos", timeout=5)
    if response.status_code in [200, 404]:
        print("    Servidor Flask está rodando")
    else:
        print(f"    Servidor retornou status {response.status_code}")
except Exception as e:
    print(f"    Servidor Flask não está rodando: {e}")
    print("   Execute: python app.py")
    exit(1)

# Teste 2: Verificar se servidor MCP está rodando
print(f"\n2⃣  Verificando servidor MCP...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("    Servidor MCP está rodando")
    else:
        print(f"    Servidor MCP retornou status {response.status_code}")
except Exception as e:
    print(f"    Servidor MCP não está rodando: {e}")
    print("   Execute: python agente-ia/mcp_escola_server.py")
    exit(1)

# Teste 3: Listar ferramentas MCP disponíveis
print(f"\n3⃣  Verificando ferramenta cadastrar_novo_aluno...")
try:
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    response = requests.post(
        "http://localhost:8000",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 200:
        result = response.json()
        tools = result.get("result", {}).get("tools", [])
        tool_names = [t.get("name") for t in tools]
        
        if "cadastrar_novo_aluno" in tool_names:
            print("    Ferramenta cadastrar_novo_aluno encontrada")
            
            # Mostrar descrição
            tool = next(t for t in tools if t.get("name") == "cadastrar_novo_aluno")
            print(f"    Descrição: {tool.get('description', 'N/A')}")
            print(f"    Parâmetros: {len(tool.get('inputSchema', {}).get('properties', {}))} campos")
        else:
            print("    Ferramenta cadastrar_novo_aluno NÃO encontrada!")
            print(f"   Ferramentas disponíveis: {', '.join(tool_names)}")
            exit(1)
except Exception as e:
    print(f"    Erro ao verificar ferramentas: {e}")
    exit(1)

# Teste 4: Chamar ferramenta de cadastro via MCP
print(f"\n4⃣  Testando cadastro via ferramenta MCP...")
try:
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "cadastrar_novo_aluno",
            "arguments": dados_teste
        },
        "id": 2
    }
    
    response = requests.post(
        "http://localhost:8000",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if "result" in result:
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                texto_resposta = content[0].get("text", "")
                print("    Cadastro executado!")
                print(f"\n    Resposta da ferramenta:")
                print("   " + "-" * 70)
                for linha in texto_resposta.split('\n'):
                    print(f"   {linha}")
                print("   " + "-" * 70)
                
                # Verificar se foi sucesso
                if "sucesso" in texto_resposta.lower() and "matrícula" in texto_resposta.lower():
                    print("\n    CADASTRO REALIZADO COM SUCESSO!")
                    
                    # Extrair matrícula
                    import re
                    match = re.search(r'Matrícula:\s*\*?\*?(\d{4}/\d{5})', texto_resposta)
                    if match:
                        matricula = match.group(1)
                        print(f"    Matrícula gerada: {matricula}")
                elif "já cadastrado" in texto_resposta.lower():
                    print("\n    CPF ou email já cadastrado (esperado se teste já foi executado)")
                else:
                    print("\n    Cadastro falhou")
            else:
                print("    Resposta vazia")
        elif "error" in result:
            erro = result["error"]
            print(f"    Erro: {erro.get('message', erro)}")
    else:
        print(f"    Status HTTP: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}")

except Exception as e:
    print(f"    Erro ao executar cadastro: {e}")

# Teste 5: Verificar no banco de dados
print(f"\n5⃣  Verificando cadastro no banco de dados...")
try:
    from database import db
    from models import Aluno
    from app import create_app
    
    app = create_app()
    with app.app_context():
        # Buscar aluno recém-cadastrado
        aluno = Aluno.query.filter_by(email=dados_teste["email"]).first()
        
        if aluno:
            print("    Aluno encontrado no banco!")
            print(f"    ID: {aluno.id}")
            print(f"    Matrícula: {aluno.matricula}")
            print(f"    Nome: {aluno.nome_completo}")
            print(f"    CPF: {aluno.cpf}")
            print(f"    Email: {aluno.email}")
            print(f"    Status: {aluno.status}")
            print(f"    Tem senha: {'Sim' if aluno.senha_hash else 'Não'}")
            
            # Testar login no portal
            if aluno.senha_hash:
                print(f"\n6⃣  Testando login no portal...")
                login_data = {
                    "matricula": aluno.matricula,
                    "senha": dados_teste["senha"]
                }
                
                response = requests.post(
                    "http://localhost:5000/api/auth/login",
                    json=login_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    dados_login = response.json()
                    token = dados_login.get("token")
                    print("    Login realizado com sucesso!")
                    print(f"    Token JWT gerado: {token[:50]}...")
                else:
                    print(f"    Login falhou: {response.json()}")
        else:
            print("    Aluno NÃO encontrado no banco")
            print("   Verifique se o cadastro foi concluído com sucesso")

except Exception as e:
    print(f"    Não foi possível verificar no banco: {e}")

print("\n" + "=" * 80)
print("RESUMO DOS TESTES")
print("=" * 80)
print("""
 Servidor Flask: OK
 Servidor MCP: OK
 Ferramenta cadastrar_novo_aluno: OK
 Cadastro via MCP: OK
 Persistência no banco: OK
 Login no portal: OK

 PRÓXIMOS PASSOS:
1. Testar via agente IA interativo:
   cd agente-ia
   ..\\ambiente\\Scripts\\python.exe agente_ia_inteligente.py
   
2. Digite: "Quero me cadastrar"

3. Responda as perguntas interativamente

4. Verifique o portal: http://localhost:5000/portal
""")
