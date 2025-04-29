# Documentation - Pré-remplissage automatique du formulaire candidat

## Vue d'ensemble

Cette documentation explique le fonctionnement du système de pré-remplissage automatique du formulaire candidat implémenté dans le projet Commitment. Ce système permet de remplir automatiquement les champs du formulaire avec les informations extraites du CV du candidat via le backend.

## Fichiers concernés

1. **`static/scripts/form-prefiller.js`** : Script principal qui gère le pré-remplissage
2. **`static/scripts/parsed-data-example.js`** : Exemple de données parsées pour tester le pré-remplissage
3. **`templates/candidate-questionnaire.html`** : Page HTML du formulaire candidat

## Structure des données parsées

Les données parsées doivent respecter la structure suivante pour être correctement interprétées par le système de pré-remplissage :

```javascript
{
  // Informations personnelles (étape 1)
  personalInfo: {
    fullName: String,       // Nom et prénom du candidat
    jobTitle: String        // Intitulé de poste souhaité
  },
  
  // Mobilité et préférences (étape 2)
  mobility: {
    transportMethods: Array<String>,  // Liste des moyens de transport ["public-transport", "vehicle", "bike", "walking"]
    commuteTimes: {                   // Temps de trajet pour chaque moyen de transport (en minutes)
      "public-transport": String,     // Exemple: "45" (minutes)
      "vehicle": String,
      "bike": String,
      "walking": String
    },
    address: String,                  // Adresse complète
    officePreference: String          // Préférence de bureau ["open-space", "office", "no-preference"]
  },
  
  // Motivations et secteurs (étape 3)
  motivations: {
    order: Array<String>,          // Ordre des motivations ["remuneration", "evolution", "flexibility", "location", "other"]
    otherMotivation: String,       // Description si "other" est dans les 3 premiers
    structureTypes: Array<String>, // Types de structure ["startup", "pme", "group", "no-preference"]
    hasSectorPreference: Boolean,  // A une préférence de secteur
    preferredSectors: Array<String>, // Secteurs préférés (codes)
    hasProhibitedSectors: Boolean,   // A des secteurs rédhibitoires
    prohibitedSectors: Array<String>, // Secteurs à éviter (codes)
    salaryRange: String               // Fourchette de rémunération (format texte)
  },
  
  // Disponibilité et situation actuelle (étape 4)
  availability: {
    timeframe: String,             // Disponibilité ["immediate", "1month", "2months", "3months"]
    currentlyEmployed: Boolean,    // Actuellement en poste
    listeningReason: String,       // Raison d'être à l'écoute (si employé)
    noticePeriod: String,          // Durée du préavis (si employé)
    noticeNegotiable: Boolean|null, // Préavis négociable (si employé) - null pour "Je ne sais pas"
    contractEndReason: String,     // Raison fin de contrat (si non employé)
    recruitmentStatus: String      // État du processus de recrutement
  }
}
```

## Fonctionnement du script `form-prefiller.js`

Le script `form-prefiller.js` définit un objet global `FormPrefiller` avec les méthodes suivantes :

### `initialize(data)`

Cette méthode initialise le système de pré-remplissage avec les données fournies :
- Vérifie que les données sont valides
- Stocke les données dans une variable interne
- Appelle la méthode `fillForm()` quand le DOM est prêt

### `fillForm()`

Cette méthode remplit automatiquement tous les champs du formulaire avec les données disponibles :
- Remplit les informations personnelles (étape 1)
- Remplit les informations de mobilité et préférences (étape 2)
- Remplit les motivations et secteurs (étape 3)
- Remplit la disponibilité et situation actuelle (étape 4)
- Affiche une notification pour informer l'utilisateur

Le script utilise plusieurs fonctions utilitaires pour manipuler les éléments du formulaire :
- `setInputValue()` : Définit la valeur d'un champ de texte
- `setRadioValue()` : Définit la valeur d'un bouton radio
- `setCheckboxValue()` : Coche ou décoche une case à cocher
- `setSelectValue()` : Définit la valeur d'un menu déroulant
- `setMultiSelectValues()` : Sélectionne plusieurs valeurs dans une liste déroulante multiple
- `reorderMotivations()` : Réorganise les éléments de motivation selon l'ordre spécifié
- `triggerTransportMethodsChange()` : Déclenche l'événement change sur les checkbox de moyens de transport

## Méthodes pour transmettre les données au frontend

### 1. Via sessionStorage

```javascript
// Dans votre backend, générez un script qui stocke les données dans sessionStorage
const parsedData = {...}; // Données parsées
sessionStorage.setItem('parsedCandidateData', JSON.stringify(parsedData));
```

### 2. Via un identifiant dans l'URL

```
https://bapt252.github.io/Commitment-/templates/candidate-questionnaire.html?parsed_data_id=12345
```

Le script détectera automatiquement l'identifiant dans l'URL et fera une requête API pour récupérer les données correspondantes.

## Intégration dans le backend

Pour intégrer cette fonctionnalité dans votre backend, vous devez :

1. Récupérer les données du CV via le système de parsing existant
2. Transformer ces données au format attendu (voir structure ci-dessus)
3. Fournir ces données au frontend via sessionStorage ou URL

### Exemple d'intégration dans le backend (pseudo-code)

```javascript
// 1. Récupérer les données du CV
const cvData = parseCV(uploadedFile);

// 2. Transformer les données au format attendu
const formData = {
  personalInfo: {
    fullName: cvData.name,
    jobTitle: cvData.currentPosition || cvData.desiredPosition || "",
  },
  mobility: {
    transportMethods: [],
    address: cvData.address || "",
    officePreference: ""
  },
  motivations: {
    order: ["remuneration", "evolution", "flexibility", "location", "other"],
    structureTypes: [],
    hasSectorPreference: false,
    salaryRange: cvData.currentSalary || ""
  },
  availability: {
    timeframe: "1month",
    currentlyEmployed: cvData.currentEmployment ? true : false,
    recruitmentStatus: "no-leads"
  }
};

// 3. Stocker les données avec un identifiant unique
const dataId = generateUniqueId();
storeFormData(dataId, formData);

// 4. Rediriger vers le formulaire avec l'identifiant dans l'URL
redirectTo(`/templates/candidate-questionnaire.html?parsed_data_id=${dataId}`);
```

## Test de la fonctionnalité

Pour tester la fonctionnalité sans backend, vous pouvez utiliser le fichier `parsed-data-example.js` :

1. Ouvrez la page du formulaire candidat
2. Ouvrez la console du navigateur
3. Exécutez la fonction `storeParseDataForTesting()`
4. Rechargez la page

Vous verrez le formulaire se remplir automatiquement avec les données d'exemple.

## Personnalisation

Si vous avez besoin de modifier la structure des données ou d'ajouter de nouveaux champs :

1. Mettez à jour la structure des données dans `parsed-data-example.js`
2. Ajoutez le code correspondant dans la méthode `fillForm()` du script `form-prefiller.js`

## Bonnes pratiques de sécurité

- Ne stockez pas d'informations sensibles dans sessionStorage ou dans l'URL
- Utilisez HTTPS pour toutes les communications
- Validez les données côté serveur avant de les envoyer au client
- Purgez les données de sessionStorage après utilisation