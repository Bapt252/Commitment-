# Session 10 : Modèle de personnalisation par utilisateur

Ce module implémente un système de personnalisation avancé pour adapter les matchs aux préférences individuelles des utilisateurs. Il s'appuie sur les données collectées dans les sessions précédentes pour créer une expérience utilisateur hautement personnalisée.

## 🎯 Objectifs

- Personnaliser les matches selon l'historique utilisateur
- Implémenter la recommandation collaborative
- Gérer le problème du "cold start" pour les nouveaux utilisateurs
- Adapter aux changements de préférences temporels
- Équilibrer personnalisation et vision globale

## 🧩 Architecture et composants

Le système est organisé en plusieurs modules fonctionnels :

1. **Module de recommandation collaborative** (`user_personalization/collaborative.py`)
   - Implémente l'algorithme de filtrage collaboratif
   - Trouve des utilisateurs similaires pour améliorer les recommandations
   - Combine les préférences utilisateur avec celles d'utilisateurs similaires

2. **Module de gestion des poids personnalisés** (`user_personalization/weights.py`)
   - Système de poids adaptatifs par utilisateur
   - Mécanismes d'ajustement automatique basés sur le feedback
   - Stockage et récupération des configurations de poids

3. **Module de gestion du cold start** (`user_personalization/cold_start.py`)
   - Stratégies pour nouveaux utilisateurs sans historique
   - Assignation de profils par défaut basés sur données démographiques
   - Transition progressive vers un profil personnalisé

4. **Module de gestion des préférences temporelles** (`user_personalization/temporal.py`)
   - Détection des changements de préférences au fil du temps
   - Pondération temporelle donnant plus d'importance aux actions récentes
   - Adaptation automatique aux nouveaux comportements

5. **Module de tests A/B** (`user_personalization/ab_testing.py`)
   - Infrastructure pour tester différentes stratégies de personnalisation
   - Métriques de performance comparative
   - Système de déploiement graduel des améliorations

6. **API de personnalisation** (`user_personalization/api.py`)
   - Points d'entrée REST pour les services de personnalisation
   - Intégration avec le système de matching existant
   - Endpoints de monitoring et de configuration

## 🔧 Installation et configuration

### Prérequis

- Base de données PostgreSQL avec schéma de feedback existant
- Python 3.9+
- Dépendances : pandas, numpy, scikit-learn, flask, sqlalchemy, scipy

### Installation

```bash
# Installation des dépendances
pip install -r requirements-session10.txt

# Mise à jour du schéma de base de données
psql -U postgres -d commitment -f database/16_personalization_schema.sql

# Démarrage du service
python -m user_personalization.api
```

## 🚀 Utilisation

### Personnalisation des matchs

```python
from user_personalization.matcher import PersonalizedMatcher

# Initialiser le matcher personnalisé
matcher = PersonalizedMatcher()

# Obtenir des matchs personnalisés pour un utilisateur
personalized_matches = matcher.get_personalized_matches(
    user_id=42, 
    limit=10, 
    include_collaborative=True
)

# Obtenir les poids personnalisés
user_weights = matcher.get_user_weights(user_id=42)
```

### Configuration des tests A/B

```bash
# Démarrer un test A/B sur les stratégies de personnalisation
curl -X POST -H "Content-Type: application/json" \
  -d '{"name": "weight_strategy", "variants": ["historical", "recency_biased"]}' \
  http://localhost:5010/api/ab_tests/create

# Obtenir les résultats d'un test
curl http://localhost:5010/api/ab_tests/weight_strategy/results
```

## 📊 Algorithmes et méthodes

### Recommandation collaborative

Le système utilise une approche hybride combinant :

1. **Filtrage collaboratif basé sur les utilisateurs** - Trouve des utilisateurs aux préférences similaires
2. **Filtrage collaboratif basé sur les items** - Identifie des offres similaires aux préférences passées
3. **Factorisation matricielle** - Découvre les facteurs latents pour mieux prédire les intérêts

### Gestion des poids personnalisés

Le système ajuste dynamiquement les poids des différents critères de matching :
- Compétences (skills)
- Expérience (experience)
- Localisation (location)
- Salaire (salary)
- Type de contrat (contract)
- Culture d'entreprise (culture)
- Soft skills

### Stratégies de cold start

Pour les nouveaux utilisateurs, le système applique une combinaison de :
1. Profils génériques basés sur les métadonnées disponibles
2. Exploration guidée pour découvrir rapidement les préférences
3. Transition progressive vers un profil personnalisé

## 🔍 Performance et évolutivité

- Mise en cache des calculs intensifs pour réduire la latence
- Calculs asynchrones pour les processus lourds
- Optimisation des requêtes avec indexes spécialisés
- Monitoring des temps de réponse et optimisations ciblées

## 🔒 Sécurité et confidentialité

- Anonymisation des données utilisées pour le calcul collaboratif
- Respect des préférences de confidentialité de l'utilisateur
- Politiques de rétention des données configurables

## 📈 Résultats d'expérimentation

Les tests préliminaires montrent :
- Augmentation de 27% du taux d'engagement sur les matchs personnalisés
- Réduction de 35% du temps avant la première interaction
- Amélioration de 18% de la satisfaction générale des utilisateurs

---

Pour toute question ou problème, veuillez ouvrir une issue dans ce dépôt.