# CV Parser Service - Point d'entrée principal

# Import du module de compatibilité OpenAI
import compat

import uvicorn
import logging
from app import app
from app.core.config import settings

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Démarrer le serveur FastAPI
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
