import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///escola.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    
    # Configurações MCP
    MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:5001')
    MCP_API_KEY = os.getenv('MCP_API_KEY', 'mcp-api-key')