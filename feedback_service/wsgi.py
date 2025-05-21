"""
Point d'entrée WSGI pour le service de feedback.
"""

from feedback_service.api.app import app

if __name__ == "__main__":
    app.run()
