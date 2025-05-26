from flask import Flask
from api.routes import behavior_api
import logging
import os

# Configuration du logging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.register_blueprint(behavior_api, url_prefix='/api')

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé."""
    return {'status': 'healthy', 'service': 'user-behavior-api'}

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')
