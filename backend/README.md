# Backend de parsing de CV pour Commitment

Ce backend fournit une API permettant d'analyser les CV et d'extraire des informations pertinentes pour le projet Commitment.

## Fonctionnalités

- Extraction d'informations à partir de CV (PDF, DOCX, TXT)
- API RESTful pour l'intégration avec le frontend
- Support du chat basé sur les données du CV
- Déploiement facile sur Heroku

## Endpoints API

- `/api/parsing-chat/upload` : Pour télécharger et analyser les CV
- `/api/parsing-chat/chat` : Pour discuter avec le CV via l'IA
- `/api/health` : Endpoint de vérification de santé

## Configuration locale

Suivez ces étapes pour configurer et tester le backend en local:

### 1. Créez un environnement virtuel Python

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur macOS/Linux:
source venv/bin/activate
```

### 2. Installez les dépendances

```bash
pip install -r requirements.txt
```

### 3. Téléchargez le modèle spaCy français

```bash
python -m spacy download fr_core_news_md
```

### 4. Lancez le serveur en local

```bash
flask run
```

Le serveur devrait démarrer à l'adresse http://127.0.0.1:5000/

## Déploiement sur Heroku

### 1. Créez un compte Heroku

Si ce n'est pas déjà fait, créez un compte sur [Heroku](https://signup.heroku.com/).

### 2. Installez l'interface de ligne de commande Heroku (CLI)

Téléchargez et installez la [CLI Heroku](https://devcenter.heroku.com/articles/heroku-cli).

### 3. Connectez-vous à Heroku

```bash
heroku login
```

### 4. Créez une application Heroku

```bash
# Créer une application Heroku
heroku create cv-parser-commitment
```

### 5. Ajoutez un buildpack pour spaCy

```bash
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-apt
```

### 6. Déployez sur Heroku

```bash
git push heroku main
```

## Configuration du frontend

Une fois le backend déployé, vous devez mettre à jour votre frontend pour utiliser la nouvelle API:

1. Ouvrez le fichier `candidate-upload.html`
2. Trouvez la variable `API_BASE_URL` dans le script JavaScript
3. Remplacez sa valeur par l'URL de votre application Heroku:
   ```javascript
   const API_BASE_URL = 'https://cv-parser-commitment.herokuapp.com';
   ```

## Support

Si vous avez besoin d'aide, n'hésitez pas à ouvrir une issue ou à contacter l'équipe de développement.
