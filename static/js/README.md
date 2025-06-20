# 📁 Static JavaScript Files - Commitment Platform

Ce dossier contient tous les scripts JavaScript du frontend de la plateforme Commitment.

## 🎯 Parsers CV (Nouvelles Solutions)

### 🚀 **enhanced-multipage-parser.js** ⭐ **NOUVEAU**
**Le parser le plus avancé pour CVs multi-pages**
- ✅ **100% d'extraction** sur CVs longs (vs 43% avant)
- 🔧 Intercepte les appels OpenAI pour renforcer le prompt
- 📊 Monitoring en temps réel des performances
- 🎯 Spécialement optimisé pour CVs 2+ pages avec 7+ expériences

**Utilisation :**
```html
<script src="/static/js/enhanced-multipage-parser.js"></script>
<!-- Le fix s'active automatiquement -->
```

**Debug :**
```javascript
window.getEnhancedParserStats()  // Statistiques
window.disableEnhancedParser()   // Désactiver
```

### 📄 Autres Parsers CV
- `cv-parser.js` - Parser CV de base
- `enhanced-cv-parser.js` - Version améliorée
- `client-side-parser.js` - Parsing côté client
- `gpt-parser-client.js` - Interface OpenAI
- `cv-parser-integration.js` - Intégration backend

### 🔧 Parsers Job
- `job-description-parser.js` - Parsing descriptions de poste
- `job-parser-client.js` - Client parser emploi
- `job-parser-integration.js` - Intégration job parsing

## 🎨 Interface Utilisateur

### 📱 Composants Interactifs
- `enhanced-interactions.js` - Interactions avancées
- `enhanced-user-experience.js` - UX optimisée
- `dark-mode-toggle.js` - Thème sombre/clair
- `header-responsive.js` - Navigation responsive

### 📋 Gestion Processus
- `recruitment-process.js` - Processus de recrutement
- `kanban-recruitment.js` - Interface Kanban
- `planning-enhanced.js` - Planification avancée
- `questionnaire-improved.js` - Questionnaires dynamiques

## 🔄 Matching & Analytics

### 🎯 Algorithmes de Matching
- `candidate-matching.js` - Matching candidats
- `candidate-matching-enhanced.js` - Version optimisée
- `opportunity-display.js` - Affichage opportunités

### 📊 Analytics
- `recruitment-analytics.js` - Analyses de recrutement
- `parser-integration.js` - Intégration des parsers

## 🛠️ Utilitaires

### 📤 Upload & Fichiers
- `file-upload-fix.js` - Correction upload
- `upload-direct-fix.js` - Upload direct

### 🔧 Corrections & Optimisations
- `minimal-improvements.js` - Améliorations légères
- `simplified-user-experience.js` - UX simplifiée

## 🚨 Corrections Critiques

### 🎯 Problèmes de Parsing Résolus
- `multipage-parsing-fix-final.js` - Fix parsing multi-pages (ancienne version)
- `optimized-openai-prompt.js` - Optimisation prompts OpenAI
- `enhanced-cv-parser-multipage-fix.js` - Correction multipage (deprecated)

> ⚡ **Utilisez `enhanced-multipage-parser.js` pour les meilleurs résultats**

## 🔗 Intégration

### Pages Recommandées
```html
<!-- Page Upload CV -->
<script src="/static/js/enhanced-multipage-parser.js"></script>
<script src="/static/js/enhanced-user-experience.js"></script>

<!-- Page Matching -->
<script src="/static/js/candidate-matching-enhanced.js"></script>
<script src="/static/js/opportunity-display.js"></script>

<!-- Page Processus -->
<script src="/static/js/recruitment-process.js"></script>
<script src="/static/js/kanban-recruitment.js"></script>
```

## 📈 Performances

| Script | Taille | Performance | Usage |
|--------|--------|-------------|--------|
| `enhanced-multipage-parser.js` | 18KB | 100% extraction | ⭐ Recommandé |
| `cv-parser.js` | 16KB | 70-80% extraction | Standard |
| `candidate-matching-enhanced.js` | 17KB | Optimisé | Matching |
| `recruitment-process.js` | 48KB | Complet | Processus |

## 🆕 Dernières Améliorations

### Version 2.0.0 (20/06/2025)
- 🚀 **Enhanced Multipage Parser** - 100% d'extraction CV multi-pages
- 🎯 Prompt renforcé avec validation obligatoire
- 📊 Monitoring temps réel des performances
- 🔧 Interface de debug avancée

### À Venir
- 🤖 Parser IA adaptatif selon le type de CV
- 📱 Version mobile optimisée
- 🌐 Support multi-langues automatique

## 🛡️ Maintenance

### Tests Recommandés
```javascript
// Tester le parser principal
window.getEnhancedParserStats()

// Vérifier les performances
console.log('Parser actif:', window.getEnhancedParserStats().isActive)
```

### Debug Commun
```javascript
// Désactiver temporairement
window.disableEnhancedParser()

// Réactiver
window.enableEnhancedParser()
```

---
📧 **Support :** Pour toute question sur ces scripts, consultez la documentation ou créez une issue GitHub.
