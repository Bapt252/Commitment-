# Service de Parsing de CV pour Commitment

Ce service permet d'extraire automatiquement les informations d'un CV en utilisant l'API OpenAI avec le modèle GPT-4o-mini.

## Fonctionnalités

- Extraction de texte depuis des fichiers PDF et DOCX
- Parsing de CV via l'API OpenAI (GPT-4o-mini)
- Mise en cache des résultats avec Redis
- API RESTful avec FastAPI
- Gestion d'erreurs robuste et mécanisme de fallback

## Prérequis

- Python 3.11+
- Redis
- Clé API OpenAI

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
export OPENAI_API_KEY=votre_clé_api
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

## Utilisation

### Démarrer le serveur

```bash
# Démarrer le serveur de développement
uvicorn app.main:app --reload

# Pour la production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Construire l'image
docker build -t commitment/cv-parser .

# Exécuter le conteneur
docker run -p 8000:8000 -e OPENAI_API_KEY=votre_clé_api commitment/cv-parser
```

## API Endpoints

### `POST /api/parse-cv/`

Parse un CV et extrait les informations structurées.

**Paramètres**:
- `file`: Fichier CV (PDF ou DOCX)
- `force_refresh`: Forcer le rafraîchissement du cache (défaut: False)

**Réponse**:
```json
{
  "nom": "Dupont",
  "prenom": "Jean",
  "poste": "Développeur Full Stack",
  "competences": ["Python", "JavaScript", "FastAPI"],
  "logiciels": ["Docker", "Git", "VS Code"],
  "soft_skills": ["Travail en équipe", "Communication"],
  "email": "jean.dupont@example.com",
  "telephone": "0123456789",
  "adresse": "123 Rue de la Paix, 75000 Paris"
}
```

## Architecture

- `app/main.py`: Point d'entrée FastAPI
- `services/cv_parser.py`: Logique principale de parsing
- `app/models/cv_model.py`: Modèle de données Pydantic

## Améliorations apportées

- Implémentation de mécanismes de retry avec tenacity pour les appels API
- Extraction de fallback en cas d'échec de l'API OpenAI
- Meilleure gestion d'erreurs avec hiérarchie d'exceptions personnalisées
- Migration vers FastAPI pour de meilleures performances et documentation
- Optimisation du prompt pour des résultats plus précis
- Système de logging amélioré

## Tests

```bash
# Exécuter les tests unitaires
pytest services/tests/
```
