# Commitment

Commitment est une plateforme de matching entre candidats et offres d'emploi.

## Fonctionnalités principales

- Analyse des offres d'emploi pour extraction automatique des compétences et exigences
- Questionnaires personnalisés pour les candidats
- Algorithme de matching intelligent
- Interface utilisateur intuitive pour explorer les matchings

## Architecture technique

- Backend: FastAPI (Python)
- Frontend: HTML/CSS/JavaScript 
- Base de données: PostgreSQL
- Machine Learning: scikit-learn, TensorFlow

## Structure du projet

```
├── backend/            # API FastAPI
├── ml_engine/          # Modèles de machine learning
├── airflow_dags/       # DAGs Airflow pour les traitements planifiés
└── docs/               # Documentation
```

## Système d'amélioration continue

Le projet intègre désormais un système complet d'amélioration continue basé sur les feedbacks utilisateurs qui permet:

1. **Collecte de feedback**:
   - Feedback explicite sur les matchings (ratings, commentaires)
   - Mesures implicites (taux d'interaction post-matching)

2. **Analyse et entraînement**:
   - Réentraînement périodique des modèles 
   - Validation croisée et métriques de qualité
   - Déploiement automatisé des modèles améliorés

3. **Monitoring**:
   - Alertes en cas de détérioration des performances
   - Tableaux de bord de suivi des métriques
   - Détection proactive des problèmes

Consultez la [documentation du système de feedback](./docs/feedback_system.md) pour plus de détails.

## Installation et configuration

### Prérequis

- Python 3.9+
- PostgreSQL
- Node.js/npm (pour certaines parties frontend)

### Installation

1. Clonez le repository
   ```
   git clone https://github.com/Bapt252/Commitment-.git
   cd Commitment-
   ```

2. Installez les dépendances du backend
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Configurez la base de données
   ```
   # Créez un fichier .env basé sur .env.example
   # Puis exécutez les migrations
   alembic upgrade head
   ```

4. Lancez l'API
   ```
   python run.py
   ```

## Contribuer au projet

Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails sur notre code de conduite et le processus de soumission des pull requests.

## Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.
