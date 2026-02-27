"""
Funções de segurança
"""
import hashlib
import secrets
import string


def generate_secure_token(length=32):
    """Gera um token seguro"""
    return secrets.token_urlsafe(length)


def hash_password(password):
    """Faz hash de uma senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hash_value):
    """Verifica se uma senha corresponde ao hash"""
    return hash_password(password) == hash_value


def generate_code(length=10):
    """Gera um código alfanumérico seguro"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_numeric_code(length=10):
    """Gera um código numérico seguro"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))
