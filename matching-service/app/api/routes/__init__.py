# Ce fichier permet à Python de traiter le répertoire routes comme un package

from fastapi import APIRouter

# Import du router depuis le fichier routes.py du niveau parent
from app.api.routes import router as main_router

# Export du router pour que l'import depuis main.py fonctionne
router = main_router
