# 🎓 Agente IA - Sistema de Geração de Declarações em PDF Real

## ✨ O Que é Novo?

O agente agora **gera PDFs reais e profissionais** usando um template HTML dedicado. Todas as declarações são criadas com aparência de documento oficial!

## 📋 Tipos de Declarações

| Tipo | Comando | Descrição |
|------|---------|-----------|
| 📄 Matrícula | `"declaração de matrícula"` | Comprovante de vínculo estudantil |
| 📊 Frequência | `"declaração de frequência"` | Comprovante de presença/frequência |
| 🎓 Conclusão | `"declaração de conclusão"` | Certificado de conclusão de curso |
| 🔗 Vínculo | `"declaração de vínculo"` | Comprovante geral de vínculo |

## 🚀 Como Começar

### Passo 1: Instalar Dependências

```bash
cd agente-ia
instalar_dependencias.bat
```

Ou manualmente:
```bash
..\ambiente\Scripts\python.exe -m pip install weasyprint jinja2
```

### Passo 2: Testar o Sistema

```bash
..\ambiente\Scripts\python.exe teste_pdf.py
```

Você verá algo como:
```
✅ Dependências: OK
✅ Template HTML: OK
✅ Geração de PDF: OK

✨ Todos os testes passaram! Sistema pronto para uso!
```

### Passo 3: Iniciar o Servidor

Terminal 1:
```bash
cd agente-ia
..\ambiente\Scripts\python.exe mcp_escola_server.py
```

Terminal 2:
```bash
cd agente-ia
..\ambiente\Scripts\python.exe agente_ia_inteligente.py
```

### Passo 4: Usar o Agente

```
📌 Digite seu ID de aluno: 1

👤 Você: declaração de matrícula

🤖 Assistente: ✅ DECLARAÇÃO GERADA COM SUCESSO!
📌 Protocolo: REQ-1-20240223143052
👤 Aluno: João Silva (MAT20240001)
📄 Tipo: DECLARAÇÃO DE MATRÍCULA
📅 Data: 23/02/2024 14:30
📁 Arquivo: declaracao_MAT20240001_matricula_20240223143052.pdf

✨ Sua declaração foi gerada em formato PDF profissional!
```

## 📁 Onde Ficam os PDFs?

```
AgenteIa/
├── agente-ia/
│   ├── declaracoes/  ← 📄 PDFs aqui!
│   │   ├── declaracao_MAT1_matricula_20240223143052.pdf
│   │   ├── declaracao_MAT1_frequencia_20240223143100.pdf
│   │   └── ...
```

## 🎨 Características dos PDFs

✨ **Profissional e Oficial**
- Cabeçalho com informações da instituição
- Watermark "DOCUMENTO OFICIAL"
- Dados completos do aluno
- Tabela com disciplinas
- Assinaturas (secretária e coordenador)
- Código de validação único
- Data e hora de emissão
- Rodapé com credenciamento

📊 **Conteúdo Based on Template**
```html
<!-- Estrutura profissional do template -->
<header>INST. EDUCAÇÃO EXEMPLAR</header>
<title>DECLARAÇÃO DE MATRÍCULA</title>
<content>
  Declaramos para os devidos fins que [ALUNO],
  portador(a) do CPF [CPF], matriculado(a) sob
  o número [MATRÍCULA]...
</content>
<signatures>
  Secretária Acadêmica: ___________
  Coordenador Pedagógico: ___________
</signatures>
```

## 🔧 Arquitetura do Sistema

```
Aluno: "declaração de matrícula"
    ↓
Agente IA (agente_ia_inteligente.py)
    ├─ Identifica: tipo="declaracao"
    ├─ Envia para MCP: criar_requerimento()
    ↓
MCP Server (mcp_escola_server.py)
    ├─ Função: gerar_pdf_declaracao()
    ├─ Carrega: templates/declaracao_template.html
    ├─ Template Engine: Jinja2
    │   └─ Renderiza HTML com dados reais
    ├─ PDF Generator: WeasyPrint
    │   └─ Converte HTML→PDF
    └─ Salva: declaracoes/declaracao_*.pdf
    ↓
Resposta: "✅ PDF gerado com sucesso!"
    ↓
Arquivo: declaracoes/declaracao_MAT1_matricula_20240223143052.pdf
```

## 📊 Dados Incluídos nos PDFs

| Campo | Automaticamente Preenchido | Origem |
|-------|---------------------------|--------|
| Nome do Aluno | ✅ Sim | Banco de dados |
| Matrícula | ✅ Sim | Banco de dados |
| CPF | ✅ Sim | Banco de dados |
| Curso | ✅ Sim | Banco de dados |
| Período | ✅ Sim | Banco de dados |
| Disciplinas Atuais | ✅ Sim | Banco de dados |
| Frequência | ✅ Sim | Banco de dados |
| Média | ✅ Sim | Banco de dados |
| Data/Hora | ✅ Sim | Sistema |
| Código Validação | ✅ Sim | Gerado |

## 🔐 Recursos de Segurança

- ✅ Código de validação único (hash MD5)
- ✅ Watermark "DOCUMENTO OFICIAL"
- ✅ Data e hora de emissão registrada
- ✅ IP de emissão registrado
- ✅ URL de verificação no PDF
- ✅ Assinaturas digitais (suporte futuro)

## 💻 Requisitos Técnicos

### Instalado ✅
- Python 3.10+
- SQLite (banco de dados)
- FastMCP (servidor MCP)

### Novo 📦
- **WeasyPrint** (60.1+) - Converte HTML para PDF
- **Jinja2** (3.1.2+) - Renderiza templates HTML
- **ReportLab** (4.0.7+) - Fallback alternativo

## 🛠️ Troubleshooting

### Erro: "weasyprint not found"
```bash
# Solução:
..\ambiente\Scripts\python.exe -m pip install weasyprint
```

### Erro: "Template not found"
Verifique se existe:
```
C:\Users\...\Downloads\AgenteIa\templates\declaracao_template.html
```

### PDF vazio ou corrompido
- Verifique se o template HTML é válido
- Procure erros em `mcp_server.log`
- Execute `teste_pdf.py` para diagnosticar

## 📱 Visualizar PDFs

### Windows
```bash
start declaracoes\declaracao_MAT1_matricula_20240223143052.pdf
```

### Linux
```bash
xdg-open declaracoes/declaracao_MAT1_matricula_20240223143052.pdf
```

### Mac
```bash
open declaracoes/declaracao_MAT1_matricula_20240223143052.pdf
```

## 🎯 Próximas Melhorias

- [ ] Assinatura digital eletrônica
- [ ] QR Code para verificação
- [ ] Envio automático por email
- [ ] Portal de validação online
- [ ] Suporte a múltiplas assinaturas
- [ ] Templates customizáveis

## 📚 Documentação Relacionada

- [PDF_TEMPLATE_GUIA.md](PDF_TEMPLATE_GUIA.md) - Guia detalhado do sistema
- [AGENTE_MELHORADO.md](AGENTE_MELHORADO.md) - Melhorias gerais do agente
- [SUMARIO_ALTERACOES.md](SUMARIO_ALTERACOES.md) - Histórico de mudanças

## 🤝 Suporte

Se encontrar problemas:

1. Execute `teste_pdf.py` para diagnosticar
2. Verifique os logs em `agente-ia/mcp_server.log`
3. Procure erros Python no terminal
4. Consulte a documentação acima

## ✅ Checklist de Uso

- [ ] Dependências instaladas (`pip install weasyprint jinja2`)
- [ ] Teste passou (`teste_pdf.py`)
- [ ] MCP Server rodando (porta 8000)
- [ ] Agente IA conectado
- [ ] Aluno identificado (ID)
- [ ] Solicitação de declaração feita
- [ ] PDF gerado em `declaracoes/`

---

**🎉 Bem-vindo ao sistema profissional de geração de declarações em PDF! 🎉**

Sistema totalmente funcional e pronto para produção.
