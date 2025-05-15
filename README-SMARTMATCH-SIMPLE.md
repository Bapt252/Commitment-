# Guide d'intégration simplifié pour SmartMatch

Ce guide explique comment tester l'intégration simplifiée du système SmartMatch.

## Prérequis

- Python 3.7+
- Un fichier CV pour le test (format PDF, DOCX, ou TXT)

## Installation

1. Rendez les scripts exécutables :
```bash
chmod +x make-test-simple-executable.sh
./make-test-simple-executable.sh
```

## Utilisation

### Test simple

```bash
# Créer un exemple de description de poste
echo "Développeur Python avec expérience en FastAPI et traitement de données." > exemple_job.txt

# Exécuter le test avec votre CV et la description de poste
./test_smartmatch_simple.py --cv path/to/your/cv.pdf --job-file exemple_job.txt

# Ou directement avec une description de poste en ligne de commande
./test_smartmatch_simple.py --cv path/to/your/cv.pdf --job "Développeur Python avec expérience en FastAPI et traitement de données."
```

### Résultat attendu

Le script affichera des informations de log sur le processus de matching, y compris :
- La confirmation du chargement du CV
- Les détails du matching simulé
- Un score de matching et une répartition par catégorie

## Développement futur

Ce script simplifié est une première étape pour l'intégration complète de SmartMatch avec les services de parsing existants. Les prochaines étapes seraient :

1. Intégration avec les services de parsing de CV existants
2. Intégration avec les services de parsing de fiches de poste existants
3. Implémentation du moteur de matching bidirectionnel
4. Exposition d'une API REST complète

Pour développer ces fonctionnalités, nous recommandons de :
- Créer une branche spécifique pour éviter les conflits avec le code existant
- Suivre une approche progressive en intégrant un service à la fois
- Mettre en place des tests unitaires et d'intégration
