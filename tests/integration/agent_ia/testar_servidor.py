"""
Script para testar se o servidor MCP está funcionando corretamente
"""
import requests
import json

def testar_servidor():
    """Testa conexão e ferramentas do servidor MCP"""
    
    print("="*70)
    print(" TESTE DO SERVIDOR MCP")
    print("="*70)
    
    # 1. Testar health check
    print("\n1⃣ Testando Health Check...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print(" Servidor está respondendo!")
            print(f"   Resposta: {response.json()}")
        else:
            print(f" Servidor retornou status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(" Servidor não está rodando!")
        print(" Execute: cd agente-ia && ..\\ambiente\\Scripts\\python.exe mcp_escola_server.py")
        return False
    except Exception as e:
        print(f" Erro: {e}")
        return False
    
    # 2. Testar listagem de ferramentas
    print("\n2⃣ Testando Listagem de Ferramentas...")
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
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f" {len(tools)} ferramentas encontradas:")
                
                # Verificar ferramentas importantes
                tool_names = [t["name"] for t in tools]
                
                ferramentas_esperadas = [
                    "listar_alunos",
                    "consultar_aluno",
                    "listar_cursos",  # ← Esta é a que estava faltando!
                    "listar_materias_disponiveis",
                    "perguntar_sobre_aluno",
                    "criar_requerimento",
                    "resumo_academico",
                    "buscar_pagamentos",
                    "diagnosticar_banco"
                ]
                
                for ferramenta in ferramentas_esperadas:
                    if ferramenta in tool_names:
                        print(f"    {ferramenta}")
                    else:
                        print(f"    {ferramenta} - FALTANDO!")
                
                # Verificar especificamente listar_cursos
                if "listar_cursos" in tool_names:
                    print(f"\n listar_cursos está disponível! Problema resolvido!")
                else:
                    print(f"\n  listar_cursos ainda não está disponível.")
                    print(f" Reinicie o servidor MCP")
            else:
                print(" Resposta não contém ferramentas")
                print(f"   Resposta: {result}")
        else:
            print(f" Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f" Erro ao listar ferramentas: {e}")
        return False
    
    # 3. Testar chamada da ferramenta listar_cursos
    print("\n3⃣ Testando Ferramenta listar_cursos...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "listar_cursos",
                "arguments": {}
            },
            "id": 2
        }
        
        response = requests.post(
            "http://localhost:8000",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                content = result["result"].get("content", [])
                if content and len(content) > 0:
                    texto = content[0].get("text", "")
                    print(" listar_cursos funcionando!")
                    print(f"\n Resultado:")
                    print(texto[:500] + "..." if len(texto) > 500 else texto)
                else:
                    print("  Resposta vazia")
            elif "error" in result:
                print(f" Erro: {result['error']}")
        else:
            print(f" Erro HTTP {response.status_code}")
            
    except Exception as e:
        print(f" Erro ao testar ferramenta: {e}")
    
    print("\n" + "="*70)
    print(" TESTE CONCLUÍDO")
    print("="*70)
    return True

if __name__ == "__main__":
    testar_servidor()
