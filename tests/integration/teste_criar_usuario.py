"""
Script de teste para criar um novo aluno via API Flask
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def criar_aluno_teste():
    """Cria um novo aluno usando a API Flask"""
    
    # Gerar dados únicos usando timestamp
    import time
    timestamp = str(int(time.time()))[-6:]  # Últimos 6 dígitos do timestamp
    
    # Dados do novo aluno
    dados_aluno = {
        "nome_completo": f"Aluno Teste {timestamp}",
        "cpf": f"456.789.{timestamp[:3]}-{timestamp[3:]}",
        "data_nascimento": "1998-05-15",
        "email": f"aluno{timestamp}@example.com",
        "telefone": "(11) 99876-5432",
        "cidade": "São Paulo",
        "estado": "SP",
        "senha": "senha123"  #  NOVO - senha agora é suportada
    }
    
    print("="*60)
    print(" TESTE DE CRIAÇÃO DE ALUNO")
    print("="*60)
    print()
    
    print(f" Dados do aluno a criar:")
    for chave, valor in dados_aluno.items():
        if chave != "senha":
            print(f"  • {chave:20} {valor}")
        else:
            print(f"  • {chave:20} ****")
    print()
    
    try:
        # 1. CRIAR ALUNO
        print("1⃣  Criando aluno...")
        response = requests.post(
            f"{BASE_URL}/alunos",
            json=dados_aluno,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            aluno = response.json()
            aluno_id = aluno['id']
            matricula = aluno['matricula']
            
            print(f"    Aluno criado com sucesso!")
            print(f"   • ID: {aluno_id}")
            print(f"   • Matrícula: {matricula}")
            print(f"   • Email: {aluno['email']}")
            print()
            
            # 2. FAZER LOGIN
            print("2⃣  Testando login...")
            dados_login = {
                "matricula": matricula,
                "senha": "senha123"
            }
            
            response_login = requests.post(
                f"{BASE_URL}/auth/login",
                json=dados_login,
                timeout=10
            )
            
            print(f"   Status: {response_login.status_code}")
            
            if response_login.status_code == 200:
                resultado_login = response_login.json()
                token = resultado_login.get('token')
                
                print(f"    Login realizado com sucesso!")
                print(f"   • Token: {token[:20]}..." if token else "   • Token: Não obtido")
                print()
                
                # 3. BUSCAR DADOS DO ALUNO
                print("3⃣  Buscando dados do aluno...")
                response_dados = requests.get(
                    f"{BASE_URL}/alunos/{aluno_id}",
                    timeout=10
                )
                
                if response_dados.status_code == 200:
                    dados = response_dados.json()
                    print(f"    Dados obtidos com sucesso!")
                    print(f"   • Nome: {dados['nome_completo']}")
                    print(f"   • CPF: {dados['cpf']}")
                    print(f"   • Email: {dados['email']}")
                    print(f"   • Status: {dados['status']}")
                    print(f"   • Tem senha: {dados['tem_senha']}")
                    print()
                else:
                    print(f"    Erro ao buscar dados: {response_dados.status_code}")
                    print()
                
                # 4. MATRICULAR NO CURSO
                print("4⃣  Buscando cursos disponíveis...")
                response_cursos = requests.get(
                    f"{BASE_URL}/cursos",
                    timeout=10
                )
                
                if response_cursos.status_code == 200:
                    cursos = response_cursos.json()
                    if cursos:
                        primeiro_curso = cursos[0]
                        curso_id = primeiro_curso['id']
                        print(f"    Curso encontrado: {primeiro_curso['nome']} (ID: {curso_id})")
                        print()
                        
                        print("4b⃣  Matriculando no curso...")
                        dados_matricula = {
                            "curso_id": curso_id,
                            "ano": 2026,
                            "semestre": 1
                        }
                        
                        response_mat = requests.post(
                            f"{BASE_URL}/alunos/{aluno_id}/matriculas",
                            json=dados_matricula,
                            timeout=10
                        )
                        
                        print(f"   Status: {response_mat.status_code}")
                        
                        if response_mat.status_code == 201:
                            matricula_info = response_mat.json()
                            print(f"    Matrícula criada com sucesso!")
                            print(f"   • ID Matrícula: {matricula_info['id']}")
                            print(f"   • Curso: {matricula_info.get('curso_nome', 'N/I')}")
                            print(f"   • Período: {matricula_info['ano']}/{matricula_info['semestre']}")
                            print(f"   • Status: {matricula_info['status']}")
                            print()
                        else:
                            print(f"     Erro ao matricular (status {response_mat.status_code})")
                            print()
                else:
                    print(f"     Não foi possível buscar cursos (status {response_cursos.status_code})")
                    print()
                
                # RESUMO FINAL
                print("="*60)
                print(" TESTE CONCLUÍDO COM SUCESSO!")
                print("="*60)
                print()
                print(f" Novo Aluno Criado:")
                print(f"  • Nome: {dados_aluno['nome_completo']}")
                print(f"  • Matrícula: {matricula}")
                print(f"  • Email: {dados_aluno['email']}")
                print(f"  • Senha: {dados_aluno['senha']}")
                print()
                print(f" Credenciais de Acesso:")
                print(f"  • Usuário: {matricula}")
                print(f"  • Senha: {dados_aluno['senha']}")
                print(f"  • Portal: http://localhost:5000/portal")
                print()
                
            else:
                erro_login = response_login.json()
                print(f"    Erro no login: {erro_login.get('erro', 'Desconhecido')}")
                print()
                
        elif response.status_code == 409:
            print(f"    CPF ou email já cadastrado")
            print()
        else:
            erro = response.json()
            print(f"    Erro: {erro.get('erro', 'Desconhecido')}")
            print()
    
    except requests.exceptions.ConnectionError:
        print(" Erro: Servidor Flask não está respondendo")
        print("   Certifique-se de que está rodando em http://localhost:5000")
        print()
    except Exception as e:
        print(f" Erro: {e}")
        import traceback
        traceback.print_exc()
        print()

if __name__ == "__main__":
    criar_aluno_teste()
