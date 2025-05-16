#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des clés API
------------------------------
Fournit des fonctions pour récupérer les clés API depuis différentes sources.

Auteur: Claude
Date: 16/05/2025
"""

import os
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

def get_maps_api_key():
    """
    Récupère la clé API Google Maps depuis différentes sources
    
    Returns:
        str: Clé API Google Maps ou None
    """
    # Ordre de priorité: variable d'environnement, fichier .env, fichier de configuration
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        # Essayer de charger depuis le fichier .env
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_MAPS_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip('"\'')
                            break
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du fichier .env: {e}")
    
    if not api_key:
        # Essayer de charger depuis le fichier de configuration
        try:
            if os.path.exists('config.py'):
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", "config.py")
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                
                if hasattr(config, 'GOOGLE_MAPS_API_KEY'):
                    api_key = config.GOOGLE_MAPS_API_KEY
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du fichier de configuration: {e}")
    
    return api_key