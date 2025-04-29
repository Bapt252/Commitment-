/**
 * Exemple de données parsées pour tester le pré-remplissage du formulaire
 * À stocker dans sessionStorage pour simuler des données venant du backend
 */
const mockParsedData = {
  // Informations personnelles (étape 1)
  personalInfo: {
    fullName: "Pierre Dupont",
    jobTitle: "Développeur Full Stack JavaScript"
  },
  
  // Mobilité et préférences (étape 2)
  mobility: {
    transportMethods: ["public-transport", "bike"],
    commuteTimes: {
      "public-transport": "45",
      "bike": "20"
    },
    address: "15 Avenue de la République, 75011 Paris",
    officePreference: "open-space"
  },
  
  // Motivations et secteurs (étape 3)
  motivations: {
    order: ["evolution", "flexibility", "remuneration", "location", "other"],
    otherMotivation: "Environnement de travail stimulant",
    structureTypes: ["startup", "pme"],
    hasSectorPreference: true,
    preferredSectors: ["tech", "healthcare", "education"],
    hasProhibitedSectors: true,
    prohibitedSectors: ["finance", "transportation"],
    salaryRange: "45K€ - 60K€ brut annuel"
  },
  
  // Disponibilité et situation actuelle (étape 4)
  availability: {
    timeframe: "1month",
    currentlyEmployed: true,
    listeningReason: "no-evolution",
    noticePeriod: "1month",
    noticeNegotiable: true,
    recruitmentStatus: "in-progress"
  }
};

/**
 * Fonction pour stocker les données dans sessionStorage
 * À exécuter dans la console pour tester le pré-remplissage
 */
function storeParseDataForTesting() {
  sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
  console.log("Données parsées stockées dans sessionStorage. Rechargez la page pour voir le pré-remplissage automatique.");
}

// Si vous êtes en mode développement, vous pouvez décommenter cette ligne pour charger 
// automatiquement les données de test
// storeParseDataForTesting();