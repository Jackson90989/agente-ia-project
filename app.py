from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database import db, migrate
from src.models import (
    Aluno, Usuario, Curso, Materia,
    Matricula, MatriculaMateria, Requerimento, Pagamento
)

# Importar blueprints
from routes.alunos import alunos_bp
from routes.materias import materias_bp
from routes.requerimentos import requerimentos_bp
from routes.pagamentos import pagamentos_bp
from routes.auth import auth_bp
from routes.portal import portal_bp
from routes.cursos import cursos_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Registrar blueprints
    app.register_blueprint(alunos_bp, url_prefix='/api/alunos')
    app.register_blueprint(materias_bp, url_prefix='/api/materias')
    app.register_blueprint(requerimentos_bp, url_prefix='/api/requerimentos')
    app.register_blueprint(pagamentos_bp, url_prefix='/api/pagamentos')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(portal_bp)
    app.register_blueprint(cursos_bp, url_prefix='/api/cursos')
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'API do Sistema Escolar',
            'version': '1.0.0',
            'endpoints': {
                'alunos': '/api/alunos',
                'materias': '/api/materias',
                'requerimentos': '/api/requerimentos',
                'pagamentos': '/api/pagamentos'
            }
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config.get('DEBUG', False),
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000)
    )