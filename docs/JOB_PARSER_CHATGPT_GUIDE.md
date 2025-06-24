# 🤖 Guide d'installation Job Parser ChatGPT

## 📋 Vue d'ensemble

Ce guide t'explique comment remplacer ton job parser actuel (basé sur des regex locales) par une solution robuste utilisant l'API ChatGPT pour une analyse intelligente des fiches de poste.

## 🎯 Fonctionnalités

✅ **Analyse intelligente avec ChatGPT** - Extraction précise des 10 champs demandés  
✅ **Support multi-formats** - PDF, DOCX, TXT  
✅ **Interface utilisateur complète** - Configuration API, drag & drop, résultats  
✅ **Compatible avec ton architecture** - S'intègre dans ton HTML existant  
✅ **Stockage sécurisé** - Clé API sauvegardée localement  

## 📁 Fichiers créés

### 1. `js/job-parser-gpt.js`
Le cœur du système ChatGPT avec extraction intelligente

### 2. `scripts/job-parsing-ui-gpt.js`
Interface utilisateur complète avec configuration API

### 3. `docs/JOB_PARSER_CHATGPT_GUIDE.md` (ce fichier)
Guide d'installation et utilisation

## 🔧 Installation

### Étape 1: Vérifier les fichiers

Les nouveaux fichiers sont déjà créés dans cette branche :
- ✅ `js/job-parser-gpt.js`
- ✅ `scripts/job-parsing-ui-gpt.js`

### Étape 2: Modifier le HTML principal

Dans `templates/client-questionnaire.html`, ajoute ces lignes APRÈS tes scripts existants :

```html
<!-- NOUVEAUX SCRIPTS CHATGPT - À ajouter avant </body> -->
<script src="../js/job-parser-gpt.js"></script>
<script src="../scripts/job-parsing-ui-gpt.js"></script>
```

**Position exacte** - Ajoute juste avant la balise `</body>` :

```html
    <!-- Scripts existants... -->
    <script src="../scripts/job-parsing-ui.js"></script>
    <script src="../scripts/debug-gpt.js"></script>
    
    <!-- NOUVEAUX SCRIPTS CHATGPT -->
    <script src="../js/job-parser-gpt.js"></script>
    <script src="../scripts/job-parsing-ui-gpt.js"></script>

    <script>
        // Script existant...
    </script>
</body>
```

### Étape 3: Fusionner la branche

1. **Teste sur ta branche** : `feature/job-parser-chatgpt`
2. **Si tout fonctionne**, fusionne avec `main`
3. **Déploie** sur GitHub Pages

## 🎮 Utilisation

### Configuration initiale

1. **Ouvre ta page** : `https://bapt252.github.io/Commitment-/templates/client-questionnaire.html`
2. **Va à l'étape 3** "Recrutement"
3. **Sélectionne "Oui"** pour le besoin de recrutement
4. **Configure ta clé API** :
   - Tu verras une nouvelle section bleue "Configuration ChatGPT"
   - Saisis ta clé API OpenAI (commence par `sk-`)
   - Clique "Sauvegarder" puis "Tester"

### Test de fonctionnement

1. **Upload un fichier** ou **colle du texte** de fiche de poste
2. **Clique sur le bouton d'analyse** (🔍)
3. **Attends l'analyse ChatGPT** (quelques secondes)
4. **Vérifie les 10 champs extraits** :
   - Titre du poste
   - Type de contrat
   - Localisation
   - Expérience requise
   - Formation demandée
   - Rémunération
   - Compétences (tags)
   - Responsabilités/missions
   - Avantages
   - Nom de l'entreprise

## 🔑 Obtenir une clé API OpenAI

1. Va sur [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Connecte-toi ou crée un compte
3. Clique "Create new secret key"
4. Copie la clé (commence par `sk-`)
5. Ajoute du crédit sur ton compte OpenAI (minimum 5$)

## 💰 Coûts estimés

- **Modèle utilisé** : `gpt-4o-mini` (le plus économique)
- **Coût par analyse** : ~0.01-0.02€
- **100 analyses** : ~1-2€
- **Usage mensuel moyen** : 5-10€

## 🚀 Migration depuis l'ancien système

### Différences principales :

| Ancien système | Nouveau système ChatGPT |
|---|---|
| Regex locales limitées | IA intelligente |
| Extraction partielle | 10 champs complets |
| Résultats approximatifs | Analyse précise |
| `generateMockResults()` | Vraie extraction |
| Pas de configuration | Interface clé API |

### Remplacement automatique :

Le nouveau système remplace automatiquement :
- `window.jobParsingUI` → `window.jobParsingUIGPT`
- `JobParserAPI` → `JobParserGPT`
- Analyse locale → Analyse ChatGPT

## 🐛 Dépannage

### Problèmes courants :

**❌ "Clé API non configurée"**
- Vérifie que ta clé commence par `sk-`
- Teste la connexion avec le bouton "Tester"

**❌ "Erreur API OpenAI (401)"**
- Clé API invalide ou expirée
- Vérifie ton crédit OpenAI

**❌ "PDF.js non disponible"**
- Assure-toi que le script PDF.js est chargé avant

**❌ Interface de config n'apparaît pas**
- Vérifie que les scripts sont dans le bon ordre
- Regarde la console pour les erreurs

### Debug :

```javascript
// Dans la console du navigateur
console.log('Parser GPT:', window.jobParserGPTInstance);
console.log('UI GPT:', window.jobParsingUIGPT);

// Test rapide
window.jobParserGPTInstance.testConnection();
```

## 📊 Monitoring

### Vérifier que ça marche :

1. **Console du navigateur** : Messages de confirmation
2. **Section API** : Statut vert "Connexion ChatGPT réussie"
3. **Résultats** : Badge "Analyse réalisée par ChatGPT"

### Logs utiles :

```
✅ Job Parser ChatGPT UI initialisé
🤖 JobParserGPT chargé et prêt !
✅ Clé API sauvegardée avec succès
✅ Connexion ChatGPT réussie !
```

## 🎨 Personnalisation

### Modifier le prompt ChatGPT :

Dans `job-parser-gpt.js`, modifie la méthode `getJobAnalysisPrompt()` pour adapter l'extraction à tes besoins spécifiques.

### Changer le modèle :

```javascript
// Dans le constructeur JobParserGPT
this.gptModel = 'gpt-4'; // Plus précis mais plus cher
// ou
this.gptModel = 'gpt-3.5-turbo'; // Plus économique
```

### Ajuster les champs extraits :

Modifie le JSON de réponse dans `getJobAnalysisPrompt()` pour ajouter/supprimer des champs.

## 📞 Support

Si tu rencontres des problèmes :

1. **Vérifie la console** du navigateur pour les erreurs
2. **Teste ta clé API** avec le bouton de test
3. **Assure-toi** que PDF.js est chargé
4. **Vérifie l'ordre** des scripts dans ton HTML

## 🏆 Résultat attendu

Après installation, tu auras :

✅ Une interface de configuration API élégante  
✅ Une analyse ChatGPT qui remplace les regex  
✅ Une extraction précise des 10 champs demandés  
✅ Un système robuste et professionnel  
✅ Ton questionnaire Nexten transformé en vrai outil de recrutement  

## 📝 Exemple d'utilisation

### Texte de test :

```
Intitulé du poste : Développeur Full Stack
Entreprise : TechInnovation SAS
Localisation : Lyon
Type de contrat : CDI
Expérience : 3-5 ans en développement web
Formation : Master en informatique ou équivalent
Compétences : React, Node.js, TypeScript, MongoDB
Missions : Développement d'applications web modernes, participation à l'architecture technique
Salaire : 45-55k€ selon profil
Avantages : Télétravail partiel, formation continue, mutuelle
```

### Résultat attendu :

- ✅ **Titre** : "Développeur Full Stack"
- ✅ **Entreprise** : "TechInnovation SAS"
- ✅ **Lieu** : "Lyon"
- ✅ **Contrat** : "CDI"
- ✅ **Expérience** : "3-5 ans en développement web"
- ✅ **Formation** : "Master en informatique ou équivalent"
- ✅ **Salaire** : "45-55k€ selon profil"
- ✅ **Compétences** : ["React", "Node.js", "TypeScript", "MongoDB"]
- ✅ **Missions** : "Développement d'applications web modernes, participation à l'architecture technique"
- ✅ **Avantages** : "Télétravail partiel, formation continue, mutuelle"

**Bravo ! Ton job parser sera enfin fonctionnel ! 🎉**