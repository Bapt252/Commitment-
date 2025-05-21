# Session 10: Personnalisation par utilisateur

Cette session se concentre sur l'implémentation d'un système de personnalisation des matchs pour chaque utilisateur, en fonction de ses préférences, comportements et interactions passées.

## Objectifs

- Mettre en place un système de personnalisation des recommandations pour chaque utilisateur
- Intégrer plusieurs stratégies de personnalisation (filtrage collaboratif, poids personnalisés, ajustements temporels)
- Gérer efficacement les nouveaux utilisateurs (cold start)
- Permettre des tests A/B pour optimiser les stratégies de recommandation
- Fournir une API RESTful pour accéder aux fonctionnalités de personnalisation

## Composants implémentés

1. **Infrastructure de base de données**
   - Schéma pour stocker les préférences utilisateur
   - Tables pour le suivi des interactions et du feedback
   - Support pour les tests A/B

2. **Modules de personnalisation**
   - `weights.py`: Gestion des poids personnalisés par utilisateur
   - `collaborative.py`: Filtrage collaboratif basé sur les comportements similaires
   - `cold_start.py`: Stratégies pour les nouveaux utilisateurs
   - `temporal.py`: Ajustements basés sur les comportements temporels
   - `ab_testing.py`: Framework pour les tests A/B de différentes stratégies

3. **Système de matching personnalisé**
   - `matcher.py`: Module principal combinant les différentes stratégies
   - Algorithme de scoring et de ranking personnalisé
   - Intégration avec le système de matching existant

4. **API REST**
   - `api.py`: Endpoints pour accéder aux fonctionnalités de personnalisation
   - Gestion du feedback utilisateur
   - Récupération des recommandations personnalisées

5. **Scripts utilitaires**
   - Script d'initialisation de la base de données
   - Script de démarrage du service de personnalisation

6. **Tests**
   - Tests unitaires pour valider l'implémentation
   - Tests d'intégration avec le système existant

## Installation et démarrage

```bash
# Installer les dépendances
pip install -r requirements-session10.txt

# Initialiser la base de données
python scripts/init_personalization_db.py --seed-data

# Démarrer le service de personnalisation
bash scripts/start_personalization_service.sh
```

## API Endpoints

- `GET /api/personalization/matches/{user_id}`: Obtenir des matchs personnalisés pour un utilisateur
- `POST /api/personalization/feedback`: Enregistrer le feedback d'un utilisateur
- `GET /api/personalization/user_weights/{user_id}`: Obtenir les poids personnalisés d'un utilisateur

## Intégration avec le système existant

Le système de personnalisation s'intègre avec le système de matching existant en tant que couche additionnelle. Le système existant fournit les candidats potentiels, et le système de personnalisation les classe selon les préférences de l'utilisateur.
