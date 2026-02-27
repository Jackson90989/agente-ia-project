# Sistema Agente IA - Gerenciamento Escolar

## Descrição

Sistema inteligente de gerenciamento acadêmico usando FastMCP e LLM (Ollama/llama3.2). Permite que alunos consultem suas informações acadêmicas, notas, matérias, pagamentos e criem requerimentos de forma conversacional.

## Início Rápido

### Opção 1: Executar script automático (Recomendado)
```batch
iniciar_sistema.bat
```

### Opção 2: Execução manual

**1. Ativar ambiente virtual:**
```batch
ambiente\Scripts\activate
```

**2. Iniciar servidor MCP:**
```batch
cd agente-ia
python mcp_escola_server.py
```

**3. Em outro terminal, iniciar o agente:**
```batch
cd agente-ia
python agente_ia_inteligente.py
```

## Pré-requisitos

- Python 3.10+
- Packages instalados (já configurados no ambiente virtual):
  - fastmcp
  - fastapi
  - uvicorn
  - requests
  - sqlalchemy

- **Opcional:** Ollama com modelo llama3.2:3b para LLM
  - Se não disponível, o sistema usa análise baseada em palavras-chave

## 🔧 Funcionalidades

### Ferramentas Disponíveis:

1. **listar_alunos** - Lista alunos cadastrados
2. **consultar_aluno** - Consulta informações de um aluno
3. **perguntar_sobre_aluno** - Faz perguntas sobre um aluno (matérias, notas, pagamentos)
4. **criar_requerimento** - Cria requerimentos (adição/remoção de matéria, declarações, boletos)
5. **resumo_academico** - Gera resumo completo do aluno
6. **buscar_pagamentos** - Busca pagamentos e boletos
7. **diagnosticar_banco** - Diagnóstico do banco de dados

### Exemplos de Perguntas:

```
- "quem sou eu?"
- "minhas matérias"
- "minhas notas"
- "meus boletos"
- "resumo acadêmico"
- "quero adicionar a matéria ALG-101"
```

## Estrutura do Projeto

```
AgenteIa/
├── agente-ia/
│   ├── agente_ia_inteligente.py  # Cliente do agente
│   ├── mcp_escola_server.py      # Servidor MCP
│   └── test_connection.py        # Script de teste
├── ambiente/                      # Ambiente virtual Python
├── escola.db                      # Banco de dados SQLite
├── iniciar_sistema.bat           # Script de inicialização
└── README.md                      # Este arquivo
```

## Testando o Sistema

Execute o script de teste para verificar a conectividade:
```batch
cd agente-ia
python test_connection.py
```

## Endpoints do Servidor

- `GET /health` - Verificação de saúde do servidor
- `POST /` - Endpoint JSON-RPC para chamadas de ferramentas
- `POST /mcp` - Endpoint SSE para MCP nativo

## ⚙️ Configurações

### agente_ia_inteligente.py
```python
USE_OLLAMA = True  # False para desativar LLM
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
```

### mcp_escola_server.py
```python
DB_PATH = r'C:\Users\...\escola.db'  # Caminho do banco
PORT = 8000  # Porta do servidor
```

## Troubleshooting

### Servidor não inicia
- Verifique se a porta 8000 está livre: `netstat -ano | findstr :8000`
- Verifique o caminho do banco de dados em `mcp_escola_server.py`

### Ollama não disponível
- O sistema funciona sem Ollama usando análise de palavras-chave
- Para instalar Ollama: https://ollama.ai
- Instalar modelo: `ollama pull llama3.2:3b`

### Erro 404
- Certifique-se de que o servidor MCP está rodando
- Verifique se está usando a URL correta: `http://localhost:8000`

## Logs

- Servidor MCP: `agente-ia/mcp_server.log`
- Saída do agente: console

## Dados de Teste

IDs de alunos disponíveis no banco:
- ID: 1, 2, 3, etc.

Para verificar alunos disponíveis:
```python
cd agente-ia
python -c "import sqlite3; conn = sqlite3.connect('../escola.db'); print(conn.execute('SELECT id, nome_completo FROM alunos LIMIT 5').fetchall())"
```

## Suporte

Para problemas ou dúvidas, verifique:
1. Logs do servidor
2. Execute `test_connection.py`
3. Verifique se o banco de dados existe

## Atualizações

Para atualizar dependências:
```batch
ambiente\Scripts\activate
pip install --upgrade fastmcp fastapi uvicorn
```

---

**Versão:** 1.0.0  
**Data:** Fevereiro 2026  
**FastMCP:** 1.26.0
"# agente-ia-project" 
