# 🔧 CV Parser V2 - Résolution Port 5051

## 🚨 Problème Identifié

**Symptôme**: CV Parser V2 inaccessible sur port 5051 avec erreur "Connection reset by peer"

**Impact**: 
- ❌ CV Parser V2 (port 5051): Non fonctionnel
- ✅ Job Parser V2 (port 5053): Opérationnel  
- ✅ Enhanced API V2.1 (port 5055): Opérationnel

**Situation**: Le système Enhanced V2.1 fonctionne parfaitement (cas Hugo Salvat validé), mais impossible de tester avec des fichiers réels à cause du CV Parser.

---

## ⚡ Solution Rapide (1 commande)

```bash
# Résolution automatique complète + tests
chmod +x fix_and_test_complete.sh && ./fix_and_test_complete.sh
```

---

## 🛠️ Solutions Étape par Étape

### 1. 🔍 Diagnostic
```bash
./diagnose_cv_parser_v2.sh
```
Analyse complète du problème et propose des solutions.

### 2. 🔧 Réparation
```bash
./fix_cv_parser_v2.sh
```
Répare spécifiquement le CV Parser V2 sur port 5051.

### 3. 🧪 Tests Complets
```bash
./test_system_complete.sh
```
Valide que tout le système fonctionne correctement.

---

## 📋 Scripts Disponibles

| Script | Description | Usage |
|--------|-------------|-------|
| `setup_scripts.sh` | Configure les permissions | `./setup_scripts.sh` |
| `diagnose_cv_parser_v2.sh` | Diagnostic complet | `./diagnose_cv_parser_v2.sh` |
| `fix_cv_parser_v2.sh` | Réparation CV Parser | `./fix_cv_parser_v2.sh` |
| `test_system_complete.sh` | Tests de validation | `./test_system_complete.sh` |
| `fix_and_test_complete.sh` | **Solution tout-en-un** | `./fix_and_test_complete.sh` |

---

## 🎯 Tests Post-Réparation

### Test Hugo Salvat (Validation V2.1)
```bash
curl http://localhost:5055/api/test/hugo-salvat
```
**Attendu**: Score < 30% avec alertes d'incompatibilité

### Test Services
```bash
# CV Parser V2
curl http://localhost:5051/health

# Job Parser V2  
curl http://localhost:5053/health

# Enhanced API V2.1
curl http://localhost:5055/health
```

### Test Fichiers Réels
```bash
# Avec BATU Sam.pdf et IT.pdf
python test_matching_system.py --cv "~/Desktop/BATU Sam.pdf" --job "~/Desktop/IT .pdf"
```

---

## 🔍 Diagnostic Manuel

### Vérifier les Conteneurs Docker
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(5051|5053|5055)"
```

### Logs des Conteneurs
```bash
# Identifier le conteneur CV Parser
docker ps | grep cv-parser

# Voir les logs
docker logs [CONTAINER_NAME]
```

### Processus sur les Ports
```bash
netstat -tlnp | grep -E "(5051|5053|5055)"
```

---

## 🔧 Solutions Manuelles

### Solution 1: Restart Docker
```bash
docker restart $(docker ps -q --filter 'publish=5051')
```

### Solution 2: Rebuild Complet
```bash
cd cv-parser-v2
docker build -t cv-parser-v2-fixed . --no-cache
docker run -d -p 5051:5051 --name cv-parser-v2-new cv-parser-v2-fixed
```

### Solution 3: Démarrage Python Direct (Debug)
```bash
cd cv-parser-v2
pip install -r requirements.txt
python app.py
```

---

## 📁 Fichiers Critiques

Le CV Parser V2 nécessite ces fichiers pour fonctionner :

```
cv-parser-v2/
├── app.py                                    # Application principale
├── Dockerfile                               # Configuration Docker
├── requirements.txt                         # Dépendances Python
└── parsers/
    ├── fix-pdf-extraction.js               # Extraction PDF
    └── enhanced-mission-parser.js          # Parsing missions
```

---

## ⚠️ Problèmes Fréquents

### Erreur: "Connection reset by peer"
**Cause**: Conteneur Docker crashé ou mal configuré  
**Solution**: `./fix_cv_parser_v2.sh`

### Erreur: "Fichiers JavaScript manquants"
**Cause**: Parsers JavaScript non copiés dans le conteneur  
**Solution**: Rebuild avec `docker build --no-cache`

### Erreur: "Port 5051 déjà utilisé"
**Cause**: Ancien processus/conteneur bloque le port  
**Solution**: `docker kill $(docker ps -q --filter 'publish=5051')`

---

## 🎉 Validation Succès

Après résolution, vous devriez avoir :

- ✅ `curl http://localhost:5051/health` → Réponse JSON
- ✅ `curl http://localhost:5055/api/test/hugo-salvat` → Score < 30%
- ✅ Tests fichiers BATU Sam.pdf vs IT.pdf fonctionnels
- ✅ Système V2.1 Enhanced pleinement opérationnel

---

## 🚀 Prochaines Étapes

1. **Tests en lot** :
   ```bash
   python test_matching_system.py --cvs-folder ~/Desktop/CV\ TEST/ --jobs-folder ~/Desktop/FDP\ TEST/
   ```

2. **Documentation des résultats** :
   - Comparaison scores V2 vs V2.1
   - Validation amélioration faux positifs
   - Tests sur différents profils métiers

3. **Déploiement production** :
   - Migration vers Enhanced API V2.1
   - Formation utilisateurs
   - Monitoring performances

---

## 📞 Support

En cas de problème persistant :

1. **Logs détaillés** : `./diagnose_cv_parser_v2.sh > debug.log`
2. **Reset complet** : `./fix_and_test_complete.sh`
3. **Consultation logs** : `docker logs [container_name]`

---

*SuperSmartMatch V2.1 Enhanced - CV Parser V2 Resolution Guide*
