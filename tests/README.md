# Tests pour Nexten SmartMatch

Ce répertoire contient les tests pour le système de matching bidirectionnel Nexten SmartMatch.

## Structure des tests

- `test_travel_time.py`: Tests unitaires pour le calcul des temps de trajet via l'API Google Maps
- `test_semantic_analysis.py`: Tests unitaires pour l'analyse sémantique des compétences
- `test_smartmatch.py`: Tests unitaires pour le moteur de matching principal
- `test_integration.py`: Tests d'intégration pour l'ensemble du système
- `test_performance.py`: Tests de performance pour évaluer la rapidité du système
- `test_data_generator.py`: Générateur de données de test

## Exécution des tests

Vous pouvez exécuter tous les tests en utilisant le script `run_tests.py` à la racine du projet :

```bash
python run_tests.py
```

Pour exécuter un type spécifique de tests :

```bash
python run_tests.py --type unit        # Tests unitaires uniquement
python run_tests.py --type integration  # Tests d'intégration uniquement
python run_tests.py --type performance  # Tests de performance uniquement
```

Vous pouvez également exécuter un fichier de test spécifique directement :

```bash
python -m tests.test_travel_time
python -m tests.test_semantic_analysis
python -m tests.test_smartmatch
python -m tests.test_integration
python -m tests.test_performance
```

## Générer des données de test

Pour générer de nouvelles données de test :

```bash
python -m tests.test_data_generator
```

Les données seront générées dans le répertoire `test_data/`.

## Configuration requise pour les tests

- Les tests utilisent `unittest.mock` pour simuler les appels à l'API Google Maps, donc pas besoin d'une clé API pour les tests unitaires et d'intégration
- Pour les tests qui nécessitent un accès à l'API Google Maps réelle, vous devez configurer la variable d'environnement `GOOGLE_MAPS_API_KEY`

## Couverture des tests

Pour générer un rapport de couverture des tests, vous pouvez utiliser `coverage` :

```bash
pip install coverage
coverage run run_tests.py
coverage report -m
```

Cela vous montrera le pourcentage de code testé et les lignes non couvertes.
