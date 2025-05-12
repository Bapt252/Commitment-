# Intégration du parsing GPT pour fiches de poste

Ce guide explique comment utiliser le système de parsing de fiches de poste via GPT dans le frontend de l'application Commitment.

## Introduction

Le système de parsing GPT permet d'analyser automatiquement les fiches de poste pour en extraire les informations clés telles que le titre du poste, l'entreprise, le lieu, le type de contrat, les compétences requises, etc. Cette fonctionnalité est maintenant intégrée dans la page `client-questionnaire.html`.

## Configuration requise

1. Le backend avec le service de parsing GPT doit être en fonctionnement
2. Les scripts JavaScript suivants doivent être inclus dans votre page HTML :
   - `pdf-cleaner.js` - Utilitaire pour nettoyer les fichiers PDF
   - `job-parser-api.js` - API pour communiquer avec le service de parsing
   - `gpt-analyze.js` - Script principal pour l'analyse GPT
   - `debug-gpt.js` - Utilitaires de débogage (optionnel)

## Comment ça marche

### 1. Initialisation automatique

Le script `gpt-analyze.js` s'initialise automatiquement lorsque la page est chargée. Il ajoute un bouton "Analyser avec GPT" sous le champ de texte de la fiche de poste.

### 2. Analyse d'une fiche de poste

Il existe deux façons d'analyser une fiche de poste :

#### A. Téléverser un fichier PDF, DOC, DOCX ou TXT
1. Glissez-déposez un fichier dans la zone prévue ou cliquez pour le sélectionner
2. Le fichier sera automatiquement analysé lors du téléversement, ou vous pouvez cliquer sur le bouton "Analyser avec GPT" pour forcer l'analyse

#### B. Coller le texte de la fiche de poste
1. Collez le texte dans le champ de texte prévu à cet effet
2. Cliquez sur le bouton "Analyser avec GPT" pour lancer l'analyse

### 3. Résultats de l'analyse

Les résultats de l'analyse seront affichés dans la section "Informations extraites" avec les champs suivants :
- Titre du poste
- Type de contrat
- Lieu
- Expérience requise
- Formation
- Rémunération
- Compétences requises
- Responsabilités / Missions
- Avantages

## Configuration avancée

### Paramètres URL

Vous pouvez configurer le comportement du parsing GPT en utilisant les paramètres URL suivants :

- `debug=true` - Active le mode de débogage
- `apiUrl=http://votre-api.com` - Spécifie l'URL de l'API de parsing (par défaut : http://localhost:5055)
- `logLevel=debug|info|error` - Définit le niveau de log en mode débogage

Exemple :
```
https://bapt252.github.io/Commitment-/templates/client-questionnaire.html?debug=true&apiUrl=http://api.example.com&logLevel=debug
```

### Configuration programmatique

Vous pouvez également configurer le comportement du parsing GPT dans votre script :

```javascript
// Configuration manuelle
GPT_ANALYZE_CONFIG.apiUrl = 'http://votre-api.com/api/parse-job';
GPT_ANALYZE_CONFIG.debug = true;
GPT_ANALYZE_CONFIG.useLocalFallback = true;

// Initialisation manuelle
document.addEventListener('DOMContentLoaded', function() {
    initializeGptAnalyzeButton();
});
```

## Fonctionnalités de débogage

Pour activer le mode de débogage, ajoutez `?debug=true` à l'URL de la page. Cela affichera une section de débogage en haut de la page avec des informations sur les requêtes et les réponses de l'API.

Vous pouvez également utiliser l'objet `gptDebug` dans la console JavaScript :

```javascript
// Activer le débogage
gptDebug.enable();

// Journaliser un message
gptDebug.log('Mon message de débogage');

// Journaliser une erreur
gptDebug.log('Une erreur s\'est produite', 'error');

// Effacer les messages de débogage
gptDebug.clear();
```

## Analyse locale (fallback)

Si l'API de parsing n'est pas disponible, le système utilisera automatiquement une analyse locale basée sur des expressions régulières. Cette analyse est moins précise mais fonctionne sans connexion à l'API.

## Personnalisation

Vous pouvez personnaliser l'apparence du bouton "Analyser avec GPT" en modifiant le CSS :

```css
#analyze-with-gpt {
    /* Personnalisation du bouton */
    background-color: #7C3AED;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    font-weight: 600;
}

#gpt-analyze-status {
    /* Personnalisation du statut */
    color: #555;
    font-style: italic;
}
```

## Annexe : Structure du dossier

```
scripts/
  ├── gpt-analyze.js    # Script principal pour l'analyse GPT
  └── debug-gpt.js      # Utilitaires de débogage
js/
  ├── job-parser-api.js # API pour communiquer avec le service de parsing
  └── pdf-cleaner.js    # Utilitaire pour nettoyer les fichiers PDF
```

## Troubleshooting

### L'analyse ne fonctionne pas

1. Vérifiez que le service de parsing GPT est en cours d'exécution et accessible
2. Vérifiez la console JavaScript pour les éventuelles erreurs
3. Activez le mode de débogage en ajoutant `?debug=true` à l'URL
4. Vérifiez que tous les scripts nécessaires sont bien chargés

### Problèmes de CORS

Si vous rencontrez des erreurs CORS, assurez-vous que le service de parsing GPT autorise les requêtes depuis votre domaine.

