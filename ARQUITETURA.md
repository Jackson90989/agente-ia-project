# Arquitetura do Projeto - AgenteIa

## Estrutura Geral

```
AgenteIa/
├── src/                          # Código principal organizado
│   ├── models/                   # Camada de Modelos de Dados
│   │   ├── __init__.py
│   │   ├── aluno.py             # Model Aluno
│   │   ├── usuario.py           # Model Usuario
│   │   ├── curso.py             # Model Curso
│   │   ├── materia.py           # Model Materia
│   │   ├── matricula.py         # Models Matricula e MatriculaMateria
│   │   ├── requerimento.py      # Model Requerimento
│   │   └── pagamento.py         # Model Pagamento
│   │
│   ├── routes/                   # Camada de Rotas (API)
│   │   ├── __init__.py
│   │   ├── alunos.py
│   │   ├── auth.py
│   │   ├── cursos.py
│   │   ├── materias.py
│   │   ├── pagamentos.py
│   │   ├── portal.py
│   │   └── requerimentos.py
│   │
│   ├── services/                 # Camada de Negócios
│   │   ├── __init__.py
│   │   ├── aluno_service.py      # Lógica de alunos
│   │   ├── auth_service.py       # Lógica de autenticação
│   │   ├── curso_service.py      # Lógica de cursos
│   │   ├── materia_service.py    # Lógica de matérias
│   │   ├── matricula_service.py  # Lógica de matrículas
│   │   ├── requerimento_service.py
│   │   ├── pagamento_service.py
│   │   └── mcp_integration.py    # Integração com MCP
│   │
│   ├── core/                     # Camada de Núcleo/Infraestrutura
│   │   ├── __init__.py
│   │   ├── errors.py             # Exceções customizadas
│   │   ├── logger.py             # Configuração de logging
│   │   ├── security.py           # Funções de segurança
│   │   └── pdf_generator.py      # Geração de PDF
│   │
│   ├── utils/                    # Utilitários
│   │   ├── __init__.py
│   │   ├── constants.py          # Constantes da aplicação
│   │   ├── validators.py         # Validadores de entrada
│   │   ├── formatters.py         # Formatação de dados
│   │   ├── helpers.py            # Funções auxiliares
│   │   └── decorators.py         # Decoradores customizados
│   │
│   ├── app.py                    # Factory da aplicação Flask
│   ├── config.py                 # Configuração
│   ├── database.py               # Conexão com BD
│   ├── extensions.py             # Extensões (Flask-CORS, etc)
│   ├── templates/                # Templates HTML
│   └── static/                   # Arquivos estáticos
│
├── agente-ia/                    # Agente IA separado
│   ├── src/
│   │   ├── agente_ia_inteligente.py
│   │   ├── mcp/
│   │   │   ├── cliente_mcp.py
│   │   │   ├── mcp_escola_server.py
│   │   │   └── database_adapter.py
│   │   └── utils/
│   ├── config.py
│   └── requirements.txt
│
├── tests/                        # Testes (Unit, Integration, Regression)
│   ├── unit/
│   ├── integration/
│   ├── regression/
│   └── security/
│
├── logs/                         # Logs da aplicação
├── declaracoes/                  # PDFs gerados
├── app.py                        # Entry point (compatibilidade)
├── models.py                     # Entry point (compatibilidade)
├── requirements.txt
└── README.md
```

## Camadas de Arquitetura

### 1. **Camada de Rotas (routes/)**
- Responsável por expor os endpoints da API
- Validação de entrada
- Delegação para services
- Resposta ao cliente

**Exemplo:**
```python
# routes/alunos.py
@alunos_bp.route('/<int:id>', methods=['GET'])
@requer_autenticacao
def get_aluno(id):
    aluno = aluno_service.obter_aluno(id)
    return jsonify(aluno.to_dict())
```

### 2. **Camada de Serviços (services/)**
- Lógica de negócios isolada
- Regras de domínio
- Transações e coordenação
- Independente de HTTP

**Exemplo:**
```python
# services/aluno_service.py
def cadastrar_aluno(dados):
    validar_campos_obrigatorios(dados, ['nome', 'cpf', 'email'])
    
    aluno = Aluno(**dados)
    db.session.add(aluno)
    db.session.commit()
    return aluno
```

### 3. **Camada de Modelos (models/)**
- Definição das entidades de domínio
- Relacionamentos
- Métodos de negócio (ex: gerar_token)
- Serialização (to_dict)

**Exemplo:**
```python
# models/aluno.py
class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200))
    
    def set_senha(self, senha):
        self.senha_hash = bcrypt.hashpw(...)
```

### 4. **Camada de Núcleo (core/)**
- Exceções customizadas
- Logging
- Segurança (hash, tokens)
- Geração de PDF
- **NÃO depende de nenhuma outra camada**

### 5. **Camada de Utilitários (utils/)**
- Constantes globais
- Validadores de entrada
- Formatadores de saída
- Funções auxiliares
- Decoradores

## Padrões de Uso

### Criando uma Nova Rota

1. **Adicionar ao services/:**
```python
# services/novo_servico.py
from src.core import ValidationError
from src.models import MeuModel

def criar_recurso(dados):
    # Validar
    if not dados.get('nome'):
        raise ValidationError("Nome é obrigatório")
    
    # Processar
    recurso = MeuModel(**dados)
    db.session.add(recurso)
    db.session.commit()
    
    return recurso
```

2. **Adicionar à rota:**
```python
# routes/novo_route.py
from flask import Blueprint, request, jsonify
from services.novo_servico import criar_recurso
from src.core import ValidationError, get_logger

novo_bp = Blueprint('novo', __name__)
logger = get_logger(__name__)

@novo_bp.route('/', methods=['POST'])
def post_novo():
    try:
        recurso = criar_recurso(request.get_json())
        return jsonify(recurso.to_dict()), 201
    except ValidationError as e:
        logger.warning(f"Validação falhou: {e}")
        return jsonify({'erro': str(e)}), 400
```

3. **Registrar em app.py:**
```python
# app.py
from routes.novo_route import novo_bp
app.register_blueprint(novo_bp, url_prefix='/api/novo')
```

## Benefícios da Arquitetura

✅ **Separação de Responsabilidades** - Cada camada tem uma função clara
✅ **Reutilização** - Services podem ser usados por múltiplas rotas
✅ **Testabilidade** - Services podem ser testados isoladamente
✅ **Manutenibilidade** - Código organizado e fácil de encontrar
✅ **Escalabilidade** - Fácil adicionar novos features
✅ **Segurança** - Validações e tratamento de erros centralizados

## Migrando Código Existente

Para arquivos antigos como `models.py` e scripts antigos:

1. Models → `src/models/`
2. Services → `src/services/`
3. Constantes → `src/utils/constants.py`
4. Validações → `src/utils/validators.py`
5. Exceções → `src/core/errors.py`

## Entry Points

Para **compatibilidade backward**, mantemos:
- `app.py` → importa de `src/` internamente
- `models.py` → re-exporta de `src/models/`

Novos projetos devem importar diretamente de `src/`.
