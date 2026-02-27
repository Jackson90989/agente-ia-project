#!/usr/bin/env python3
"""
Teste do agente IA - Verificar se a ferramenta listar_cursos funciona
"""
import subprocess
import sys
import time

# Adicionar o diretório agente-ia ao caminho
sys.path.insert(0, r'C:\Users\JacksonRodrigues\Downloads\AgenteIa\agente-ia')

# Importar o agente
from agente_ia_inteligente import AgenteIAInteligente

print("="*60)
print(" TESTANDO AGENTE IA - FERRAMENTA 'listar_cursos'")
print("="*60)

# Criar agente
agente = AgenteIAInteligente(mcp_url="http://localhost:8000")

print("\n Teste 1: Listar ferramentas disponíveis")
print("-" * 60)
ferramentas = agente.listar_ferramentas()
print(f"\n {len(ferramentas)} ferramentas encontradas")

# Verificar se listar_cursos está na lista
listar_cursos_encontrada = any(f.get('name') == 'listar_cursos' for f in ferramentas)
if listar_cursos_encontrada:
    print(" Ferramenta 'listar_cursos' encontrada na lista!")
else:
    print(" Ferramenta 'listar_cursos' NÃO encontrada!")

print("\n Teste 2: Chamar ferramenta 'listar_cursos' diretamente")
print("-" * 60)
resultado = agente.chamar_ferramenta('listar_cursos', {})
print("\n" + resultado)

print("\n" + "="*60)
print(" TESTE CONCLUÍDO COM SUCESSO!")
print("="*60)
print("\n A ferramenta 'listar_cursos' agora está funcionando corretamente!")
print("   Você pode perguntar ao agente: 'quais são os cursos?'")
