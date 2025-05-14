# Service d'Analyse de Fiches de Poste avec GPT

Ce service permet d'analyser automatiquement des fiches de poste en utilisant GPT et d'extraire les informations clés comme le titre, les compétences requises, le salaire, etc.

## Points d'entrée

### 1. Page simplifiée d'analyse de fiches de poste
URL: https://bapt252.github.io/Commitment-/templates/job-analyzer.html

Cette page est optimisée pour l'analyse de fiches de poste avec:
- Un bouton d'analyse GPT bien visible
- Une interface simplifiée centrée sur l'analyse
- Connexion automatique à l'API sans besoin de paramètres

### 2. Questionnaire client complet
URL: https://bapt252.github.io/Commitment-/templates/client-questionnaire.html

Cette page intègre l'analyse de fiches de poste dans un workflow complet:
- Étape d'analyse comme première étape du questionnaire
- Données analysées utilisées pour pré-remplir les étapes suivantes

## Fonctionnalités

- **Analyse de fichiers PDF, DOCX et TXT** - Déposez ou téléchargez un fichier de fiche de poste
- **Analyse de texte** - Collez le texte de votre fiche de poste directement
- **Extraction automatique** des informations clés:
  - Titre du poste
  - Type de contrat
  - Lieu
  - Expérience requise
  - Formation
  - Rémunération
  - Compétences requises
  - Responsabilités/Missions
  - Avantages

## Configuration de l'API

Le service se connecte automatiquement à l'API par détection intelligente. L'ordre de priorité est:
1. URL spécifiée via le paramètre `apiUrl` dans l'URL (ex: `?apiUrl=http://localhost:5055`)
2. Serveur local à http://localhost:5055
3. Serveur de production à https://api.commitment-analyzer.com
4. Serveur de secours à https://gpt-parser-api.onrender.com

## Mode Debug

Pour activer le mode debug et voir des informations supplémentaires, ajoutez `?debug=true` à l'URL.

## Architecture Technique

### Composants Frontend

- **job-analyzer.html** - Page simplifiée d'analyse de fiches de poste
- **client-questionnaire.html** - Questionnaire client complet
- **gpt-autoloader.js** - Module de chargement automatique de l'API GPT
- **job-parser-api.js** - API client pour le service de parsing
- **pdf-cleaner.js** - Utilitaires de nettoyage des textes extraits des PDF

### Fonctionnement du Chargeur Automatique GPT

Le module `gpt-autoloader.js` assure une expérience utilisateur fluide:
1. Détection automatique de l'API disponible
2. Ajout de boutons d'analyse GPT bien visibles dans l'interface
3. Gestion intelligente des erreurs et fallback local si l'API n'est pas disponible
4. Retour visuel sur l'état de la connexion à l'API

## Développement

### Serveur API Local

Pour lancer un serveur API local pour le développement:
```bash
cd api
pip install -r requirements.txt
python app.py
```

Le serveur sera disponible à http://localhost:5055.

### Options d'URL

- `?apiUrl=http://localhost:5055` - Spécifie l'URL de l'API
- `?debug=true` - Active le mode debug

### Exemples de requêtes

1. Page d'analyse simple avec debug:
```
https://bapt252.github.io/Commitment-/templates/job-analyzer.html?debug=true
```

2. Questionnaire avec API personnalisée:
```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?apiUrl=http://localhost:5055
```

## Dépannage

Si le service d'analyse ne fonctionne pas:

1. Vérifiez que l'API est accessible en ouvrant `http://localhost:5055/api/health` dans votre navigateur
2. Activez le mode debug avec `?debug=true` pour voir les messages de détail
3. Vérifiez la console du navigateur (F12) pour les éventuelles erreurs
4. Si l'API n'est pas disponible, le service utilisera automatiquement une analyse locale moins précise
