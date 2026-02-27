# 🔧 Guia de Solução de Problemas - Ferramentas MCP

## ❌ Erro: "Ferramenta não encontrada"

Se você receber uma mensagem como:
```
❌ Ferramenta 'listar_cursos' não encontrada
```

### 🔍 Causas Comuns

1. **Servidor MCP não está rodando**
2. **Servidor precisa ser reiniciado** (após alterações no código)
3. **Ferramenta não foi registrada corretamente**
4. **Problema de conexão entre cliente e servidor**

### ✅ Soluções

#### Solução 1: Reiniciar o Servidor MCP

O servidor MCP precisa ser reiniciado sempre que:
- O código do servidor for modificado
- Novas ferramentas forem adicionadas
- Houver erros de inicialização

**Passos:**

1. **Parar o servidor atual** (se estiver rodando):
   - Pressione `Ctrl + C` no terminal do servidor
   - Ou feche o terminal do servidor

2. **Iniciar novamente:**
   ```bash
   cd agente-ia
   ..\ambiente\Scripts\python.exe mcp_escola_server.py
   ```

3. **Aguardar a mensagem de sucesso:**
   ```
   ✅ Servidor MCP iniciado com sucesso
   📡 Rodando em http://localhost:8000
   ```

4. **Reiniciar o agente:**
   - Se o agente já estava rodando, reinicie-o também
   ```bash
   cd agente-ia
   ..\ambiente\Scripts\python.exe agente_ia_inteligente.py
   ```

#### Solução 2: Verificar se o Servidor Está Rodando

Execute este comando em um terminal:
```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{"status": "ok", "message": "Escola MCP Server is running"}
```

**Se não funcionar:**
- O servidor não está rodando
- Siga os passos da Solução 1

#### Solução 3: Verificar Ferramentas Disponíveis

Quando o agente inicia, ele lista as ferramentas disponíveis:

```
✅ 7 ferramentas encontradas:
  • listar_alunos: Lista os alunos cadastrados no sistema
  • consultar_aluno: Consulta informações de um aluno específico
  • perguntar_sobre_aluno: Faz perguntas sobre um aluno
  • criar_requerimento: Cria um requerimento para o aluno
  • resumo_academico: Gera resumo acadêmico completo
  • buscar_pagamentos: Busca pagamentos e boletos do aluno
  • listar_cursos: Lista cursos cadastrados  ← Deve aparecer aqui!
```

**Se `listar_cursos` não aparecer na lista:**
1. O servidor MCP não registrou a ferramenta
2. Há um erro no código do servidor
3. Reinicie o servidor (Solução 1)

#### Solução 4: Verificar Logs do Servidor

Os logs do servidor MCP mostram quando ferramentas são registradas:

```
🎯 Registrando ferramentas MCP...
✅ listar_alunos
✅ consultar_aluno
✅ perguntar_sobre_aluno
✅ criar_requerimento
✅ resumo_academico
✅ buscar_pagamentos
✅ listar_cursos  ← Deve aparecer aqui!
```

**Se alguma ferramenta não aparecer:**
- Há um erro de sintaxe no código do servidor
- A ferramenta não tem o decorador `@mcp.tool()`
- Revise o arquivo `mcp_escola_server.py`

### 🛡️ Proteção Implementada

O agente agora possui **fallback automático** para ferramentas indisponíveis:

Quando uma ferramenta não está disponível, o agente:
1. Detecta o erro automaticamente
2. Retorna uma resposta útil ao invés de mostrar erro técnico
3. Orienta o usuário sobre próximos passos

**Exemplo com `listar_cursos`:**
```
📚 Cursos Disponíveis

Atualmente temos diversos cursos nas áreas de:
• Ciência da Computação
• Engenharias
• Administração
• Direito
• Saúde

💡 Para mais informações:
• Entre em contato com a secretaria
• Visite nosso site institucional
• Ou faça seu cadastro para ter acesso completo

⚠️ Nota: A ferramenta de listagem está temporariamente indisponível.
```

### 📋 Checklist Rápido

Quando tiver problema com ferramentas, verifique:

- [ ] Servidor MCP está rodando? → `curl http://localhost:8000/health`
- [ ] Ferramenta está na lista? → Veja mensagem de inicialização do agente
- [ ] Servidor foi reiniciado recentemente? → Reinicie se necessário
- [ ] Conexão com banco de dados OK? → Servidor mostra erros de DB nos logs
- [ ] Ambiente virtual ativado? → Deve estar usando `ambiente\Scripts\python.exe`

### 🚀 Teste Rápido

Para testar se está tudo funcionando:

1. Inicie o servidor MCP
2. Inicie o agente
3. Escolha [3] Modo visitante
4. Digite: "quais cursos?"
5. Deve listar os cursos ou mostrar mensagem útil

### 📞 Ainda com Problemas?

Se após seguir todos os passos o problema persistir:

1. Colete as seguintes informações:
   - Mensagem de erro completa
   - Lista de ferramentas que o agente encontrou
   - Logs do servidor MCP
   - Versão do Python em uso

2. Verifique se há erros de sintaxe:
   ```bash
   cd agente-ia
   ..\ambiente\Scripts\python.exe -m py_compile mcp_escola_server.py
   ```

3. Execute o servidor em modo debug para ver mais detalhes

---

## ✨ Melhorias Implementadas

### Tratamento Inteligente de Erros

O agente agora trata automaticamente:
- ✅ Ferramentas não encontradas
- ✅ Erros de conexão
- ✅ Timeout de requisições
- ✅ Respostas malformadas

### Respostas Alternativas

Quando uma ferramenta falha:
- ❌ Antes: `❌ Ferramenta 'listar_cursos' não encontrada`
- ✅ Agora: Resposta útil com informações e orientações

---

**Última atualização:** 23/02/2026
