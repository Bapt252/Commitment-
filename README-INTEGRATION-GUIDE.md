# Guide d'intégration du JOB PARSER via GPT

Ce document explique comment utiliser le service JOB PARSER via GPT pour extraire automatiquement des informations à partir de fiches de poste dans votre application.

## Présentation du service

Le service JOB PARSER est un microservice qui utilise GPT-4o-mini pour extraire des informations structurées à partir de fiches de poste. Il peut analyser des fichiers PDF, DOCX, DOC, TXT, ainsi que du texte brut, et en extraire des données clés comme le titre du poste, l'entreprise, le lieu, les compétences requises, etc.

## Comment cela fonctionne

1. **Upload de fichier ou saisie de texte** : L'utilisateur peut soit télécharger un fichier de fiche de poste, soit coller directement le texte.
2. **Analyse automatique** : Le service utilise GPT-4o-mini pour extraire les informations clés.
3. **Affichage des résultats** : Les informations extraites sont affichées à l'utilisateur et peuvent être utilisées pour préremplir des formulaires.

## Architecture de l'intégration

L'architecture d'intégration est conçue pour être robuste et flexible :

```
Frontend (HTML/JS) <---> JobParserAPI <---> Backend JOB PARSER (GPT)
                            |                       |
                            v                       v
                     Traitement local          Redis Queue
                      (mode fallback)            MinIO Storage
```

## Comment intégrer le JOB PARSER dans votre application

### 1. Inclure le script JobParserAPI

```html
<script src="../js/job-parser-api.js"></script>
```

### 2. Initialiser l'API

```javascript
// Initialiser l'API JOB PARSER
const jobParserAPI = new JobParserAPI({
    // La configuration est optionnelle, le système détectera automatiquement le serveur
    debug: true // Activer les logs pour le développement
});
```

### 3. Analyser un fichier de fiche de poste

```javascript
// Récupérer le fichier depuis un élément input
const fileInput = document.getElementById('job-file-input');
const file = fileInput.files[0];

if (file) {
    try {
        // Afficher un loader
        showLoader();
        
        // Analyser le fichier
        const result = await jobParserAPI.parseJobFile(file);
        
        // Traiter les résultats
        displayJobResults(result);
    } catch (error) {
        console.error('Erreur lors de l\'analyse du fichier:', error);
        showErrorMessage(error.message);
    } finally {
        // Masquer le loader
        hideLoader();
    }
}
```

### 4. Analyser un texte de fiche de poste

```javascript
// Récupérer le texte depuis un textarea
const jobText = document.getElementById('job-description-text').value;

if (jobText.trim()) {
    try {
        // Afficher un loader
        showLoader();
        
        // Analyser le texte
        const result = await jobParserAPI.parseJobText(jobText);
        
        // Traiter les résultats
        displayJobResults(result);
    } catch (error) {
        console.error('Erreur lors de l\'analyse du texte:', error);
        showErrorMessage(error.message);
    } finally {
        // Masquer le loader
        hideLoader();
    }
}
```

### 5. Afficher les résultats

Voici un exemple de fonction pour afficher les résultats de l'analyse :

```javascript
function displayJobResults(jobData) {
    // Titre du poste
    if (jobData.title) {
        document.getElementById('job-title-value').textContent = jobData.title;
    }
    
    // Entreprise
    if (jobData.company) {
        document.getElementById('company-name').value = jobData.company;
    }
    
    // Lieu
    if (jobData.location) {
        document.getElementById('job-location-value').textContent = jobData.location;
    }
    
    // Type de contrat
    if (jobData.contract_type) {
        document.getElementById('job-contract-value').textContent = jobData.contract_type;
        // Pré-sélectionner le type de contrat dans un select
        setSelectValue('contract-type', jobData.contract_type);
    }
    
    // Compétences requises
    if (jobData.required_skills && jobData.required_skills.length > 0) {
        document.getElementById('job-skills-value').innerHTML = jobData.required_skills.map(skill => 
            `<span class="tag">${skill}</span>`
        ).join('');
    }
    
    // Responsabilités
    if (jobData.responsibilities && jobData.responsibilities.length > 0) {
        document.getElementById('job-responsibilities-value').innerHTML = '<ul>' + 
            jobData.responsibilities.map(resp => `<li>${resp}</li>`).join('') + 
            '</ul>';
    }
    
    // Afficher le conteneur des résultats
    document.getElementById('job-info-container').style.display = 'block';
}
```

## Gestion des erreurs et fallback

Le système est conçu pour être résilient :

1. **Détection automatique du serveur** : L'API détecte automatiquement le serveur backend disponible.
2. **Mode fallback local** : Si le serveur n'est pas disponible, l'API utilise un mode d'analyse locale.
3. **Gestion des timeouts** : Les requêtes sont limitées dans le temps pour éviter les blocages.

## Structure des données extraites

L'API renvoie les informations sous forme d'objet JSON avec la structure suivante :

```javascript
{
    "title": "Développeur FullStack React/Node.js",         // Titre du poste
    "company": "TechInnovation",                           // Nom de l'entreprise
    "location": "Paris, France",                           // Lieu de travail
    "contract_type": "CDI",                                // Type de contrat
    "required_skills": [                                   // Compétences requises
        "JavaScript", 
        "React", 
        "Node.js"
    ],
    "preferred_skills": [                                  // Compétences souhaitées
        "TypeScript", 
        "MongoDB"
    ],
    "responsibilities": [                                  // Missions et responsabilités
        "Développer de nouvelles fonctionnalités",
        "Collaborer avec les équipes produit"
    ],
    "requirements": [                                      // Prérequis
        "Diplôme d'ingénieur ou équivalent",
        "3 ans d'expérience minimum"
    ],
    "benefits": [                                          // Avantages
        "Télétravail partiel",
        "Tickets restaurant"
    ],
    "salary_range": "45K€ - 55K€",                        // Fourchette de salaire
    "remote_policy": "3 jours par semaine"                 // Politique de télétravail
}
```

## Configuration avancée

L'API JobParser accepte les options de configuration suivantes :

```javascript
const jobParserAPI = new JobParserAPI({
    // URL de base de l'API (optionnel, auto-détecté)
    apiBaseUrl: '/api/job-parser',
    
    // URLs de base alternatives pour l'auto-détection
    apiBaseUrls: [
        '/api/job-parser',
        'http://localhost:5053/api/parse-job',
        'http://localhost:7000/api/job-parser'
    ],
    
    // Timeout des requêtes en millisecondes
    requestTimeout: 120000,
    
    // Intervalle de vérification du statut d'un job
    pollInterval: 2000,
    
    // Nombre maximum de tentatives de vérification
    maxPollAttempts: 30,
    
    // Mode debug
    debug: true
});
```

## Événements

L'API émet des événements que vous pouvez écouter pour mieux contrôler l'intégration :

```javascript
// Événement émis quand un serveur d'API est détecté
window.addEventListener('jobParserApiReady', (event) => {
    console.log('API JOB PARSER prête à l\'emploi avec le serveur:', event.detail.url);
});

// Événement émis en cas d'erreur de détection de serveur
window.addEventListener('jobParserApiError', (event) => {
    console.error('Erreur avec l\'API JOB PARSER:', event.detail.error);
});
```

## Exemples d'intégration

Vous pouvez voir un exemple complet d'intégration dans le fichier `templates/client-questionnaire.html`.

## Support et dépannage

### Problèmes courants et solutions

1. **Erreur "No API server detected"** : Vérifiez que le service JOB PARSER est bien lancé et accessible.
2. **Timeout lors de l'analyse** : Vérifiez la connexion au service et augmentez éventuellement la valeur de `requestTimeout`.
3. **Erreur d'extraction de données** : Le document pourrait être dans un format difficile à analyser, essayez de copier-coller le texte directement.

### Activer le mode debug

Pour faciliter le dépannage, activez le mode debug :

```javascript
const jobParserAPI = new JobParserAPI({ debug: true });
```

Vous pouvez également ajouter `?debug=true` à l'URL pour activer automatiquement le mode debug.

## En cas de problème avec GPT

Si le service GPT est indisponible, l'API utilisera automatiquement son mode d'analyse locale. Ce mode est moins précis mais permet de continuer à utiliser l'application en mode dégradé.

---

Pour toute question ou problème, consultez la documentation du service JOB PARSER dans `README-JOB-PARSER-GPT.md` ou contactez l'équipe de développement.