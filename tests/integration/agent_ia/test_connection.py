"""
Script de teste para verificar a conexão com o servidor MCP
"""
import requests
import json

MCP_URL = "http://localhost:8000"

def test_health():
    """Testa o endpoint de saúde"""
    print(" Testando endpoint /health...")
    try:
        r = requests.get(f"{MCP_URL}/health", timeout=2)
        print(f" Status: {r.status_code}")
        print(f"   Resposta: {r.json()}")
        return True
    except Exception as e:
        print(f" Erro: {e}")
        return False

def test_tools_list():
    """Testa listagem de ferramentas"""
    print("\n Testando tools/list...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        r = requests.post(MCP_URL, json=payload, timeout=5)
        print(f" Status: {r.status_code}")
        
        result = r.json()
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f" {len(tools)} ferramentas disponíveis:")
            for tool in tools:
                print(f"   • {tool['name']}: {tool.get('description', '')}")
            return True
        else:
            print(f" Resposta inesperada: {result}")
            return False
    except Exception as e:
        print(f" Erro: {e}")
        return False

def test_consultar_aluno():
    """Testa consulta de aluno"""
    print("\n Testando consultar_aluno (ID=1)...")
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "consultar_aluno",
                "arguments": {"aluno_id": 1}
            },
            "id": 2
        }
        r = requests.post(MCP_URL, json=payload, timeout=5)
        print(f" Status: {r.status_code}")
        
        result = r.json()
        if "result" in result:
            content = result["result"].get("content", [])
            if content and len(content) > 0:
                text = content[0].get("text", "")
                print(f" Resposta:\n{text[:300]}...")
                return True
        
        print(f" Resposta inesperada: {json.dumps(result, indent=2)[:200]}")
        return False
    except Exception as e:
        print(f" Erro: {e}")
        return False

def main():
    print("="*70)
    print(" TESTE DE CONEXÃO MCP SERVER")
    print("="*70)
    
    tests = [
        ("Health Check", test_health),
        ("Tools List", test_tools_list),
        ("Consultar Aluno", test_consultar_aluno)
    ]
    
    passed = 0
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*70)
    print(f" RESULTADO: {passed}/{len(tests)} testes passaram")
    print("="*70)
    
    if passed == len(tests):
        print(" Sistema funcionando corretamente!")
        print("\n Para usar o agente interativo, execute:")
        print("   python agente_ia_inteligente.py")
    else:
        print(" Alguns testes falharam. Verifique o servidor MCP.")

if __name__ == "__main__":
    main()
