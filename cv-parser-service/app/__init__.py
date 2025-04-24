from flask import Flask
import logging
import os

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    # Health check route
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app
