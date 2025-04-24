from flask import Flask, jsonify
from flask_cors import CORS
import logging
import os

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/commitment')
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    app.config['CV_PARSER_SERVICE_URL'] = os.environ.get('CV_PARSER_SERVICE_URL', 'http://cv-parser-service:5000')
    app.config['MATCHING_SERVICE_URL'] = os.environ.get('MATCHING_SERVICE_URL', 'http://matching-service:5000')
    
    # Extensions initialization
    CORS(app)
    
    # Import routes after extensions to avoid circular imports
    from app.routes import register_routes
    register_routes(app)
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    # Setup logging
    if not app.debug:
        logging.basicConfig(
            filename='logs/app.log',
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
