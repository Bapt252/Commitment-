# API Commitment - Phase 5

API RESTful pour intégrer tous les composants ML du projet Commitment. Cette API permet l'upload et l'analyse de fiches de poste, l'analyse des réponses aux questionnaires, la génération de recommandations de matching, et l'enregistrement des feedbacks pour amélioration continue.

## Fonctionnalités

- **Analyse de fiches de poste**: Extraction automatique d'informations clés à partir de fichiers PDF, DOCX ou texte brut
- **Analyse de questionnaires**: Traitement des réponses pour identifier compétences, expériences et préférences
- **Algorithme de matching**: Génération de recommandations de matching basées sur la compatibilité des profils
- **Système de feedback**: Collecte et analyse des feedbacks pour amélioration continue des modèles ML

## Technologies

- [FastAPI](https://fastapi.tiangolo.com/): Framework API hautes performances
- [Pydantic](https://docs.pydantic.dev/): Validation des données et sérialisation
- [SQLAlchemy](https://www.sqlalchemy.org/): ORM pour la persistance des données
- [spaCy](https://spacy.io/): NLP pour l'extraction d'informations et l'analyse de texte
- [scikit-learn](https://scikit-learn.org/): Algorithmes de ML pour le matching et les recommandations
- [pytest](https://docs.pytest.org/): Tests automatisés
- [Swagger/OpenAPI](https://swagger.io/): Documentation interactive de l'API

## Installation

1. Cloner ce dépôt:
```bash
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-/backend
```

2. Créer un environnement virtuel Python:
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances:
```bash
pip install -r requirements.txt
```

4. Créer un fichier `.env` basé sur `.env.example` et configurer les variables d'environnement

## Démarrage

### Mode développement

```bash
uvicorn app.main:app --reload --port 8000
```

### Mode production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Avec Docker

```bash
docker compose up -d
```

## Structure du projet

```
backend/
├── app/                  # Code principal de l'application
│   ├── api/              # Endpoints de l'API
│   │   ├── endpoints/    # Endpoints organisés par fonctionnalité
│   │   └── api.py        # Router principal
│   ├── core/             # Configuration et fonctionnalités de base
│   ├── ml/               # Modèles et composants ML
│   ├── models/           # Modèles Pydantic pour la validation
│   ├── db/               # Modèles SQLAlchemy et opérations CRUD
│   ├── utils/            # Utilitaires divers
│   └── main.py           # Point d'entrée de l'application
├── data/                 # Données pour les modèles ML
├── logs/                 # Fichiers de logs
├── tests/                # Tests automatisés
├── .env.example          # Exemple de configuration
├── requirements.txt      # Dépendances Python
└── run.py                # Script de démarrage
```

## Documentation API

L'API est documentée via Swagger/OpenAPI. Une fois l'API démarrée, accédez à:

- Documentation Swagger: http://localhost:8000/docs
- Documentation ReDoc: http://localhost:8000/redoc

Pour plus de détails sur les endpoints, voir [backend/app/api/README.md](app/api/README.md).

## Tests

Pour exécuter les tests:

```bash
pytest -v
```

## Déploiement

### Docker

Un `Dockerfile` et un fichier `docker-compose.yml` sont fournis pour faciliter le déploiement.

```bash
docker compose up -d
```

### Kubernetes

Des exemples de configurations Kubernetes sont disponibles dans le dossier `k8s/`.

## Intégration avec le frontend

Le frontend peut communiquer avec l'API REST aux endpoints définis. Exemple d'intégration:

```javascript
// Exemple d'appel pour l'analyse d'une fiche de poste
async function parseJobPost(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/v1/job-posts/parse', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
}
```

## Contribuer

1. Créer une branche pour votre fonctionnalité
2. Ajouter vos changements
3. Écrire des tests pour vos changements
4. S'assurer que tous les tests passent
5. Soumettre une Pull Request

## Licence

Voir le fichier LICENSE à la racine du projet.
