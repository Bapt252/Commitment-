# Tests pour Nexten SmartMatch

Ce document décrit comment exécuter les tests du système de matching bidirectionnel Nexten SmartMatch.

## Prérequis

- Python 3.8 ou supérieur
- Modules requis installés (`pip install -r requirements.txt`)

## Utilisation rapide

```bash
# Rendre les scripts exécutables
chmod +x test-smartmatch.sh

# Exécuter tous les tests
./test-smartmatch.sh

# Exécuter uniquement les tests unitaires
./test-smartmatch.sh unit

# Exécuter uniquement les tests d'intégration
./test-smartmatch.sh integration

# Exécuter uniquement les tests de performance
./test-smartmatch.sh performance
```

## Structure des tests

Les tests sont organisés dans les fichiers suivants :

- `test_travel_time.py`: Tests unitaires pour le calcul des temps de trajet via l'API Google Maps
- `test_semantic_analysis.py`: Tests unitaires pour l'analyse sémantique des compétences
- `test_smartmatch.py`: Tests unitaires pour le moteur de matching principal
- `test_integration.py`: Tests d'intégration pour l'ensemble du système
- `test_performance.py`: Tests de performance pour évaluer la rapidité du système

## Génération de données de test

Le script `test_data_generator.py` permet de générer des données de test pour les candidats et les entreprises. Ces données sont utilisées par les tests.

```bash
python -m tests.test_data_generator
```

## Utilisation de l'API Google Maps pour les tests

Les tests unitaires et d'intégration utilisent des mocks pour éviter d'avoir besoin d'une clé API Google Maps réelle. Cependant, si vous souhaitez exécuter des tests contre l'API réelle, vous devez configurer la variable d'environnement `GOOGLE_MAPS_API_KEY` :

```bash
export GOOGLE_MAPS_API_KEY="votre_clé_api_google_maps"
```

## Rapport de couverture des tests

Pour générer un rapport de couverture des tests, vous pouvez utiliser `coverage` :

```bash
pip install coverage
coverage run run_tests.py
coverage report -m
```

Cela vous montrera le pourcentage de code testé et les lignes non couvertes.
