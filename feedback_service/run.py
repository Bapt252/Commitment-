"""
Script pour démarrer le service de feedback.
"""

import os
from feedback_service.api.app import app

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5058))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host="0.0.0.0", port=port, debug=debug)
