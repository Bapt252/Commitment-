# NexTen - Application de Parsing CV et Matching Intelligent

NexTen est une application moderne pour l'analyse des CV et le matching intelligent avec des offres d'emploi, conçue avec une architecture microservices.

## Architecture

L'application est conçue avec une architecture microservices légère, qui comprend :

- **Backend principal** (Flask) : API principale qui coordonne les microservices
- **Service de parsing CV** : Service spécialisé dans l'extraction d'informations structurées depuis des CV au format PDF ou DOCX
- **Service de matching** : Service d'intelligence artificielle qui effectue le matching entre les profils de candidats et les offres d'emploi
- **Frontend** (Next.js) : Interface utilisateur moderne et réactive

## Technologies utilisées

- **Backend** : Flask (Python)
- **Frontend** : Next.js (React)
- **Base de données** : PostgreSQL
- **Cache / File d'attente** : Redis
- **Stockage d'objets** : MinIO (pour les CV)
- **Conteneurisation** : Docker + docker-compose

## Structure du projet

```
nexten/
├── backend/                   # API principale Flask
│   ├── app.py                 # Point d'entrée principal
│   ├── parsing_service.py     # Client pour le service de parsing
│   └── app/                   # Modules de l'application
│
├── cv-parser-service/         # Service de parsing des CV
│   ├── app/
│   │   ├── services/
│   │   │   ├── pdf_parser.py   # Parser pour les PDF
│   │   │   └── docx_parser.py  # Parser pour les DOCX
│   │   └── routes.py          # Endpoints API
│
├── matching-service/          # Service de matching intelligent
│   └── app/
│       ├── services/
│       │   └── matcher.py     # Algorithme de matching
│       └── routes.py          # Endpoints API
│
├── frontend/                  # Frontend Next.js
│   ├── src/
│   │   ├── pages/             # Pages Next.js
│   │   │   ├── index.js       # Page d'accueil
│   │   │   ├── cv-upload.js   # Page de téléchargement CV
│   │   │   └── api/           # Endpoints API proxy
│   │   └── components/        # Composants React
│
└── docker-compose.yml         # Configuration Docker
```

## Fonctionnalités principales

1. **Analyse de CV** : Extraction intelligente des informations depuis des CV PDF et DOCX
2. **Matching intelligent** : Algorithme de correspondance entre profils et offres d'emploi
3. **Stockage sécurisé** : Conservation des CV et données structurées
4. **API REST** : API complète pour l'intégration avec d'autres systèmes

## Installation et démarrage

### Prérequis

- Docker et docker-compose
- Git

### Étapes d'installation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Bapt252/Commitment-.git
   cd Commitment-
   ```

2. Créer un fichier `.env` à partir du modèle :
   ```bash
   cp .env.example .env
   ```

3. Démarrer les services avec Docker Compose :
   ```bash
   docker-compose up -d
   ```

4. Accéder à l'application :
   - Frontend : http://localhost:3000
   - API : http://localhost:5050
   - MinIO (stockage) : http://localhost:9001

## Développement

Pour contribuer au développement, consultez le fichier [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
