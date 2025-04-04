"""
Initialisation des API pour l'application.
"""

from fastapi import APIRouter

# Import des endpoints
from .endpoints import matching

# Création du routeur principal
api_router = APIRouter()

# Ajout des sous-routeurs
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
