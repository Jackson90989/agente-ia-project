# Guia de Migração de Imports

## 📦 Estrutura Antiga vs Nova

### Models

**Antes:**
```python
from models import Aluno, Usuario, Curso, Materia, Matricula, Requerimento, Pagamento
```

**Depois:**
```python
# Opção 1: Importar do package
from src.models import Aluno, Usuario, Curso, Materia

# Opção 2: Importar direto
from src.models.aluno import Aluno
from src.models.usuario import Usuario
```

### Services

**Antes:**
```python
from services.requerimento_service import RequerimentoService
from services.pagamento_service import gerar_boleto
```

**Depois:**
```python
# Services continuam em services/
from services.requerimento_service import RequerimentoService
from services.pagamento_service import gerar_boleto

# OU (nova estrutura, quando migrado para src/)
from src.services.requerimento_service import RequerimentoService
```

### Utilitários

**Antes:**
```python
# Validações dispersas em vários arquivos
from utils import validar_cpf  # se existisse
```

**Depois:**
```python
from src.utils import validar_cpf, formatar_cpf, validar_email
from src.utils.constants import ALUNO_STATUS_ATIVO
from src.utils.helpers import gerar_matricula, calcular_idade
```

### Exceções

**Antes:**
```python
raise Exception("Erro genérico")
try:
    ...
except:  # Bad practice!
    pass
```

**Depois:**
```python
from src.core import ValidationError, DatabaseError, NotFoundError

raise ValidationError("Email inválido")
try:
    ...
except DatabaseError as e:
    logger.error(f"DB error: {e}")
except ValidationError as e:
    logger.warning(f"Validation: {e}")
```

### Logging

**Antes:**
```python
import logging

logger = logging.getLogger(__name__)
```

**Depois:**
```python
from src.core import get_logger

logger = get_logger(__name__)
```

### Segurança

**Antes:**
```python
import hashlib

hash_value = hashlib.md5(password).hexdigest()  # ❌ INSEGURO
```

**Depois:**
```python
from src.core.security import hash_password, generate_code

hash_value = hash_password(password)  # ✅ SEGURO (bcrypt)
codigo = generate_code(10)  # Alfanumérico
numero = generate_numeric_code(8)  # Apenas números
```

## 🎯 Mapeamento Rápido

| Antes | Depois | Arquivo |
|-------|--------|---------|
| `from models import *` | `from src.models import *` | src/models/__init__.py |
| `from services import *` | `from services import *` ou `from src.services import *` | services/ ou src/services/ |
| Validação manual | `from src.utils.validators import validar_cpf` | src/utils/validators.py |
| Constantes espalhadas | `from src.utils.constants import ALUNO_STATUS_ATIVO` | src/utils/constants.py |
| `logging.getLogger()` | `from src.core import get_logger` | src/core/logger.py |
| `hashlib.md5()` | `from src.core.security import hash_password` | src/core/security.py |
| `jwt.encode()` manual | Use model.generate_token() | src/models/aluno.py |
| `Exception` genérico | `from src.core import ValidationError` | src/core/errors.py |

## 📝 Checklist de Migração

Para cada arquivo a migrar:

- [ ] Identificar imports de models
- [ ] Identificar validações
- [ ] Identificar logging
- [ ] Identificar exceções
- [ ] Atualizar imports para src/
- [ ] Usar validadores de src.utils
- [ ] Usar logger de src.core
- [ ] Usar exceções de src.core
- [ ] Testar arquivo

## 🔗 Transição Suave

Você pode migrar **gradualmente**:

1. Novos arquivos já importam de `src/`
2. Arquivos antigos podem continuar importando de forma antiga
3. Depois de testar, atualiza os imports

**Exemplo:** routes/alunos.py pode ter:
```python
# Ainda funciona (compatível)
from models import Aluno

# Novo (preferido)
from src.models import Aluno
```

## ⚠️ Evitar

❌ Não misture imports:
```python
from models import Aluno
from src.models import Usuario  
```

✅ Padronize:
```python
from src.models import Aluno, Usuario
```

---

**Dica:** Use find-replace no seu editor para atualizar tudo de uma vez!
