// Constantes de configuration
const API_URL = 'http://localhost:5054/api/parse-job';
const SIMULATION_MODE = false; // Désactiver le mode simulation
const DEBUG_MODE = true; // Activer le mode débogage

// Fonction pour journaliser les messages de débogage
function logDebug(message, data = null) {
  if (DEBUG_MODE) {
    if (data) {
      console.log(`[DEBUG] ${message}`, data);
    } else {
      console.log(`[DEBUG] ${message}`);
    }
    
    // Ajouter également les logs à un élément HTML si disponible
    const debugElement = document.getElementById('debug-output');
    if (debugElement) {
      const logItem = document.createElement('div');
      logItem.className = 'debug-log';
      logItem.innerHTML = `<strong>${message}</strong>`;
      
      if (data) {
        const dataStr = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
        logItem.innerHTML += `<pre>${dataStr}</pre>`;
      }
      
      debugElement.appendChild(logItem);
    }
  }
}

// Fonction pour créer un élément de débogage dans la page
function createDebugInterface() {
  if (DEBUG_MODE) {
    // Vérifier si l'élément existe déjà
    if (!document.getElementById('debug-panel')) {
      // Créer le panneau de débogage
      const debugPanel = document.createElement('div');
      debugPanel.id = 'debug-panel';
      debugPanel.style.cssText = 'position: fixed; bottom: 0; right: 0; width: 400px; height: 300px; background: #f0f0f0; border: 1px solid #ccc; z-index: 1000; overflow: auto; padding: 10px; font-family: monospace; font-size: 12px;';
      
      // Ajouter un titre
      const title = document.createElement('h3');
      title.textContent = 'Debug Panel';
      debugPanel.appendChild(title);
      
      // Ajouter un bouton pour effacer les logs
      const clearButton = document.createElement('button');
      clearButton.textContent = 'Effacer les logs';
      clearButton.onclick = function() {
        document.getElementById('debug-output').innerHTML = '';
      };
      debugPanel.appendChild(clearButton);
      
      // Ajouter un conteneur pour les logs
      const debugOutput = document.createElement('div');
      debugOutput.id = 'debug-output';
      debugOutput.style.cssText = 'margin-top: 10px; border-top: 1px solid #ccc; padding-top: 10px;';
      debugPanel.appendChild(debugOutput);
      
      // Ajouter le panneau à la page
      document.body.appendChild(debugPanel);
    }
  }
}

// Fonction pour soumettre un fichier de poste
function submitJobFile(file) {
  // Créer l'interface de débogage si elle n'existe pas
  createDebugInterface();
  
  if (SIMULATION_MODE) {
    // Mode simulation (données fictives)
    logDebug('Mode simulation activé - retour de données simulées');
    
    const simulatedResponse = {
      title: "Développeur Full Stack",
      skills: ["JavaScript", "React", "Node.js", "MongoDB"],
      contract_type: "CDI",
      location: "Paris",
      experience: "3 ans",
      education: "Bac+5",
      salary: "45K€",
      company: "TechCorp"
    };
    
    // Traiter les données simulées
    handleJobData(simulatedResponse);
    
  } else {
    // Mode réel - utiliser l'API
    logDebug(`Mode réel - envoi du fichier "${file.name}" à l'API ${API_URL}`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Afficher un loader
    showLoader();
    
    // Appel à l'API
    fetch(API_URL, {
      method: 'POST',
      body: formData
    })
    .then(response => {
      logDebug(`Réponse reçue avec statut: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Masquer le loader
      hideLoader();
      
      logDebug('Données extraites reçues de l\'API:', data);
      
      // Traiter les données reçues
      handleJobData(data);
    })
    .catch(error => {
      // Masquer le loader
      hideLoader();
      
      logDebug(`Erreur lors de l'appel API: ${error.message}`);
      console.error('Erreur:', error);
      showError(`Une erreur est survenue lors du traitement du fichier: ${error.message}`);
    });
  }
}

// Fonction pour gérer les données du poste
function handleJobData(jobData) {
  logDebug('Traitement des données du poste:', jobData);
  
  // Vérifier que les données contiennent au moins certaines informations essentielles
  if (!jobData.title) {
    logDebug('Avertissement: Titre du poste manquant dans les données');
  }
  
  // Afficher les données extraites dans l'interface
  displayJobTitle(jobData.title);
  displayJobSkills(jobData.skills);
  displayJobDetails({
    contractType: jobData.contract_type,
    location: jobData.location,
    experience: jobData.experience,
    education: jobData.education,
    salary: jobData.salary,
    company: jobData.company
  });
}

// Fonctions d'interface utilisateur
function showLoader() {
  const loader = document.getElementById('loader');
  if (loader) {
    loader.style.display = 'block';
    logDebug('Affichage du loader');
  } else {
    logDebug('Élément loader non trouvé dans le DOM');
  }
}

function hideLoader() {
  const loader = document.getElementById('loader');
  if (loader) {
    loader.style.display = 'none';
    logDebug('Masquage du loader');
  } else {
    logDebug('Élément loader non trouvé dans le DOM');
  }
}

function showError(message) {
  logDebug(`Affichage de l'erreur: ${message}`);
  
  const errorElement = document.getElementById('error-message');
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  } else {
    logDebug('Élément error-message non trouvé dans le DOM, affichage par alert');
    alert(message);
  }
}

function displayJobTitle(title) {
  logDebug(`Affichage du titre du poste: ${title}`);
  
  const titleElement = document.getElementById('job-title');
  if (titleElement) {
    titleElement.textContent = title || 'Titre non disponible';
  } else {
    logDebug('Élément job-title non trouvé dans le DOM');
  }
}

function displayJobSkills(skills) {
  logDebug(`Affichage des compétences:`, skills);
  
  const skillsContainer = document.getElementById('job-skills');
  if (!skillsContainer) {
    logDebug('Élément job-skills non trouvé dans le DOM');
    return;
  }
  
  skillsContainer.innerHTML = '';
  
  if (skills && skills.length > 0) {
    skills.forEach(skill => {
      const skillElement = document.createElement('span');
      skillElement.className = 'skill-tag';
      skillElement.textContent = skill;
      skillsContainer.appendChild(skillElement);
    });
  } else {
    skillsContainer.innerHTML = '<p>Aucune compétence spécifiée</p>';
  }
}

function displayJobDetails(details) {
  logDebug(`Affichage des détails du poste:`, details);
  
  const detailsContainer = document.getElementById('job-details');
  if (!detailsContainer) {
    logDebug('Élément job-details non trouvé dans le DOM');
    return;
  }
  
  // Créer une liste de détails
  const detailsList = document.createElement('ul');
  
  // Ajouter chaque détail disponible
  if (details.contractType) {
    addDetailItem(detailsList, 'Type de contrat', details.contractType);
  }
  
  if (details.location) {
    addDetailItem(detailsList, 'Localisation', details.location);
  }
  
  if (details.experience) {
    addDetailItem(detailsList, 'Expérience requise', details.experience);
  }
  
  if (details.education) {
    addDetailItem(detailsList, 'Formation', details.education);
  }
  
  if (details.salary) {
    addDetailItem(detailsList, 'Salaire', details.salary);
  }
  
  if (details.company) {
    addDetailItem(detailsList, 'Entreprise', details.company);
  }
  
  // Vider le conteneur et ajouter la liste
  detailsContainer.innerHTML = '';
  detailsContainer.appendChild(detailsList);
}

function addDetailItem(list, label, value) {
  const item = document.createElement('li');
  item.innerHTML = `<strong>${label}:</strong> ${value}`;
  list.appendChild(item);
}

// Gestionnaire d'événement pour le formulaire de téléchargement
document.addEventListener('DOMContentLoaded', function() {
  logDebug('Initialisation de l\'application');
  
  // Créer l'interface de débogage
  createDebugInterface();
  
  const fileForm = document.getElementById('file-upload-form');
  const fileInput = document.getElementById('file-input');
  
  if (fileForm && fileInput) {
    logDebug('Formulaire et champ de fichier trouvés, ajout des écouteurs d\'événements');
    
    fileForm.addEventListener('submit', function(event) {
      event.preventDefault();
      logDebug('Formulaire soumis');
      
      const file = fileInput.files[0];
      if (file) {
        logDebug(`Fichier sélectionné: ${file.name} (${file.type})`);
        
        if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
          submitJobFile(file);
        } else {
          logDebug(`Type de fichier non valide: ${file.type}`);
          showError('Veuillez sélectionner un fichier PDF.');
        }
      } else {
        logDebug('Aucun fichier sélectionné');
        showError('Veuillez sélectionner un fichier.');
      }
    });
    
    // Ajouter un écouteur pour le changement de fichier
    fileInput.addEventListener('change', function() {
      const file = fileInput.files[0];
      if (file) {
        logDebug(`Fichier sélectionné: ${file.name} (${file.type})`);
      }
    });
  } else {
    logDebug('ERREUR: Formulaire ou champ de fichier non trouvé dans le DOM');
  }
  
  // Vérifier si on est en mode simulation
  logDebug(`Mode simulation: ${SIMULATION_MODE ? 'ACTIVÉ' : 'DÉSACTIVÉ'}`);
  
  // Vérifier la connectivité avec l'API
  fetch(API_URL, { method: 'GET' })
    .then(response => {
      logDebug(`Test de connectivité à l'API: ${response.status}`);
    })
    .catch(error => {
      logDebug(`Erreur de connectivité à l'API: ${error.message}. Vérifiez que le serveur est en cours d'exécution sur le port 5054.`);
    });
});