#!/usr/bin/env python
import os
import sys

# Ajout du répertoire courant au path Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import de l'application Flask
from api.app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
