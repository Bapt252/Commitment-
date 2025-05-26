#!/bin/bash

# Script pour mettre à jour le README principal avec SuperSmartMatch
# Auteur: Nexten Team

echo "📝 Mise à jour du README principal avec SuperSmartMatch"
echo "======================================================"

# Backup du README existant
echo "💾 Sauvegarde du README existant..."
cp README.md README.md.backup.$(date +%Y%m%d_%H%M%S)

# Création de la section SuperSmartMatch
cat >> README_SUPERSMARTMATCH_SECTION.md << 'EOF'

## 🧠 **NOUVEAU : SuperSmartMatch - Service Unifié de Matching**

**SuperSmartMatch** est notre nouvelle innovation qui révolutionne l'architecture de matching en regroupant TOUS nos algorithmes sous une seule API intelligente.

### 🎯 **Pourquoi SuperSmartMatch ?**

#### ❌ **AVANT** : Architecture complexe
- 5 services de matching séparés (ports 5051, 5052, 5055, 5057, 5060)
- Logique de sélection d'algorithme dans le front-end
- Maintenance complexe et points de défaillance multiples

#### ✅ **APRÈS** : Architecture unifiée
- **1 seul service intelligent** (port 5070)
- **Sélection automatique** du meilleur algorithme selon le contexte
- **Fallback automatique** en cas d'erreur
- **Cache intelligent** pour des performances optimales

### 🚀 **Démarrage Express SuperSmartMatch**

```bash
# Nouveau script avec SuperSmartMatch intégré
chmod +x start-all-services-supersmartmatch.sh
./start-all-services-supersmartmatch.sh

# ✅ SuperSmartMatch disponible sur http://localhost:5070
```

### 🌐 **Accès aux services avec SuperSmartMatch**

Après avoir lancé les conteneurs avec SuperSmartMatch :

- **🧠 SuperSmartMatch API** : http://localhost:5070
- **📖 Documentation API unifiée** : http://localhost:5070/docs
- **🔍 Health Check** : http://localhost:5070/health
- **🎯 Algorithmes disponibles** : http://localhost:5070/algorithms
- **📊 Statistiques** : http://localhost:5070/api/v1/stats
- **🌐 Frontend** : http://localhost:3000 (inchangé)
- **🗄️ MinIO Console** : http://localhost:9001 (inchangé)

### 🔥 **Utilisation simplifiée**

#### **Ancien code** (multiples services) :
```javascript
// Avant - Appels multiples
const matchingAPI = 'http://localhost:5052/api/match';
const jobAnalyzerAPI = 'http://localhost:5055/analyze';
const personalizationAPI = 'http://localhost:5060/api/v1/personalize';

// Gestion manuelle des algorithmes...
```

#### **Nouveau code** (SuperSmartMatch) :
```javascript
// Après - Un seul appel unifié !
const response = await fetch('http://localhost:5070/api/v1/match', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    candidate: {
      competences: ["Python", "Django", "SQL"],
      annees_experience: 3,
      adresse: "Paris",
      contrats_recherches: ["CDI"],
      salaire_souhaite: 45000
    },
    jobs: jobsArray,
    algorithm: "auto",  // 🧠 Sélection automatique !
    limit: 20
  })
});

const result = await response.json();
console.log('🎯 Algorithme utilisé:', result.algorithm_used);
console.log('📊 Scores:', result.matches);
```

### 🧠 **Intelligence Automatique**

SuperSmartMatch sélectionne automatiquement le meilleur algorithme :

| Contexte | Algorithme | Raison |
|----------|------------|--------|
| 👨‍💻 Candidat junior | `smart-match` | Optimal pour profils débutants |
| 👨‍💼 Candidat senior + tech | `enhanced` | Matching sémantique avancé |
| 📊 Volume > 1000 offres | `original` | Performance maximale |
| 🌐 Candidat remote | `smart-match` | Géolocalisation intelligente |
| 🎯 Précision maximale | `hybrid` | Combine plusieurs algorithmes |

### ⚡ **Performances**

- **Cache intelligent** : Résultats mis en cache 5 minutes
- **Fallback automatique** : Basculement transparent en cas d'erreur
- **Métriques en temps réel** : Monitoring des performances
- **Optimisation contextuelle** : Le bon algorithme au bon moment

### 🔧 **Configuration**

```bash
# Variables d'environnement disponibles
export SUPER_SMART_MATCH_ENABLED=true      # Activer SuperSmartMatch
export SKIP_LEGACY_SERVICES=true           # Ignorer anciens services
export START_MONITORING=true               # Prometheus + Grafana

# Relancer avec la nouvelle configuration
./start-all-services-supersmartmatch.sh
```

### 🧪 **Tests**

```bash
# Tests automatiques complets
cd super-smart-match-service
./test-supersmartmatch.sh

# Test rapide
curl http://localhost:5070/health
```

### 📊 **Monitoring avancé**

Si monitoring activé (`START_MONITORING=true`) :
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000 (admin/nexten123)

### 🎉 **Bénéfices immédiats**

✅ **Simplicité** : 1 endpoint au lieu de 5  
✅ **Performance** : Sélection automatique optimale  
✅ **Robustesse** : Fallback automatique  
✅ **Maintenance** : Complexité réduite de 80%  
✅ **Évolutivité** : Ajout facile de nouveaux algorithmes  
✅ **Observabilité** : Métriques unifiées  

### 🔄 **Migration**

1. **Phase 1** : Démarrer SuperSmartMatch en parallèle
2. **Phase 2** : Tester sur une page front-end
3. **Phase 3** : Migration graduelle
4. **Phase 4** : Décommission des anciens services

---

**🧠 SuperSmartMatch : Votre matching devient intelligent !**

EOF

echo "📝 Section SuperSmartMatch créée"
echo "💡 Vous pouvez maintenant l'intégrer manuellement dans votre README.md"
echo "📁 Fichier généré : README_SUPERSMARTMATCH_SECTION.md"
echo ""
echo "🔧 Pour intégration automatique, lancez :"
echo "   cat README_SUPERSMARTMATCH_SECTION.md >> README.md"
echo ""
echo "✅ Mise à jour terminée !"
