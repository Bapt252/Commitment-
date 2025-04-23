# Nexten (Commitment)

Plateforme de recrutement avec analyse de CV assistée par IA et matching intelligent, basée sur une architecture microservices.

## Architecture microservices

Le projet est organisé selon une architecture microservices pour permettre une meilleure scalabilité et une maintenance simplifiée:

1. **Gateway API** : Point d'entrée centralisé pour toutes les requêtes
2. **User Service** : Gestion des utilisateurs et authentification
3. **CV Parser Service** : Parsing automatisé des CV avec IA
4. **Profile Service** : Gestion des profils candidats
5. **Matching Service** : Algorithmes de matching intelligent
6. **Job Service** : Gestion des offres d'emploi
7. **Notification Service** : Gestion des emails et alertes
8. **Frontend** : Interface utilisateur en Next.js

## Structure du projet

```
nexten/
├── gateway/                  # Service de passerelle API
├── user-service/             # Gestion des utilisateurs
├── cv-parser-service/        # Service de parsing de CV
├── profile-service/          # Gestion des profils
├── matching-service/         # Algorithmes de matching
├── job-service/              # Gestion des offres d'emploi
├── notification-service/     # Notifications et emails
├── frontend/                 # Application Next.js
└── docker-compose.yml        # Configuration des services
```

## Fonctionnalités

- Parsing de CV automatisé avec GPT-4o-mini
- Interface utilisateur intuitive basée sur Next.js
- Matching intelligent entre profils et offres d'emploi
- Architecture scalable pour supporter la croissance
- API RESTful pour tous les services

## Technologies

- **Backend** : Flask pour les services, RabbitMQ pour la communication asynchrone
- **Frontend** : Next.js
- **Bases de données** : MongoDB pour les profils et PostgreSQL pour les données relationnelles
- **Déploiement** : Docker, Docker Compose (dev), Kubernetes (prod)

## Configuration

### Prérequis

- Python 3.8 ou supérieur
- Node.js et npm
- Docker et Docker Compose
- Clé API OpenAI

### Installation en développement

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Bapt252/Commitment-.git
   cd Commitment-
   ```

2. Lancez les services avec Docker Compose :
   ```bash
   docker-compose up
   ```

Le serveur de développement sera disponible sur `http://localhost:3000` pour le frontend et `http://localhost:8000` pour l'API gateway.

## Utilisation des microservices

Chaque service expose sa propre API RESTful, mais toutes les communications doivent passer par la Gateway API pour assurer l'authentification et le routage appropriés.

## Développement

### Structure type d'un microservice

```
service-name/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── service_logic.py
│   ├── models/
│   └── utils/
├── config.py
├── Dockerfile
└── requirements.txt
```

## Licence

MIT