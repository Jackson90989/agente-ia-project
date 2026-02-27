# 🎓 GUIA DA NOVA INTERFACE DO AGENTE IA

## 📋 Novidades

A interface do Agente IA foi completamente reformulada para ser mais intuitiva e acessível! Agora qualquer pessoa pode usar o sistema, não apenas alunos já cadastrados.

## 🚀 Como Usar

### 1️⃣ Iniciando o Sistema

Execute o agente normalmente:
```bash
cd agente-ia
..\ambiente\Scripts\python.exe agente_ia_inteligente.py
```

### 2️⃣ Menu Principal

Ao iniciar, você verá um menu com 4 opções:

```
╔════════════════════════════════════════════════════════════╗
║           🏫 BEM-VINDO AO PORTAL ACADÊMICO             ║
╚════════════════════════════════════════════════════════════╝

Selecione uma opção:
  [1] 🔑 Já sou aluno (fazer login)
  [2] 📝 Quero me matricular (novo aluno)
  [3] 👁️  Modo visitante (consultas gerais)
  [0] 🚪 Sair
```

## 🔐 Opção 1: Login de Aluno

- Para alunos já cadastrados no sistema
- Digite seu ID numérico (exemplo: 1, 2, 3, etc.)
- Você tem 3 tentativas para fazer login
- Digite 'voltar' a qualquer momento para retornar ao menu

**Exemplo:**
```
📌 Digite seu ID de aluno (ou 'voltar' para o menu): 1
🔍 Verificando aluno...
✅ Login realizado com sucesso!
👤 Bem-vindo(a), João Silva!
```

## 📝 Opção 2: Novo Aluno (Matrícula)

- Para pessoas que querem se matricular
- Modo interativo: o agente te guia pela conversa
- Você pode simplesmente dizer "quero me cadastrar"
- O sistema coletará seus dados de forma natural

**Exemplo de uso:**
```
👤 Você: quero me cadastrar
🤖 Assistente: Ótimo! Vou te ajudar com sua matrícula...
```

## 👁️ Opção 3: Modo Visitante

- Para qualquer pessoa que queira informações gerais
- Não precisa estar cadastrado
- Pode fazer perguntas sobre cursos, faculdade, etc.
- Conversar livremente com o assistente

**Exemplos de perguntas:**
- "Quais cursos vocês oferecem?"
- "Como funciona a matrícula?"
- "Quanto custa o curso?"
- Ou até perguntas gerais não acadêmicas!

## 💬 Após o Login/Cadastro

### Se você fez login como aluno:

O sistema mostrará opções personalizadas:

```
👤 Logado como: João Silva (ID: 1)

📌 O que você pode fazer:

   📊 Consultas
      • 'meus dados' ou 'quem sou eu?'
      • 'minhas matérias' ou 'minha grade'
      • 'minhas notas' ou 'meu histórico'
      • 'meus boletos' ou 'quanto devo?'
      • 'resumo acadêmico'

   📄 Documentos
      • 'declaração de matrícula'
      • 'segunda via de boleto'
      • 'histórico escolar'

   📝 Solicitações
      • 'adicionar matéria ALG-101'
      • 'remover matéria MAT-102'
      • 'trancar o semestre'
      • 'solicitar transferência'
```

### Se você está como visitante:

```
👁️  Modo: Visitante

📌 O que você pode fazer:
      • 'quero me cadastrar' ou 'fazer matrícula'
      • 'quais cursos tem?' ou 'me fale sobre os cursos'
      • Fazer perguntas gerais sobre a faculdade
      • Conversar comigo sobre diversos assuntos
```

## 🎯 Recursos

### ✅ Vantagens da Nova Interface

1. **Menu Visual Intuitivo**: Opções claras e numeradas
2. **Modo Visitante**: Não precisa ter cadastro para usar
3. **Login Seguro**: Sistema de tentativas limitadas
4. **Instruções Contextuais**: Ajuda específica para cada modo
5. **Retorno ao Menu**: Opção de voltar a qualquer momento
6. **Mensagens Personalizadas**: Interface adaptável ao tipo de usuário

### 🔄 Fluxos de Uso

#### Fluxo 1: Aluno Existente
```
Início → [1] Login → Digite ID → Sistema Verificado → Acesso Completo
```

#### Fluxo 2: Novo Aluno  
```
Início → [2] Matrícula → Conversa Natural → Dados Coletados → Cadastro Completo
```

#### Fluxo 3: Visitante
```
Início → [3] Modo Visitante → Consultas Gerais → Informações
```

## 📝 Exemplos de Uso

### Exemplo 1: Login Simples
```
📌 Escolha uma opção (0-3): 1
📌 Digite seu ID de aluno: 5
🔍 Verificando aluno...
✅ Login realizado com sucesso!
👤 Bem-vindo(a), Maria Santos!
```

### Exemplo 2: Cadastro de Novo Aluno
```
📌 Escolha uma opção (0-3): 2
✅ Ótimo! Vou te ajudar a fazer sua matrícula.
💬 Você pode começar digitando 'quero me cadastrar'

👤 Você: quero fazer minha matrícula
🤖 Assistente: [inicia coleta de dados...]
```

### Exemplo 3: Modo Visitante
```
📌 Escolha uma opção (0-3): 3
✅ Bem-vindo ao modo visitante!
💬 Você pode fazer consultas gerais e conversar comigo.

👤 Você: quais cursos vocês oferecem?
🤖 Assistente: [lista cursos disponíveis...]
```

## 🆘 Dicas e Atalhos

- **Sair do sistema**: Digite `sair`, `exit` ou `quit`
- **Voltar ao menu (durante login)**: Digite `voltar` ou `v`
- **Interromper (teclado)**: Pressione `Ctrl + C`

## 🎨 Melhorias Implementadas

1. **Interface Visual Aprimorada**
   - Menu com bordas e ícones
   - Mensagens coloridas e estruturadas
   - Indicadores visuais claros

2. **Experiência de Usuário**
   - Instruções contextuais
   - Mensagens de erro amigáveis
   - Feedback em tempo real

3. **Segurança e Controle**
   - Limite de tentativas de login (3)
   - Validação de entrada
   - Opção de cancelar/voltar

4. **Flexibilidade**
   - Modo para alunos cadastrados
   - Modo para novos alunos
   - Modo para visitantes
   - Conversação natural em todos os modos

## 🔧 Arquivos Modificados

- `agente_ia_inteligente.py`
  - Método `iniciar()` reformulado
  - Novo método `_fazer_login()`
  - Método `executar()` melhorado
  - Interface adaptativa

## 📞 Suporte

Se encontrar algum problema:
1. Verifique se o servidor MCP está rodando
2. Certifique-se de estar usando o ambiente virtual correto
3. Consulte os logs de erro para detalhes

---

**✨ Aproveite a nova interface do Agente IA!**
