# SmartMatcher - Architecture Modulaire Refactorisée

## Vue d'ensemble

Cette version refactorisée du SmartMatcher suit les principes de Clean Architecture pour offrir :

- **Séparation claire des responsabilités** 
- **Extensibilité** via le système de plugins
- **Testabilité** avec injection de dépendances
- **Performance** avec cache intelligent
- **Maintainabilité** avec code modulaire

## Structure du projet

```
smartematch-refactored/
├── domain/                    # Couche domaine métier
├── application/               # Couche application (use cases)
├── infrastructure/            # Couche infrastructure 
├── adapters/                  # Adaptateurs (controllers)
└── shared/                    # Code partagé
```

## Architecture

L'architecture suit le pattern Clean Architecture avec :

1. **Domain Layer** : Entités métier et logique de domaine pure
2. **Application Layer** : Use cases et orchestration
3. **Infrastructure Layer** : Services externes et persistance
4. **Adapters Layer** : Controllers et interfaces externes

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```python
from smartmatch_refactored import MatchingServiceFactory

# Créer le service de matching
config = MatchingConfig.from_environment()
matching_service = MatchingServiceFactory.create(config)

# Effectuer un matching
result = matching_service.match_candidate_to_job(candidate, job)
print(f"Score: {result.overall_score}")
```

## Migration depuis l'ancien système

Voir [MIGRATION.md](./MIGRATION.md) pour les détails de migration.
