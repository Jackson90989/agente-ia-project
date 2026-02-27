"""
Configuração de logging
"""
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(app):
    """Configura logging para a aplicação"""
    
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar logger da aplicação
    logger = logging.getLogger('agente_ia')
    logger.setLevel(logging.DEBUG)
    
    # Handler para arquivo
    file_handler = RotatingFileHandler(
        'logs/agente_ia.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name):
    """Obtém um logger com o nome especificado"""
    return logging.getLogger(f'agente_ia.{name}')
