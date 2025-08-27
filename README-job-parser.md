# Système d'Analyse de Fiches de Poste

Ce système permet d'analyser automatiquement des fiches de poste au format PDF ou texte brut pour en extraire les informations clés telles que le titre du poste, l'entreprise, la localisation, les compétences requises, etc.

## Architecture du système

Le système comprend trois composants principaux :

1. **Script CLI (job_parser_cli.py)** - Un outil en ligne de commande pour analyser individuellement des fichiers PDF de fiches de poste
2. **API REST (job-parser-api.py)** - Un service web permettant d'intégrer le parser à d'autres applications
3. **Bibliothèque JavaScript (job-parser-api.js)** - Une bibliothèque client pour intégrer facilement l'API dans des interfaces web

## Installation et configuration

### Prérequis

- Python 3.6 ou supérieur
- Bibliothèque PyPDF2 (`pip install PyPDF2`)
- Flask et Flask-CORS pour l'API (`pip install flask flask-cors`)

### Utilisation du script CLI

Le script CLI permet d'analyser rapidement un fichier PDF de fiche de poste :

```bash
python job_parser_cli.py /chemin/vers/fiche_de_poste.pdf
```

Options disponibles :
- `--output` ou `-o` : Spécifier un chemin personnalisé pour le fichier de sortie JSON
- `--verbose` ou `-v` : Activer le mode verbeux pour plus d'informations de débogage

### Lancement de l'API

L'API REST permet d'exposer le service de parsing via une interface HTTP :

```bash
cd templates
python job-parser-api.py
```

Par défaut, l'API écoute sur le port 5055. Vous pouvez vérifier qu'elle fonctionne en accédant à http://localhost:5055/

### Intégration avec le questionnaire client

Le formulaire de questionnaire client est déjà configuré pour utiliser l'API de parsing. Il suffit de :

1. Démarrer l'API (`python templates/job-parser-api.py`)
2. Ouvrir le questionnaire client dans un navigateur (https://bapt252.github.io/Commitment-/templates/client-questionnaire.html)

## Fonctionnalités

### Informations extraites

Le système peut extraire les informations suivantes d'une fiche de poste :

- Titre du poste
- Entreprise
- Localisation
- Type de contrat
- Compétences requises
- Expérience demandée
- Formation/Éducation requise
- Salaire 
- Description/Responsabilités
- Avantages proposés

### Mode fallback

Le système dispose d'un mode "fallback" qui permet de continuer à fonctionner même lorsque l'API n'est pas disponible. Dans ce cas, l'analyse est effectuée côté client, directement dans le navigateur, avec des résultats légèrement moins précis.

## Personnalisation

### Ajustement des patterns d'extraction

Vous pouvez personnaliser les patterns d'extraction (expressions régulières) dans les fichiers suivants :

- `job_parser_cli.py` : Pour le script CLI
- `static/js/job-parser-api.js` : Pour le mode fallback côté client

### Ajout de nouvelles compétences techniques

Pour ajouter de nouvelles compétences techniques à détecter, modifiez les listes `tech_skills` dans `job_parser_cli.py` et `commonSkills` dans `job-parser-api.js`.

## Déploiement

### Déploiement de l'API

Pour un déploiement en production, il est recommandé d'utiliser un serveur WSGI comme Gunicorn ou uWSGI :

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5055 'templates.job-parser-api:app'
```

### Intégration avec Docker

Le système peut être facilement conteneurisé avec Docker. Un exemple de Dockerfile est disponible dans le dossier `simple-job-parser/`.

## Dépannage

### L'API ne démarre pas

- Vérifiez que le port 5055 n'est pas déjà utilisé par une autre application
- Assurez-vous d'avoir installé toutes les dépendances requises

### Problèmes d'extraction de texte des PDFs

- Vérifiez que le PDF contient du texte sélectionnable (et non des images de texte)
- Utilisez l'option `-v` avec le script CLI pour voir le texte brut extrait
- Pour les PDFs scannés, un service OCR externe peut être nécessaire

## Futures améliorations

- Support de l'OCR pour les PDFs scannés
- Intégration d'un modèle de langage plus avancé pour améliorer la précision
- Support multilingue pour les fiches de poste en différentes langues
- Interface d'administration pour suivre les analyses effectuées

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
