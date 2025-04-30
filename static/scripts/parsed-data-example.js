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
 * et initialiser le pré-remplissage du formulaire
 */
function storeParseDataForTesting() {
  try {
    // Stocker les données dans sessionStorage
    sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
    console.log("✅ Données parsées stockées avec succès dans sessionStorage");
    
    // Définir les fonctions globales si elles n'existent pas encore
    ensureGlobalFunctionsExist();
    
    // Appliquer directement le pré-remplissage si FormPrefiller est disponible
    if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
      console.log("⚙️ Initialisation du FormPrefiller avec les données mockées");
      window.FormPrefiller.initialize(mockParsedData);
    } else {
      console.log("⚠️ Le FormPrefiller n'est pas encore disponible, programmation d'une nouvelle tentative...");
      // Effectuer plusieurs tentatives de pré-remplissage avec délais croissants
      attemptFormFilling(0);
    }
    
    return true;
  } catch (error) {
    console.error("❌ Erreur lors du stockage des données de test:", error);
    return false;
  }
}

/**
 * S'assure que les fonctions globales requises pour le formulaire existent
 */
function ensureGlobalFunctionsExist() {
  // Fonction pour afficher/masquer les préférences de secteur
  if (typeof window.toggleSectorPreference !== 'function') {
    window.toggleSectorPreference = function(radio) {
      const container = document.getElementById('sector-preference-container');
      if (container) {
        container.style.display = radio.value === 'yes' ? 'block' : 'none';
      }
    };
  }
  
  // Fonction pour afficher/masquer les secteurs prohibés
  if (typeof window.toggleProhibitedSector !== 'function') {
    window.toggleProhibitedSector = function(radio) {
      const container = document.getElementById('prohibited-sector-selection');
      if (container) {
        container.style.display = radio.value === 'yes' ? 'block' : 'none';
      }
    };
  }
  
  // Fonction pour afficher/masquer les sections en fonction du statut d'emploi
  if (typeof window.toggleEmploymentStatus !== 'function') {
    window.toggleEmploymentStatus = function(radio) {
      const employedSection = document.getElementById('employed-section');
      const unemployedSection = document.getElementById('unemployed-section');
      
      if (employedSection && unemployedSection) {
        employedSection.style.display = radio.value === 'yes' ? 'block' : 'none';
        unemployedSection.style.display = radio.value === 'yes' ? 'none' : 'block';
        
        // Gestion des champs requis
        if (radio.value === 'yes') {
          document.querySelectorAll('#employed-section input[type="radio"][name="listening-reason"]').forEach(input => {
            input.setAttribute('required', '');
          });
          const noticePeriod = document.getElementById('notice-period');
          if (noticePeriod) noticePeriod.setAttribute('required', '');
          document.querySelectorAll('#employed-section input[type="radio"][name="notice-negotiable"]').forEach(input => {
            input.setAttribute('required', '');
          });
          
          document.querySelectorAll('#unemployed-section input[type="radio"][name="contract-end-reason"]').forEach(input => {
            input.removeAttribute('required');
          });
        } else {
          document.querySelectorAll('#unemployed-section input[type="radio"][name="contract-end-reason"]').forEach(input => {
            input.setAttribute('required', '');
          });
          
          document.querySelectorAll('#employed-section input[type="radio"][name="listening-reason"]').forEach(input => {
            input.removeAttribute('required');
          });
          const noticePeriod = document.getElementById('notice-period');
          if (noticePeriod) noticePeriod.removeAttribute('required');
          document.querySelectorAll('#employed-section input[type="radio"][name="notice-negotiable"]').forEach(input => {
            input.removeAttribute('required');
          });
        }
      }
    };
  }
}

/**
 * Tente de remplir le formulaire à plusieurs reprises avec des délais croissants
 * @param {number} attempt - Numéro de la tentative actuelle
 */
function attemptFormFilling(attempt) {
  const maxAttempts = 5;
  const delays = [500, 1000, 2000, 3000, 5000]; // Délais croissants entre chaque tentative
  
  if (attempt >= maxAttempts) {
    console.warn("⚠️ Nombre maximum de tentatives atteint. Pré-remplissage automatique abandonné.");
    return;
  }
  
  setTimeout(function() {
    console.log(`🔄 Tentative de pré-remplissage #${attempt + 1}`);
    
    if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
      window.FormPrefiller.initialize(mockParsedData);
      console.log(`✅ Pré-remplissage réussi à la tentative #${attempt + 1}`);
    } else {
      console.log(`⏳ FormPrefiller toujours pas disponible. Nouvelle tentative programmée...`);
      // Programmation de la prochaine tentative
      attemptFormFilling(attempt + 1);
      
      // Si c'est la deuxième tentative, essayons de charger dynamiquement le script
      if (attempt === 1) {
        loadFormPrefillerScript();
      }
      
      // Après plusieurs tentatives, essayons un remplissage manuel basique
      if (attempt === 3) {
        applyBasicFormFilling();
      }
    }
  }, delays[attempt]);
}

/**
 * Charge dynamiquement le script FormPrefiller s'il n'est pas déjà chargé
 */
function loadFormPrefillerScript() {
  if (!document.querySelector('script[src*="form-prefiller.js"]')) {
    console.log("📥 Chargement dynamique du script form-prefiller.js");
    const script = document.createElement('script');
    script.src = "../static/scripts/form-prefiller.js";
    script.onload = function() {
      console.log("✅ Script form-prefiller.js chargé avec succès");
      if (window.FormPrefiller) {
        window.FormPrefiller.initialize(mockParsedData);
      }
    };
    document.head.appendChild(script);
  }
}

/**
 * Applique un pré-remplissage basique pour les champs essentiels
 * quand tout le reste échoue
 */
function applyBasicFormFilling() {
  console.log("🔧 Application d'un pré-remplissage basique de secours");
  
  try {
    // Informations personnelles
    const fullNameField = document.getElementById('full-name');
    if (fullNameField) {
      fullNameField.value = mockParsedData.data.personal_info.name || '';
      fullNameField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    const jobTitleField = document.getElementById('job-title');
    if (jobTitleField) {
      jobTitleField.value = mockParsedData.data.position || '';
      jobTitleField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // Adresse
    const addressField = document.getElementById('address');
    if (addressField && mockParsedData.data.personal_info.address) {
      addressField.value = mockParsedData.data.personal_info.address;
      addressField.dispatchEvent(new Event('input', { bubbles: true }));
    }
    
    // Transport (cocher transport en commun par défaut)
    const publicTransportCheckbox = document.querySelector('input[name="transport-method"][value="public-transport"]');
    if (publicTransportCheckbox) {
      publicTransportCheckbox.checked = true;
      publicTransportCheckbox.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    console.log("✅ Pré-remplissage basique appliqué");
    
    // Afficher une notification
    if (window.showNotification) {
      window.showNotification("Formulaire partiellement pré-rempli avec vos informations", "success");
    }
  } catch (error) {
    console.error("❌ Erreur lors du pré-remplissage basique:", error);
  }
}

// Exécution automatique au chargement du script
(function() {
  console.log("📝 Script de données d'exemple chargé");
  
  // Vérifier si les données sont déjà stockées pour éviter tout doublon
  const existingData = sessionStorage.getItem('parsedCandidateData');
  if (!existingData) {
    console.log("🔄 Première exécution, stockage et application des données de test");
    storeParseDataForTesting();
  } else {
    console.log("📋 Données déjà présentes dans sessionStorage");
    
    // Si les données existent mais le formulaire n'est pas encore rempli, on tente quand même
    const fullNameField = document.getElementById('full-name');
    if (fullNameField && !fullNameField.value && document.readyState !== 'loading') {
      console.log("🔄 Formulaire non rempli, nouvelle tentative de pré-remplissage");
      storeParseDataForTesting();
    }
  }
  
  // S'assurer que le pré-remplissage est effectué une fois le DOM chargé
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      console.log("🔄 DOM chargé, vérification de l'état du pré-remplissage");
      // Vérifier si le formulaire a des valeurs
      const fullNameField = document.getElementById('full-name');
      if (fullNameField && !fullNameField.value) {
        console.log("🔄 Formulaire non rempli après chargement du DOM, nouvelle tentative");
        storeParseDataForTesting();
      }
    });
  }
  
  // Ajouter un événement au cas où la page aurait fini de charger avant notre exécution
  window.addEventListener('load', function() {
    console.log("🔄 Page entièrement chargée, vérification finale de l'état du pré-remplissage");
    const fullNameField = document.getElementById('full-name');
    if (fullNameField && !fullNameField.value) {
      console.log("🔄 Formulaire toujours non rempli, dernière tentative");
      storeParseDataForTesting();
    }
  });
})();