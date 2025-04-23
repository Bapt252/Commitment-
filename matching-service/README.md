# Service de Matching pour Nexten

Ce microservice gère le matching entre les candidats et les offres d'emploi en utilisant l'algorithme modulaire implémenté dans PostgreSQL.

## Fonctionnalités

- Calcul de scores de matching entre candidats et emplois
- Gestion des algorithmes de matching (configuration, pondérations)
- Génération de recommandations personnalisées
- Explicabilité des scores (détails des critères de matching)

## Architecture

```
matching-service/
├── app/                 # Module principal
│   ├── __init__.py      # Initialisation de l'application Flask
│   ├── api/             # Endpoints API REST
│   │   ├── __init__.py
│   │   └── routes.py    # Routes API
│   ├── core/            # Logique métier
│   │   ├── __init__.py
│   │   └── matching.py  # Fonctions de matching
│   ├── models/          # Modèles de données
│   │   ├── __init__.py
│   │   └── match.py     # Modèle de matching
│   └── utils/           # Utilitaires
│       ├── __init__.py
│       └── db.py        # Connexion base de données
├── config.py            # Configuration de l'application
├── Dockerfile           # Instructions de construction du conteneur
└── requirements.txt     # Dépendances Python
```

## Endpoints API

- `GET /api/matches/job/{job_id}` - Obtenir les meilleurs candidats pour un job
- `GET /api/matches/candidate/{candidate_id}` - Obtenir les meilleurs jobs pour un candidat
- `POST /api/matches/calculate` - Calculer un score de matching spécifique
- `GET /api/matches/{match_id}` - Obtenir les détails d'un match
- `PUT /api/matches/{match_id}/status` - Mettre à jour le statut d'un match
- `GET /api/algorithms` - Lister les algorithmes disponibles
- `POST /api/algorithms` - Créer un nouvel algorithme
- `GET /api/algorithms/{algorithm_id}` - Obtenir les détails d'un algorithme
- `PUT /api/algorithms/{algorithm_id}` - Mettre à jour un algorithme

## Utilisation

### Installation

```bash
pip install -r requirements.txt
```

### Variables d'environnement

- `POSTGRES_USER` - Nom d'utilisateur PostgreSQL
- `POSTGRES_PASSWORD` - Mot de passe PostgreSQL
- `POSTGRES_HOST` - Hôte PostgreSQL
- `POSTGRES_PORT` - Port PostgreSQL (défaut: 5432)
- `POSTGRES_DB` - Nom de la base de données
- `JWT_SECRET_KEY` - Clé secrète pour JWT
- `API_PREFIX` - Préfixe pour les routes API (défaut: /api)

### Lancement

```bash
python -m app.run
```

### Docker

```bash
docker build -t nexten-matching-service .
docker run -p 5003:5000 --name matching-service nexten-matching-service
```

## Interaction avec les autres services

Le service de matching interagit principalement avec :
- Service de profils (pour les données des candidats)
- Service d'emploi (pour les données des offres)
- Service d'analyse (pour les statistiques de matching)