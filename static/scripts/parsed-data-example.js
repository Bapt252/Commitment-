/**
 * Exemple de données parsées pour tester le pré-remplissage du formulaire
 * À stocker dans sessionStorage pour simuler des données venant du backend
 */

// Format correspondant au format de données du backend (format brut avant transformation)
const mockParsedData = {
  "processing_time": 1.23,
  "parsed_at": 1714505237.987,
  "file_format": ".pdf",
  "model": "gpt-4o-mini",
  "data": {
    "personal_info": {
      "name": "Thomas Dupont",
      "email": "thomas.dupont@email.com",
      "phone": "06 12 34 56 78",
      "address": "15 Rue de la République, 75001 Paris"
    },
    "position": "Développeur Full Stack JavaScript",
    "skills": [
      { "name": "JavaScript" },
      { "name": "React" },
      { "name": "Node.js" },
      { "name": "TypeScript" },
      { "name": "Express" }
    ],
    "experience": [
      {
        "title": "Développeur Frontend",
        "company": "TechStart",
        "start_date": "Janvier 2021",
        "end_date": "Présent",
        "description": "Développement d'applications web avec React"
      },
      {
        "title": "Développeur Junior",
        "company": "WebAgency",
        "start_date": "Juin 2019",
        "end_date": "Décembre 2020",
        "description": "Maintenance et développement d'applications web"
      }
    ],
    "education": [
      {
        "degree": "Master en Informatique",
        "institution": "Université Paris-Saclay",
        "start_date": "2017",
        "end_date": "2019"
      },
      {
        "degree": "Licence Informatique",
        "institution": "Université de Lyon",
        "start_date": "2014",
        "end_date": "2017"
      }
    ],
    "languages": [
      { "language": "Français", "level": "Natif" },
      { "language": "Anglais", "level": "Courant" },
      { "language": "Espagnol", "level": "Intermédiaire" }
    ],
    "softwares": [
      "VS Code",
      "Git",
      "Docker",
      "Figma",
      "Jira"
    ]
  }
};

/**
 * Fonction pour stocker les données dans sessionStorage
 * À exécuter dans la console pour tester le pré-remplissage
 */
function storeParseDataForTesting() {
  try {
    // Stocker les données dans sessionStorage
    sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
    console.log("✅ Données parsées stockées avec succès dans sessionStorage");
    
    // Appliquer directement le pré-remplissage si FormPrefiller est disponible
    if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
      console.log("⚙️ Tentative d'initialisation du FormPrefiller avec les données mockées");
      window.FormPrefiller.initialize(mockParsedData);
    } else {
      console.warn("⚠️ Le FormPrefiller n'est pas encore disponible, attendez que la page soit complètement chargée");
      // On va tenter d'appliquer un pré-remplissage manuel basique
      setTimeout(function() {
        console.log("⚙️ Tentative de pré-remplissage manuel différé");
        const nameField = document.getElementById('full-name');
        const jobField = document.getElementById('job-title');
        
        if (nameField && mockParsedData.data && mockParsedData.data.personal_info) {
          nameField.value = mockParsedData.data.personal_info.name || '';
          console.log("✅ Champ 'Nom Prénom' pré-rempli avec:", nameField.value);
        }
        
        if (jobField && mockParsedData.data) {
          jobField.value = mockParsedData.data.position || '';
          console.log("✅ Champ 'Intitulé de poste' pré-rempli avec:", jobField.value);
        }
      }, 500);
    }
    
    return true;
  } catch (error) {
    console.error("❌ Erreur lors du stockage des données de test:", error);
    return false;
  }
}

// Cette fonction est exécutée automatiquement au chargement du script
(function() {
  console.log("📝 Script de données d'exemple chargé");
  
  // Stocker les données immédiatement
  const stored = storeParseDataForTesting();
  
  // S'assurer que le pré-remplissage sera effectué une fois le DOM chargé
  if (stored) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function() {
        console.log("🔄 DOM chargé, nouvelle tentative de pré-remplissage");
        if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
          window.FormPrefiller.initialize(mockParsedData);
        }
      });
    } else {
      // Le DOM est déjà chargé
      console.log("🔄 DOM déjà chargé, nouvelle tentative de pré-remplissage");
      if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
        window.FormPrefiller.initialize(mockParsedData);
      }
    }
  }
})();
