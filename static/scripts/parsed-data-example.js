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
 * Applique un pré-remplissage basique pour les champs essentiels
 */
function applyBasicFormFilling() {
  console.log("🔧 Application d'un pré-remplissage basique direct");
  
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
      window.showNotification("Formulaire pré-rempli avec vos informations", "success");
    }
  } catch (error) {
    console.error("❌ Erreur lors du pré-remplissage basique:", error);
  }
}

// Exécution automatique au chargement du script - Version simplifiée sans récursion
(function() {
  console.log("📝 Script de données d'exemple chargé");
  
  // Stocker les données dans sessionStorage
  try {
    sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
    console.log("✅ Données parsées stockées avec succès dans sessionStorage");
  } catch (e) {
    console.error("Erreur lors du stockage des données:", e);
  }
  
  // Définir les fonctions globales
  ensureGlobalFunctionsExist();
  
  // Appliquer directement le pré-remplissage si le DOM est chargé
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(applyBasicFormFilling, 500);
  } else {
    document.addEventListener('DOMContentLoaded', function() {
      setTimeout(applyBasicFormFilling, 500);
    });
  }
  
  // Ajouter une notification de mode démo
  window.addEventListener('load', function() {
    const formContainer = document.querySelector('.form-container');
    if (formContainer && !document.querySelector('.demo-mode-indicator')) {
      const demoIndicator = document.createElement('div');
      demoIndicator.className = 'demo-mode-indicator';
      demoIndicator.innerHTML = '<i class="fas fa-info-circle"></i> Mode démonstration - Données simulées';
      demoIndicator.style.background = 'rgba(124, 58, 237, 0.1)';
      demoIndicator.style.color = 'var(--purple)';
      demoIndicator.style.padding = '12px 16px';
      demoIndicator.style.borderRadius = '8px';
      demoIndicator.style.marginBottom = '20px';
      demoIndicator.style.textAlign = 'center';
      demoIndicator.style.fontWeight = '500';
      formContainer.insertBefore(demoIndicator, formContainer.firstChild);
    }
  });
})();