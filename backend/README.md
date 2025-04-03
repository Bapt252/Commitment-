# Commitment - Backend API

Cette partie du projet implémente l'API backend pour la solution de recrutement Commitment.

## Technologies utilisées

- Python 3.9+
- FastAPI - Framework API haute performance
- SQLAlchemy - ORM pour la gestion de la base de données
- Alembic - Gestion des migrations de base de données
- Pydantic - Validation des données
- JWT - Authentification des utilisateurs

## Installation

1. Cloner le dépôt

```bash
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-/backend
```

2. Créer et activer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

3. Installer les dépendances

```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer le fichier .env avec vos propres valeurs
```

5. Initialiser la base de données

```bash
python -m app.db.init_db
```

## Lancement du serveur de développement

```bash
python run.py
```

L'API sera accessible à l'adresse http://localhost:8000

La documentation interactive de l'API sera disponible à http://localhost:8000/docs

## Fonctionnalités principales

- Authentification des utilisateurs (JWT)
- Gestion des offres d'emploi
- Analyse automatique des fiches de poste
- Extraction des compétences requises
- Matching candidats / offres

## Structure du projet

- `app/` - Code source principal
  - `api/` - Routes et endpoints
  - `core/` - Configuration et fonctionnalités de base
  - `db/` - Gestion de la base de données
  - `models/` - Modèles SQLAlchemy
  - `schemas/` - Schémas Pydantic
  - `services/` - Services métier
- `tests/` - Tests unitaires et d'intégration