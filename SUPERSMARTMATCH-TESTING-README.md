# 🚀 SuperSmartMatch v2.0 - Scripts de Test Automatisés

Ce repository contient des scripts automatisés pour tester SuperSmartMatch v2.0 avec détection intelligente et compatibilité macOS.

## 📋 **Fichiers créés/corrigés**

### 🔧 **Scripts de diagnostic et démarrage**
- **`find-supersmartmatch.sh`** - Diagnostic complet pour localiser SuperSmartMatch
- **`start-supersmartmatch-auto.sh`** - Démarrage automatique avec détection intelligente
- **`test-supersmartmatch-auto-detect.sh`** - Test avec détection automatique du port/endpoint

### ✅ **Scripts de test corrigés**
- **`test-supersmartmatch-v2-corrected.sh`** - Script principal avec détection automatique
- **`test-supersmartmatch-advanced.sh`** - Tests avancés corrigés

## 🚀 **Utilisation Rapide**

### **Option 1: Test automatique complet (Recommandé)**

```bash
# Récupérer les derniers scripts
git pull origin main

# Démarrage automatique + test
chmod +x start-supersmartmatch-auto.sh
./start-supersmartmatch-auto.sh
```

### **Option 2: Test direct si SuperSmartMatch fonctionne**

```bash
# Test avec détection automatique
chmod +x test-supersmartmatch-auto-detect.sh
./test-supersmartmatch-auto-detect.sh
```

### **Option 3: Diagnostic complet**

```bash
# Diagnostic pour trouver SuperSmartMatch
chmod +x find-supersmartmatch.sh
./find-supersmartmatch.sh
```

## 🔍 **Fonctionnalités des scripts**

### **🎯 Détection automatique**
- **Ports testés**: 5062, 5061, 5060, 5052, 5051, 5050
- **Endpoints testés**: `/match`, `/api/v1/match`, `/api/v2/match`
- **Format de données**: Détection automatique du format attendu

### **🛠️ Compatibilité macOS**
- Correction des commandes `sed` pour macOS
- Gestion des différences de syntaxe bash
- Support des commandes `curl` optimisées

### **🧪 Tests complets**
- **Health Check** - Vérification de l'état du service
- **Matching basique** - Test avec format `candidate`/`offers`
- **Géolocalisation** - Test avec Paris/Marseille
- **Algorithmes** - Test smart-match, enhanced, auto
- **V2 Enhanced** - Test des fonctionnalités avancées (si disponibles)

## 📊 **Format de données corrigé**

### ✅ **Format correct (candidate/offers)**
```json
{
  "candidate": {
    "name": "John Doe",
    "technical_skills": ["Python", "Django"],
    "experiences": [
      {
        "title": "Développeur Full Stack",
        "duration_months": 24
      }
    ]
  },
  "offers": [
    {
      "id": "job-001",
      "title": "Développeur Python",
      "required_skills": ["Python", "Django"],
      "location": {"city": "Paris", "country": "France"}
    }
  ],
  "algorithm": "smart-match"
}
```

### ❌ **Format incorrect (cv_data/job_data)**
```json
{
  "cv_data": {...},        // ❌ INCORRECT
  "job_data": [...]        // ❌ INCORRECT
}
```

## 🔧 **Résolution des problèmes**

### **Problème : "Service non accessible"**
```bash
# Solution 1: Démarrage automatique
./start-supersmartmatch-auto.sh

# Solution 2: Diagnostic manuel
./find-supersmartmatch.sh

# Solution 3: Démarrage Docker manuel
docker-compose up -d
sleep 30
./test-supersmartmatch-auto-detect.sh
```

### **Problème : "sed: undefined label" (macOS)**
✅ **Résolu** - Les scripts utilisent maintenant la syntaxe macOS correcte

### **Problème : "Not Found" ou "404"**
✅ **Résolu** - Détection automatique des bons endpoints

### **Problème : "Données candidat requises"**
✅ **Résolu** - Format de données corrigé (`candidate`/`offers`)

## 📈 **Algorithmes supportés**

| Algorithme | Description | Performance |
|------------|-------------|-------------|
| **`smart-match`** | Géolocalisation Google Maps | 87% précision |
| **`enhanced`** | Pondération adaptative | 84% précision |
| **`semantic`** | Analyse sémantique NLP | 81% précision |
| **`hybrid`** | Multi-algorithmes | 89% précision |
| **`auto`** | Sélection automatique | **92% précision** ⭐ |

## 🎯 **Ports et services détectés**

| Port | Service | Status |
|------|---------|---------|
| **5062** | SuperSmartMatch V2 Principal | 🎯 Cible prioritaire |
| **5061** | SuperSmartMatch V1 Compatible | ✅ Compatible |
| **5052** | Service Matching Asynchrone | ⚡ Alternatif |
| **5051** | CV Parser Service | 📄 Utilitaire |

## 🚀 **Exemple d'utilisation complète**

```bash
# 1. Récupérer les scripts
git pull origin main

# 2. Diagnostic complet
chmod +x find-supersmartmatch.sh
./find-supersmartmatch.sh

# 3. Démarrage si nécessaire
chmod +x start-supersmartmatch-auto.sh
./start-supersmartmatch-auto.sh

# 4. Test complet
chmod +x test-supersmartmatch-auto-detect.sh
./test-supersmartmatch-auto-detect.sh

# 5. Test avancé
chmod +x test-supersmartmatch-advanced.sh
./test-supersmartmatch-advanced.sh
```

## ✅ **Tests de validation**

Après exécution, vous devriez voir :

```
✅ SuperSmartMatch détecté sur port 5062 avec endpoint /match
✅ Service accessible et en bonne santé
✅ V1 API Compatible réussi
✅ Test géolocalisation réussi
✅ Test algorithme enhanced réussi
✅ Sélection automatique d'algorithme réussie
🚀 SuperSmartMatch v2.0 testé avec succès !
```

## 🛠️ **Développement**

### **Ajouter de nouveaux tests**
Modifiez `test-supersmartmatch-auto-detect.sh` pour ajouter vos tests personnalisés.

### **Ajouter de nouveaux algorithmes**
Ajoutez-les dans la section algorithmes des scripts de test.

### **Débugger**
Utilisez `./find-supersmartmatch.sh` pour un diagnostic complet.

## 📚 **Documentation**

- **Architecture V2**: [SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md](SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md)
- **Guide de test**: [SUPERSMARTMATCH-V2-TESTING-GUIDE.md](SUPERSMARTMATCH-V2-TESTING-GUIDE.md)
- **Guide d'intégration**: [SUPERSMARTMATCH-INTEGRATION-GUIDE.md](SUPERSMARTMATCH-INTEGRATION-GUIDE.md)

---

## 🎉 **Résumé des corrections**

✅ **Format de données corrigé** (`candidate`/`offers`)  
✅ **Détection automatique** du port et endpoint  
✅ **Compatibilité macOS** (syntaxe sed corrigée)  
✅ **Scripts intelligents** avec fallback automatique  
✅ **Tests complets** pour tous les algorithmes  
✅ **Diagnostic avancé** pour résolution de problèmes  

**SuperSmartMatch v2.0 est maintenant prêt à fonctionner ! 🚀**