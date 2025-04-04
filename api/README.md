# Commitment API

API backend pour le projet Commitment, permettant l'analyse de fiches de poste et de CV.

## Fonctionnalités

- Analyse de fiches de poste à partir de texte brut
- Analyse de fiches de poste à partir de fichiers (PDF, DOCX, TXT)
- Extraction d'informations structurées:
  - Titre du poste
  - Expérience requise
  - Compétences techniques
  - Formation et diplômes
  - Type de contrat
  - Localisation
  - Rémunération

## Prérequis

- Python 3.8+
- pip (gestionnaire de paquets Python)

## Installation

1. Clonez ce dépôt:
```bash
git clone <url-du-repo>
cd commitment-api
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
   - Sous Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. Installez les dépendances:
```bash
pip install -r requirements.txt
```

5. Téléchargez le modèle spaCy (en option, pour améliorer l'analyse):
```bash
python -m spacy download fr_core_news_md
```

## Lancement de l'API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

L'API sera disponible à l'adresse: http://localhost:8000

La documentation interactive sera disponible à: http://localhost:8000/docs

## Endpoints API

### 1. Analyse de texte de fiche de poste

- **URL**: `/api/v1/jobs/parse`
- **Méthode**: POST
- **Corps de la requête**:
  ```json
  {
    "text": "Texte de la fiche de poste..."
  }
  ```
- **Réponse**: JSON avec les informations extraites et scores de confiance

### 2. Analyse de fichier de fiche de poste

- **URL**: `/api/v1/jobs/parse-file`
- **Méthode**: POST
- **Corps de la requête**: Formulaire multipart avec un champ `file`
- **Réponse**: JSON avec les informations extraites et scores de confiance

## Intégration avec le frontend

Le frontend existant est déjà configuré pour appeler cette API sur `http://localhost:8000`. Si vous déployez l'API sur un autre serveur, vous devrez mettre à jour la variable `API_BASE_URL` dans le fichier `static/scripts/document-parser.js`.

## Déploiement en production

Pour un déploiement en production, considérez:

1. Utiliser un serveur WSGI comme Gunicorn
2. Configurer un proxy inverse avec Nginx
3. Limiter les origines CORS autorisées
4. Ajouter une authentification à l'API
5. Mettre en place HTTPS

Exemple de commande pour lancer en production:
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```