# 🚀 Guia Rápido - Sistema Agente IA

## 📦 Instalação (primeira vez)

```batch
instalar_completo.bat
```

Este script vai:
- Criar o ambiente virtual Python
- Instalar todas as dependências
- Verificar se tudo está funcionando

## ▶️ Iniciar o Sistema

### Opção 1: Sistema Completo (recomendado)
```batch
iniciar_sistema.bat
```
Abre 3 terminais:
- Flask API (Backend)
- MCP Server (Ferramentas)
- Agente IA (Interface)

### Opção 2: Apenas Agente IA (simples)
```batch
iniciar_sistema_unico.bat
```
Abre apenas o Agente IA em um terminal.

## 🛑 Parar o Sistema

```batch
parar_sistema.bat
```
Para todos os processos relacionados ao sistema.

## 📋 Ordem de Execução

1. **Primeira vez:**
   ```batch
   instalar_completo.bat
   ```

2. **Iniciar sistema:**
   ```batch
   iniciar_sistema.bat
   ```

3. **Usar o agente:**
   - Digite perguntas no terminal do Agente IA
   - Exemplos: "minhas matérias", "minhas notas", "meus boletos"

4. **Parar sistema:**
   ```batch
   parar_sistema.bat
   ```
   OU simplesmente feche os terminais

## ⚠️ Troubleshooting

### Erro: "Ambiente virtual não encontrado"
```batch
instalar_completo.bat
```

### Erro: "Porta já em uso"
```batch
parar_sistema.bat
iniciar_sistema.bat
```

### Ferramentas não encontradas
1. Pare tudo: `parar_sistema.bat`
2. Inicie novamente: `iniciar_sistema.bat`
3. Aguarde 10 segundos para tudo carregar

## 📂 Estrutura de Scripts

| Script | Função |
|--------|--------|
| `instalar_completo.bat` | Instalação completa do zero |
| `iniciar_sistema.bat` | Inicia tudo (3 terminais) |
| `iniciar_sistema_unico.bat` | Inicia apenas o agente |
| `parar_sistema.bat` | Para todos os processos |

## 🎯 Exemplos de Uso

Após iniciar o sistema, digite no Agente IA:

```
- "quem sou eu?"
- "minhas matérias"
- "minhas notas"  
- "meus boletos"
- "resumo acadêmico"
- "quero adicionar a matéria ALG-101"
```

## 📞 Suporte

Ver documentação completa em:
- `README.md` - Documentação completa
- `agente-ia\TROUBLESHOOTING_FERRAMENTAS.md` - Solução de problemas
