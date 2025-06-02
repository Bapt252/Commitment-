#!/usr/bin/env python3
"""
SuperSmartMatch V2 - Service principal unifié
Port: 5070

Service intelligent qui unifie :
- Nexten Matcher (port 5052) - 40K lignes ML avancé
- SuperSmartMatch V1 (port 5062) - 4 algorithmes existants

Objectif: +13% précision via sélection intelligente d'algorithmes
"""

import os
import sys
import logging
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.main import app
from app.config import get_config
from app.logger import setup_logging

def main():
    """Point d'entrée principal du service SuperSmartMatch V2"""
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Configuration
    config = get_config()
    
    logger.info("🚀 Démarrage SuperSmartMatch V2")
    logger.info(f"📍 Port: {config.port}")
    logger.info(f"🧠 Sélection intelligente: {'✅' if config.enable_smart_selection else '❌'}")
    logger.info(f"🥇 Nexten integration: {'✅' if config.enable_nexten else '❌'}")
    logger.info(f"🔄 V1 compatibility: {'✅' if config.enable_v1_compatibility else '❌'}")
    
    # Démarrage du serveur
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.port,
        reload=config.debug,
        log_level="info" if not config.debug else "debug",
        access_log=True,
        loop="auto"
    )

if __name__ == "__main__":
    main()