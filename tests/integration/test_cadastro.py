#!/usr/bin/env python3
"""
Teste do agente IA - Simular cadastro de aluno
"""
import sys
import json

sys.path.insert(0, r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\agente-ia')

from agente_ia_inteligente import AgenteIAInteligente

print("="*70)
print(" TESTANDO CADASTRO DE NOVO ALUNO")
print("="*70)

# Dados do formulário que o usuário preencheu
dados_cadastro = {
    "nome_completo": "jackson",
    "cpf": "143.145.123-03",
    "data_nascimento": "31/01/2025",
    "email": "jackson@gmail.com",
    "telefone": None,  # pulou
    "cidade": "hortolandia",
    "estado": "sp",
    "senha": "1234",
    "curso_codigo": "CC001"  # Ciência da Computação
}

# Criar agente
agente = AgenteIAInteligente(mcp_url="http://localhost:8000")

# Testar se a ferramenta está disponível
print("\n Verificando disponibilidade da ferramenta...")
ferramentas = agente.listar_ferramentas()
cadastrar_disponivel = any(f.get('name') == 'cadastrar_novo_aluno' for f in ferramentas)

if cadastrar_disponivel:
    print(" Ferramenta 'cadastrar_novo_aluno' encontrada!")
else:
    print(" Ferramenta 'cadastrar_novo_aluno' não encontrada!")
    sys.exit(1)

# Chamar a ferramenta com os dados do usuário
print("\n Cadastrando novo aluno...")
print("-" * 70)
print(f"Nome: {dados_cadastro['nome_completo']}")
print(f"CPF: {dados_cadastro['cpf']}")
print(f"Data de Nascimento: {dados_cadastro['data_nascimento']}")
print(f"Email: {dados_cadastro['email']}")
print(f"Cidade: {dados_cadastro['cidade']}")
print(f"Estado: {dados_cadastro['estado']}")
print(f"Senha: {'*' * len(dados_cadastro['senha'])}")
print(f"Curso: {dados_cadastro['curso_codigo']}")
print("-" * 70)

# Remover None values para não enviar parâmetros opcionais vazios
argumentos = {k: v for k, v in dados_cadastro.items() if v is not None}

resultado = agente.chamar_ferramenta('cadastrar_novo_aluno', argumentos)

print("\n Resultado:")
print("=" * 70)
print(resultado)
print("=" * 70)

if "" in resultado and "cadastrado com sucesso" in resultado.lower():
    print("\n CADASTRO REALIZADO COM SUCESSO!")
else:
    print("\n Verifique o resultado acima para mais detalhes.")
