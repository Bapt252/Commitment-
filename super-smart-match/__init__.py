#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch - Service Unifié de Matching Intelligent
Version 1.0.0

Ce package contient tous les algorithmes de matching de Nexten
unifiés sous une seule API puissante et flexible.
"""

__version__ = "1.0.0"
__author__ = "Nexten Team"
__email__ = "contact@nexten.fr"
__license__ = "MIT"

# Imports principaux pour faciliter l'utilisation
from .core.engine import SuperSmartMatchEngine, MatchOptions, AlgorithmType
from .core.selector import AlgorithmSelector
from .utils.data_adapter import DataAdapter
from .utils.performance import PerformanceMonitor
from .utils.fallback import FallbackManager

# Configuration par défaut
DEFAULT_CONFIG = {
    "timeout": 30,
    "max_results": 50,
    "cache_enabled": True,
    "fallback_enabled": True,
    "performance_tracking": True
}

# Quick start function
def create_engine(config=None):
    """
    Fonction de création rapide d'un moteur SuperSmartMatch
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Instance de SuperSmartMatchEngine configurée
    """
    merged_config = {**DEFAULT_CONFIG, **(config or {})}
    return SuperSmartMatchEngine(merged_config)

def quick_match(candidat, offres, algorithme="auto", limite=10):
    """
    Fonction de matching rapide et simple
    
    Args:
        candidat: Données du candidat
        offres: Liste des offres d'emploi
        algorithme: Algorithme à utiliser (défaut: "auto")
        limite: Nombre maximum de résultats
        
    Returns:
        Résultats du matching
    """
    engine = create_engine()
    options = MatchOptions(
        algorithme=AlgorithmType(algorithme),
        limite=limite,
        details=True,
        explications=True
    )
    
    return engine.match(candidat, offres, options)

# Informations du package
__all__ = [
    "SuperSmartMatchEngine",
    "MatchOptions", 
    "AlgorithmType",
    "AlgorithmSelector",
    "DataAdapter",
    "PerformanceMonitor",
    "FallbackManager",
    "create_engine",
    "quick_match",
    "DEFAULT_CONFIG"
]
