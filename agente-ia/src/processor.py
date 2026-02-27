"""
Agente IA - Processadores e Helpers
Parte 4 de 4: Funções auxiliares e processamento
"""
import unicodedata

def normalizar_texto(texto):
    """Normaliza texto removendo acentos e convertendo para minusculas"""
    texto_normalizado = unicodedata.normalize("NFD", texto)
    texto_sem_acento = "".join(ch for ch in texto_normalizado if unicodedata.category(ch) != "Mn")
    return texto_sem_acento.lower()

def confirmar_acao(pergunta_sem_acento):
    """Detecta confirmacao para executar acao pendente"""
    import re
    confirmacoes_frases = ["pode abrir", "pode fazer"]
    confirmacoes_palavras = ["sim", "pode", "ok", "confirmo", "quero", "faca", "prosseguir"]
    
    if any(frase in pergunta_sem_acento for frase in confirmacoes_frases):
        return True
    
    return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in confirmacoes_palavras)

def negar_acao(pergunta_sem_acento):
    """Detecta negativa para cancelar acao"""
    import re
    negativas_frases = ["nao quero", "nao precisa", "nao precisa nao"]
    negativas_palavras = ["nao", "cancela", "cancelar", "deixa", "deixe", "pare", "parar"]
    
    if any(frase in pergunta_sem_acento for frase in negativas_frases):
        return True
    
    return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in negativas_palavras)

def eh_texto_confessional(pergunta_sem_acento):
    """Detecta confissao/intencao que deve pedir confirmacao"""
    import re
    gatilhos_frases = ["nao gostei"]
    gatilhos_palavras = ["quero", "gostaria", "preciso", "vou", "pretendo", "decidi"]
    
    if any(frase em pergunta_sem_acento for frase in gatilhos_frases):
        return True
    
    return any(re.search(rf"\b{re.escape(palavra)}\b", pergunta_sem_acento) for palavra in gatilhos_palavras)

__all__ = [
    'normalizar_texto',
    'confirmar_acao', 
    'negar_acao',
    'eh_texto_confessional',
]
