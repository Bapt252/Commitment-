# ADR-001: Adoption d'une architecture microservices avec Domain-Driven Design

## Statut
**ACCEPTÉ** - Date: 2025-05-27

## Contexte
SuperSmartMatch V1 utilise une architecture monolithique qui présente des limitations critiques :
- Scalabilité limitée (impossible de scaler individuellement les composants)
- Déploiements risqués (tout ou rien)
- Couplage fort entre modules
- Difficultés de maintenance et d'évolution
- Performances dégradées sous charge

## Décision
Nous adoptons une **architecture microservices basée sur Domain-Driven Design** avec les services suivants :

### Services Core Business
1. **Geolocation Service** - Calculs géographiques et temps de trajet
2. **Scoring Engine Service** - Algorithmes de matching et scoring
3. **Parsing Service** - Extraction d'informations CV/jobs avec IA
4. **Behavior Analytics Service** - Analyse comportementale utilisateurs
5. **Explainability Service** - Génération d'explications en langage naturel

### Services Infrastructure
6. **API Gateway** - Point d'entrée unique et routage
7. **Authentication Service** - Gestion identité et autorisation
8. **Notification Service** - Communications email/SMS
9. **File Storage Service** - Gestion documents et médias

## Conséquences

### Avantages ✅
- **Scalabilité granulaire** : Chaque service peut être scalé indépendamment
- **Déploiements indépendants** : Réduction des risques et accélération des releases
- **Résilience** : Failure isolation entre services
- **Technologies diversifiées** : Choix optimal par service
- **Équipes autonomes** : Ownership claire par domaine
- **Performance** : Optimisation ciblée par use case

### Défis ⚠️
- **Complexité opérationnelle** : Monitoring, logging, tracing distribués
- **Cohérence des données** : Gestion des transactions distribuées
- **Latence réseau** : Communications inter-services
- **Testing complexe** : Tests d'intégration end-to-end

### Mitigations 🛡️
- **Service Mesh (Istio)** : Gestion transparente des communications
- **Event Sourcing** : Traçabilité et cohérence événementielle
- **Circuit Breakers** : Protection contre les cascading failures
- **Observability Stack** : Monitoring complet (Prometheus/Grafana/Jaeger)
- **Contract Testing** : Validation des interfaces (Pact)

## Alternatives Considérées

### 1. Monolithe Modulaire
- ❌ Ne résout pas les problèmes de scalabilité
- ❌ Déploiements toujours risqués
- ✅ Simplicité opérationnelle

### 2. Microservices Pure (sans DDD)
- ❌ Risque de services trop granulaires
- ❌ Couplage par la donnée
- ❌ Boundaries mal définies

### 3. Serverless Architecture
- ❌ Vendor lock-in
- ❌ Cold starts impactant la latence
- ❌ Limitations pour les workloads ML
- ✅ Auto-scaling automatique

## Implémentation

### Phase 1: Services Foundation
```yaml
Services à implémenter en priorité:
  1. API Gateway (Kong/Envoy)
  2. Authentication Service (OAuth2/JWT)
  3. Geolocation Service (base pour matching)
  4. Scoring Engine Service (core business)
```

### Phase 2: Services Métier
```yaml
Extension avec services avancés:
  5. Enhanced Parsing Service
  6. Behavior Analytics Service  
  7. Explainability Service
  8. Notification Service
```

### Patterns Architecturaux
- **API Gateway Pattern** : Point d'entrée unifié
- **Database per Service** : Isolation des données
- **Event-Driven Architecture** : Communication asynchrone
- **CQRS** : Séparation lecture/écriture pour performance
- **Saga Pattern** : Gestion transactions distribuées

## Métriques de Succès
- **Déploiement indépendant** : Chaque service déployable séparément
- **Scalabilité** : Scaling horizontal par service selon charge
- **Résilience** : Aucun SPOF, graceful degradation
- **Performance** : Latence <200ms pour 95% des requêtes
- **Disponibilité** : 99.9% uptime par service

## Outils et Technologies

### Orchestration
- **Kubernetes** : Orchestration et scheduling
- **Helm** : Package management
- **Istio** : Service mesh pour observability et sécurité

### Development
- **FastAPI (Python)** : Services haute performance
- **Node.js** : Services I/O intensifs
- **Go** : Services système et performance critique

### Data
- **PostgreSQL** : Database principale avec partitioning
- **Redis Cluster** : Cache distribué
- **Elasticsearch** : Search et analytics
- **MinIO** : Object storage pour documents

### Observability
- **Prometheus** : Métriques
- **Grafana** : Dashboards
- **Jaeger** : Distributed tracing
- **ELK Stack** : Logging centralisé

## Révision
Cette décision sera révisée après 6 mois d'opération en production pour évaluer :
- Performance réelle vs. théorique
- Complexité opérationnelle
- Satisfaction des équipes de développement
- Coûts d'infrastructure

---
**Auteur**: Architecture Team  
**Reviewers**: CTO, Lead Developers, DevOps Team  
**Approbation finale**: CTO - 2025-05-27