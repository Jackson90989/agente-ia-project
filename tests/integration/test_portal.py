"""
Script de teste para validar o Portal do Aluno
Testa integração com autenticação, requerimentos e PDFs
"""

import requests
import json
from datetime import datetime

BASE_URL = 'http://localhost:5000'
API_URL = f'{BASE_URL}/api'

print("=" * 60)
print(" TESTES DO PORTAL DO ALUNO")
print("=" * 60)

# 1. Testar acesso ao portal
print("\n1⃣  Acessando o Portal...")
try:
    resp = requests.get(f'{BASE_URL}/portal')
    if resp.status_code == 200:
        print(" Portal HTML carregado com sucesso")
    else:
        print(f" Erro ao acessar portal: {resp.status_code}")
except Exception as e:
    print(f" Erro: {e}")

# 2. Testar serviços disponíveis
print("\n2⃣  Obtendo serviços disponíveis...")
try:
    resp = requests.get(f'{API_URL}/portal/servicos-disponiveis')
    if resp.status_code == 200:
        servicos = resp.json()
        print(f" {len(servicos)} serviços disponíveis:")
        for serv in servicos:
            print(f"   {serv['icone']} {serv['nome']}")
    else:
        print(f" Erro: {resp.status_code}")
except Exception as e:
    print(f" Erro: {e}")

# 3. Testar login
print("\n3⃣  Testando Login...")
print("   (Usando matrícula de teste: 2024001)")

login_data = {
    'matricula': '2024001',
    'senha': ''  # Será preenchida se existir
}

try:
    # Primeiro, vamos tentar com uma senha vazia/padrão
    resp = requests.post(
        f'{API_URL}/auth/login',
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if resp.status_code == 200:
        dados = resp.json()
        token = dados.get('token')
        aluno = dados.get('aluno')
        print(f" Login bem-sucedido!")
        print(f"   Nome: {aluno.get('nome_completo')}")
        print(f"   Matrícula: {aluno.get('matricula')}")
        print(f"   Token: {token[:20]}...")
    else:
        print(f"  Login falhou (esperado se senha não foi definida)")
        print(f"   Status: {resp.status_code}")
        print(f"   Resposta: {resp.json()}")
        token = None
        aluno = {'id': 1}  # ID de teste
        
except Exception as e:
    print(f" Erro de conexão: {e}")
    token = None

# 4. Testar validação de token (se login funcionou)
if token:
    print("\n4⃣  Validando Token JWT...")
    try:
        resp = requests.get(
            f'{API_URL}/auth/validar-token',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if resp.status_code == 200:
            print(" Token válido!")
        else:
            print(f" Token inválido: {resp.status_code}")
    except Exception as e:
        print(f" Erro: {e}")

# 5. Testar dashboard data
print("\n5⃣  Obtendo dados do dashboard...")
try:
    if token:
        resp = requests.get(
            f'{API_URL}/auth/requerimentos/1',
            headers={'Authorization': f'Bearer {token}'}
        )
    else:
        resp = requests.get(f'{API_URL}/portal/dashboard-data/1')
    
    if resp.status_code == 200:
        dados = resp.json()
        reqs = dados.get('requerimentos', [])
        print(f" Dashboard carregado!")
        print(f"   Requerimentos: {len(reqs)}")
        
        if reqs:
            for i, req in enumerate(reqs[:3], 1):
                print(f"   {i}. {req.get('tipo')} - {req.get('status')}")
        else:
            print("   (Nenhum requerimento cadastrado)")
    else:
        print(f" Erro: {resp.status_code}")
except Exception as e:
    print(f" Erro: {e}")

# 6. Testar verificação de senha (para agente)
print("\n6⃣  Testando verificação de senha (para Agente)...")
try:
    resp = requests.post(
        f'{API_URL}/auth/verificar-senha/1',
        json={'senha': 'teste123'},
        headers={'Content-Type': 'application/json'}
    )
    
    if resp.status_code == 200:
        print(" Verificação de senha disponível!")
        print("   (Agente pode usar este endpoint)")
    else:
        print(f"  Status: {resp.status_code}")
        print("   (Esperado se senha não existe)")
except Exception as e:
    print(f" Erro: {e}")

# 7. Testar listagem de serviços do aluno
print("\n7⃣  Listando requerimentos do aluno...")
try:
    if token:
        resp = requests.get(
            f'{API_URL}/auth/requerimentos/1',
            headers={'Authorization': f'Bearer {token}'}
        )
    else:
        resp = requests.get(f'{API_URL}/portal/dashboard-data/1')
    
    if resp.status_code == 200:
        dados = resp.json()
        print(" Requerimentos obtidos!")
        print(f"   Total: {dados.get('estatisticas', {}).get('total', 0)}")
        print(f"   Concluídos: {dados.get('estatisticas', {}).get('concluidos', 0)}")
        print(f"   Pendentes: {dados.get('estatisticas', {}).get('pendentes', 0)}")
    else:
        print(f" Erro: {resp.status_code}")
except Exception as e:
    print(f" Erro: {e}")

# 8. Testar PDF endpoints
print("\n8⃣  Testando PDFs (se houver declarações)...")
try:
    resp = requests.get(f'{API_URL}/requerimentos/1/pdf')
    if resp.status_code == 200:
        print(" PDF disponível para download")
        print(f"   Tamanho: {len(resp.content)} bytes")
    elif resp.status_code == 404:
        print("  Nenhum PDF encontrado (normal se não tem declarações)")
    else:
        print(f" Erro: {resp.status_code}")
except Exception as e:
    print(f" Erro: {e}")

print("\n" + "=" * 60)
print(" TESTES CONCLUÍDOS!")
print("=" * 60)

print("""
 PRÓXIMOS PASSOS:

1. Se algum teste falhou, verifique:
   - Se o servidor Flask está rodando (python app.py)
   - Se o banco de dados foi inicializado (python init_db.py)
   - Se há alunos cadastrados (python populate_db.py)

2. Para testar com dados reais:
   - Abra http://localhost:5000/portal no navegador
   - Faça login com uma matrícula válida
   - Visualize seus requerimentos

3. Para integrar com o Agente:
   - Execute o agente IA normalmente
   - Ele usará os endpoints para:
     * Verificar senha: POST /api/auth/verificar-senha/<id>
     * Obter requerimentos: GET /api/auth/requerimentos/<id>
     * Gerar links: Endpoints dos PDFs

4. Documentação completa em: GUIA_PORTAL_ALUNO.md
""")
