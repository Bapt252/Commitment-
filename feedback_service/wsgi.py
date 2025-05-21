"""
Point d'entrée WSGI pour le service de feedback.
"""

from api.app import app

if __name__ == "__main__":
    app.run()
