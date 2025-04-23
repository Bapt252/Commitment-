# Commitment

Plateforme de recrutement avec analyse de CV assistée par IA

## Fonctionnalités

- Parsing de CV automatisé avec GPT-4o-mini
- Interface utilisateur intuitive pour le téléchargement de CV
- Système de chat avec l'IA pour obtenir des conseils sur le CV
- Extraction automatique des informations clés : nom, poste actuel, compétences, etc.

## Architecture

Le projet est divisé en deux parties principales :

1. **Frontend** : Interface utilisateur HTML/CSS/JS située dans le dossier `templates/`
2. **Backend** : API Flask qui gère le parsing des CV avec GPT dans le dossier `backend/`

## Configuration

### Prérequis

- Python 3.8 ou supérieur
- Node.js et npm (optionnel, pour le développement frontend)
- Clé API OpenAI (gpt-4o-mini)

### Installation du Backend

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Bapt252/Commitment-.git
   cd Commitment-/backend
   ```

2. Créez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez votre clé API OpenAI :
   ```bash
   cp .env.example .env
   ```
   Puis modifiez le fichier `.env` pour y ajouter votre clé API OpenAI.

### Lancement du Backend

```bash
flask run
```

Le serveur sera disponible sur `http://localhost:5000`.

## Configuration pour le déploiement

Pour déployer l'application en production, suivez ces étapes :

1. Configurez vos variables d'environnement sur votre serveur :
   ```
   OPENAI=votre_clé_api_openai
   FLASK_ENV=production
   ```

2. Lancez l'application avec Gunicorn :
   ```bash
   cd backend
   gunicorn app:app
   ```

## Utilisation du Frontend

Le frontend est accessible directement via GitHub Pages à l'adresse :
https://bapt252.github.io/Commitment-/templates/candidate-upload.html

En développement local, vous pouvez utiliser le serveur Flask qui sert les fichiers statiques, ou simplement ouvrir les fichiers HTML dans votre navigateur.

## Intégration Frontend-Backend

Pour que le frontend se connecte correctement au backend :

1. En développement local, le frontend est configuré pour se connecter à `http://localhost:5000`
2. Pour un déploiement en production, modifiez la variable `API_BASE_URL` dans le fichier `templates/candidate-upload.html` pour pointer vers l'URL de votre backend déployé.

## Sécurité

- La clé API OpenAI est stockée en tant que variable d'environnement "OPENAI"
- CORS est configuré sur le backend pour permettre les requêtes depuis n'importe quelle origine (à ajuster en production)
- Les fichiers téléchargés sont traités de manière sécurisée et supprimés après analyse

## Développement

### Structure des fichiers backend

- `app.py` : Point d'entrée de l'application Flask
- `parsing_service.py` : Service pour l'extraction de texte et l'interaction avec l'API OpenAI
- `requirements.txt` : Dépendances Python
- `.env` : Variables d'environnement (ne pas committer)

## Licence

MIT
