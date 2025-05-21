#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration du service de personnalisation
"""

import os
from dotenv import load_dotenv
import logging

# Chargement des variables d'environnement
load_dotenv()

# Configuration de base
SERVICE_NAME = "personalization-service"
SERVICE_VERSION = "1.0.0"
PORT = int(os.getenv('PORT', 5060))
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Configuration du niveau de log
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_FORMAT = os.getenv('LOG_FORMAT', 'json').lower()

# Configuration de la base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/nexten')

# Configuration de Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

# Configuration des services externes
MATCHING_SERVICE_URL = os.getenv('MATCHING_SERVICE_URL', 'http://matching-api:5000')

# Configuration du service de personnalisation
AB_TESTING_ENABLED = os.getenv('AB_TESTING_ENABLED', 'false').lower() == 'true'
COLLABORATIVE_FILTER_ENABLED = os.getenv('COLLABORATIVE_FILTER_ENABLED', 'true').lower() == 'true'
TEMPORAL_DRIFT_ENABLED = os.getenv('TEMPORAL_DRIFT_ENABLED', 'true').lower() == 'true'

# Paramètres de démarrage à froid
MIN_INTERACTIONS_FOR_PREFERENCES = int(os.getenv('MIN_INTERACTIONS_FOR_PREFERENCES', 3))

# Paramètres de filtrage collaboratif
MAX_SIMILAR_USERS = int(os.getenv('MAX_SIMILAR_USERS', 10))

# Paramètres de dérive temporelle
TEMPORAL_DRIFT_HALF_LIFE_DAYS = int(os.getenv('TEMPORAL_DRIFT_HALF_LIFE_DAYS', 30))

# Configuration du format de journalisation
if LOG_FORMAT == 'json':
    LOG_FORMATTER = logging.Formatter(r'{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}')
else:
    LOG_FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configuration CORS
CORS_ORIGINS = ["*"]

# Configuration des métriques de surveillance
METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
