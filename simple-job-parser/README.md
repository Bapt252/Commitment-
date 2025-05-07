# Service d'analyse de fiches de poste pour Commitment-

Ce service backend permet d'analyser des fichiers PDF de fiches de poste et d'en extraire automatiquement les informations clés.

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez le dépôt ou accédez au dossier simple-job-parser:
```bash
cd simple-job-parser
```

2. Créez un environnement virtuel:
```bash
python -m venv venv
```

3. Activez l'environnement virtuel:
   - Sous Windows:
   ```bash
   venv\Scripts\activate
   ```
   - Sous macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

## Démarrage du service

1. Démarrez le serveur Flask:
```bash
python app.py
```

2. Le service sera accessible à l'adresse `http://localhost:5053`

## Test du service

Pour tester le service, vous pouvez:

1. Ouvrir le fichier `test-api.html` dans votre navigateur
2. Utiliser curl:
```bash
curl -X POST -F "file=@/chemin/vers/votre/fiche_poste.pdf" http://localhost:5053/api/parse-job
```

## Intégration avec le frontend existant

Pour intégrer ce service avec le frontend existant:

1. Assurez-vous que le service fonctionne sur le port 5053
2. Remplacez le code JavaScript actuel par la version dans `frontend-debug.js`
3. Désactivez le mode simulation en définissant `SIMULATION_MODE = false`

## Dépannage

Si vous rencontrez des problèmes:

1. Vérifiez les logs du serveur Flask pour les erreurs
2. Assurez-vous que CORS est correctement configuré
3. Utilisez la version avec débogage pour voir les messages détaillés
4. Testez l'API directement avec `test-api.html` avant d'intégrer au frontend

## Personnalisation

Vous pouvez modifier les expressions régulières dans `app.py` ou utiliser l'extracteur personnalisé dans `custom_extractor.py` pour adapter l'extraction à vos besoins spécifiques.

Pour utiliser l'extracteur personnalisé, modifiez la fonction `parse_job()` dans `app.py` pour appeler `extract_job_info_custom` au lieu de `extract_job_info`.
