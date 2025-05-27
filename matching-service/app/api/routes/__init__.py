# Ce fichier permet à Python de traiter le répertoire routes comme un package

from fastapi import APIRouter

# Créer un router principal pour ce module
router = APIRouter()

# Import et inclusion des sous-modules de routes
try:
    from .matches import matches_bp
    from .algorithms import algorithms_bp
    
    # Pour FastAPI, on peut créer des sous-routers si nécessaire
    # ou rediriger vers les blueprints Flask existants
    
except ImportError:
    # Si les imports échouent, créer un router minimal
    pass

# Routes de base pour le matching
@router.get("/health")
async def health():
    return {"status": "ok", "module": "matching routes"}
