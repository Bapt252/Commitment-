#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script d'exécution des tests pour le système SmartMatch."""

import unittest
import sys
import os
import logging
import argparse

def setup_logging():
    """Configure le logging pour les tests."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('test_results.log', mode='w')
        ]
    )

def run_all_tests():
    """Découvre et exécute tous les tests."""
    setup_logging()
    logging.info("Démarrage des tests SmartMatch")
    
    # Découvrir les tests
    loader = unittest.TestLoader()
    start_dir = './tests'
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher le résumé
    logging.info(f"Tests terminés. Succès: {result.testsRun - len(result.failures) - len(result.errors)}, "  
                 f"Échecs: {len(result.failures)}, Erreurs: {len(result.errors)}")
    
    # Retourner le code d'état approprié
    return 0 if result.wasSuccessful() else 1

def run_specific_tests(test_type=None):
    """Exécute une catégorie spécifique de tests."""
    setup_logging()
    logging.info(f"Démarrage des tests SmartMatch de type: {test_type}")
    
    # Découvrir les tests
    loader = unittest.TestLoader()
    start_dir = './tests'
    
    if test_type == "unit":
        # Tests unitaires
        pattern = "test_[a-z]*.py"  # Exclut les tests d'intégration et de performance
    elif test_type == "integration":
        # Tests d'intégration
        pattern = "test_integration.py"
    elif test_type == "performance":
        # Tests de performance
        pattern = "test_performance.py"
    else:
        # Tous les tests
        pattern = "test_*.py"
    
    suite = loader.discover(start_dir, pattern=pattern)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher le résumé
    logging.info(f"Tests terminés. Succès: {result.testsRun - len(result.failures) - len(result.errors)}, "  
                 f"Échecs: {len(result.failures)}, Erreurs: {len(result.errors)}")
    
    # Retourner le code d'état approprié
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exécuter les tests pour SmartMatch")
    parser.add_argument('--type', choices=['unit', 'integration', 'performance', 'all'], 
                        default='all', help='Type de tests à exécuter')
    
    args = parser.parse_args()
    
    if args.type == 'all':
        sys.exit(run_all_tests())
    else:
        sys.exit(run_specific_tests(args.type))
