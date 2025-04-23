import os

class Config:
    """Configuration de base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    
    # Services URLs
    USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL') or 'http://user-service:5000'
    CV_PARSER_SERVICE_URL = os.environ.get('CV_PARSER_SERVICE_URL') or 'http://cv-parser-service:5000'
    PROFILE_SERVICE_URL = os.environ.get('PROFILE_SERVICE_URL') or 'http://profile-service:5000'
    MATCHING_SERVICE_URL = os.environ.get('MATCHING_SERVICE_URL') or 'http://matching-service:5000'
    JOB_SERVICE_URL = os.environ.get('JOB_SERVICE_URL') or 'http://job-service:5000'
    NOTIFICATION_SERVICE_URL = os.environ.get('NOTIFICATION_SERVICE_URL') or 'http://notification-service:5000'
    
    # Paramètres de l'application
    TIMEOUT = int(os.environ.get('REQUEST_TIMEOUT') or '5')  # Timeout en secondes
    
    @staticmethod
    def init_app(app):
        """Initialisation de l'application avec la configuration"""
        pass

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Configuration de test"""
    TESTING = True
    DEBUG = True

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
        
        file_handler = RotatingFileHandler('logs/gateway.log', maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Gateway startup')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
