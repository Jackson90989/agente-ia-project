"""List tables and row counts for integration sanity checks."""

from app import create_app
from database import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print("Tabelas encontradas:")
    for table in tables:
        print(f"  - {table}")
        
        # Contar registros
        from sqlalchemy import text
        result = db.session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"    Registros: {result}")