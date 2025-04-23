import psycopg2
import psycopg2.extras
from flask import g, current_app

def setup_db(app):
    """Configure la connexion à la base de données PostgreSQL."""
    app.teardown_appcontext(close_db_connection)

def get_db_connection():
    """Obtient une connexion à la base de données depuis le contexte de l'application ou en crée une nouvelle."""
    if 'db' not in g:
        # Créer une nouvelle connexion
        g.db = psycopg2.connect(
            dbname=current_app.config['POSTGRES_DB'],
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD'],
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT']
        )
        # Configurer la connexion pour renvoyer des dictionnaires
        g.db.autocommit = False
        g.db.cursor_factory = psycopg2.extras.RealDictCursor
    
    return g.db

def close_db_connection(e=None):
    """Ferme la connexion à la base de données."""
    db = g.pop('db', None)
    
    if db is not None:
        # Rollback de toutes les transactions non validées
        if not db.closed:
            db.rollback()
            db.close()

def setup_audit_context(conn, user_id, ip_address=None, app_user=None):
    """Configure le contexte d'audit pour tracer les modifications."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT set_app_context(%s, %s, %s)",
            (str(user_id) if user_id else None, ip_address, app_user or "api")
        )
    finally:
        cursor.close()