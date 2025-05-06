import os

class Config:
    """Configuration de base"""
    # Support des deux noms de variables d'environnement
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI')
    MONGODB_URI = os.environ.get('MONGODB_URI') or 'mongodb://localhost:27017/job_data'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
    
    @staticmethod
    def init_app(app):
        """Initialisation de l'application avec la configuration"""
        # Création du dossier d'upload si nécessaire
        upload_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), app.config['UPLOAD_FOLDER'])
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuration de test"""
    TESTING = True
    DEBUG = True
    MONGODB_URI = os.environ.get('TEST_MONGODB_URI') or 'mongodb://localhost:27017/test_job_data'

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configuration de logging pour la production
        import logging
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler('logs/job-parser.log', maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Job Parser Service startup')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
