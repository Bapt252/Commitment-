/**
 * job-parser-connector.js
 * Script pour connecter le back-end du job parser au front-end du site
 */

// Configuration
// En mode production, utiliser l'URL de production ou utiliser directement des données de test
const USE_TEST_DATA = true; // Toujours utiliser les données de test (pour la démo)
const API_BASE_URL = 'https://api.commitment-app.com'; // URL de base de l'API job-parser-service
const API_ENDPOINT = '/api/parse-job'; // Point d'entrée de l'API

// Sélecteurs DOM
const SELECTORS = {
  dropZone: '#job-drop-zone',
  fileInput: '#job-file-input',
  textArea: '#job-description-text',
  analyzeButton: '#analyze-job-text',
  analysisResults: '#inline-analysis-results',
  jobInfoContainer: '#job-info-container',
  jobTitleValue: '#job-title-value',
  jobSkillsValue: '#job-skills-value',
  jobExperienceValue: '#job-experience-value',
  jobContractValue: '#job-contract-value',
  editButton: '#edit-parsed-info',
  previewButton: '#preview-job-info',
  loadingIndicator: '#analysis-loader',
  // Nouveaux sélecteurs pour les champs additionnels
  jobLocationValue: '#job-location-value',
  jobResponsibilitiesValue: '#job-responsibilities-value',
  jobEducationValue: '#job-education-value',
  jobBenefitsValue: '#job-benefits-value',
  jobSalaryValue: '#job-salary-value'
};

// Classe principale du connecteur
class JobParserConnector {
  constructor() {
    this.initElements();
    this.setupEventListeners();
    this.cachedJobData = null;
    console.log('JobParserConnector initialisé');
  }

  // Initialiser les références aux éléments du DOM
  initElements() {
    this.elements = {};
    
    for (const [key, selector] of Object.entries(SELECTORS)) {
      this.elements[key] = document.querySelector(selector);
      
      // Journaliser les éléments manquants pour débogage
      if (!this.elements[key] && selector !== '#edit-parsed-info' && selector !== '#preview-job-info') {
        console.warn(`Élément non trouvé: ${selector}`);
      }
    }
  }

  // Configurer les écouteurs d'événements
  setupEventListeners() {
    // Pour le glisser-déposer
    if (this.elements.dropZone && this.elements.fileInput) {
      this.setupDropZone();
    }

    // Pour le bouton d'analyse
    if (this.elements.analyzeButton) {
      this.elements.analyzeButton.addEventListener('click', () => this.analyzeJobDescription());
    }

    // Pour le bouton d'édition manuelle (si présent)
    if (this.elements.editButton) {
      this.elements.editButton.addEventListener('click', () => this.enableManualEditing());
    }
    
    // Pour le bouton de prévisualisation (si présent)
    if (this.elements.previewButton) {
      this.elements.previewButton.addEventListener('click', () => {
        if (window.JobPreview) {
          const preview = new window.JobPreview();
          preview.showPreview();
        } else {
          console.warn('JobPreview n\'est pas disponible');
        }
      });
    }
  }

  // Configurer la zone de glisser-déposer
  setupDropZone() {
    const { dropZone, fileInput } = this.elements;

    // Prévenir le comportement par défaut pour permettre le drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
      }, false);
    });

    // Mettre en surbrillance la zone lors du survol
    ['dragenter', 'dragover'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('highlight');
      }, false);
    });

    // Enlever la surbrillance
    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('highlight');
      }, false);
    });

    // Gérer le drop de fichier
    dropZone.addEventListener('drop', (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        fileInput.files = files;
        this.updateDropZoneText(files[0].name);
      }
    }, false);

    // Gérer la sélection de fichier via l'input
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length > 0) {
        this.updateDropZoneText(fileInput.files[0].name);
      }
    });

    // Cliquer sur la zone pour ouvrir le sélecteur de fichier
    dropZone.addEventListener('click', () => {
      fileInput.click();
    });
  }

  // Mettre à jour le texte de la zone de drop après sélection d'un fichier
  updateDropZoneText(fileName) {
    const dropZoneText = this.elements.dropZone.querySelector('.drop-zone-text');
    if (dropZoneText) {
      dropZoneText.textContent = `Fichier sélectionné: ${fileName}`;
    }
  }

  // Analyser la fiche de poste (fichier ou texte)
  analyzeJobDescription() {
    // Vérifier si un fichier a été sélectionné ou si du texte a été entré
    const hasFile = this.elements.fileInput && this.elements.fileInput.files && this.elements.fileInput.files.length > 0;
    const hasText = this.elements.textArea && this.elements.textArea.value.trim() !== '';
    
    if (!hasFile && !hasText) {
      this.showNotification('Veuillez sélectionner un fichier ou saisir du texte à analyser.', 'error');
      return;
    }

    // Afficher l'indicateur de chargement
    if (this.elements.loadingIndicator) {
      this.elements.loadingIndicator.style.display = 'flex';
    }
    
    this.showLoadingIndicator();

    // Si on doit toujours utiliser les données de test, on court-circuite l'appel API
    if (USE_TEST_DATA) {
      setTimeout(() => {
        this.hideLoadingIndicator();
        if (this.elements.loadingIndicator) {
          this.elements.loadingIndicator.style.display = 'none';
        }
        this.processAPIResponse(this.getTestData());
      }, 1500); // Simuler un délai d'API
      return;
    }

    if (hasFile) {
      // Analyser le fichier
      const file = this.elements.fileInput.files[0];
      this.parseFileWithAPI(file);
    } else {
      // Analyser le texte
      const text = this.elements.textArea.value;
      this.parseTextWithAPI(text);
    }
  }

  // Analyser un fichier avec l'API
  parseFileWithAPI(file) {
    console.log(`Envoi du fichier "${file.name}" à l'API ${API_BASE_URL}${API_ENDPOINT}`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch(API_BASE_URL + API_ENDPOINT, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Données extraites reçues:', data);
      this.hideLoadingIndicator();
      if (this.elements.loadingIndicator) {
        this.elements.loadingIndicator.style.display = 'none';
      }
      
      // Traiter la réponse de l'API et mettre à jour l'interface
      this.processAPIResponse(data);
    })
    .catch(error => {
      console.error('Erreur lors de l\'appel à l\'API:', error);
      this.hideLoadingIndicator();
      if (this.elements.loadingIndicator) {
        this.elements.loadingIndicator.style.display = 'none';
      }
      this.showNotification(`Erreur lors de l'analyse: ${error.message}`, 'error');
      
      // En cas d'erreur, utiliser des données de test pour la démo
      this.processAPIResponse(this.getTestData());
    });
  }

  // Analyser du texte avec l'API
  parseTextWithAPI(text) {
    console.log(`Envoi du texte à l'API ${API_BASE_URL}${API_ENDPOINT}`);
    
    // Créer un fichier Blob à partir du texte
    const blob = new Blob([text], { type: 'text/plain' });
    const file = new File([blob], 'job-description.txt', { type: 'text/plain' });
    
    this.parseFileWithAPI(file);
  }

  // Traiter la réponse de l'API et mettre à jour l'interface
  processAPIResponse(data) {
    // Stocker les données dans le cache
    this.cachedJobData = data;
    
    // Extraire les données pertinentes
    let jobData = data;
    
    // Si les données sont dans un sous-objet "data"
    if (data && data.data) {
      jobData = data.data;
    }
    
    // Mettre à jour l'interface
    if (jobData) {
      // Mettre à jour le titre du poste
      if (this.elements.jobTitleValue) {
        this.elements.jobTitleValue.textContent = jobData.title || 'Non spécifié';
      }
      
      // Mettre à jour les compétences
      if (this.elements.jobSkillsValue) {
        const skills = [];
        
        // Combiner compétences requises et souhaitées
        if (jobData.required_skills && jobData.required_skills.length > 0) {
          skills.push(...jobData.required_skills);
        }
        if (jobData.preferred_skills && jobData.preferred_skills.length > 0) {
          skills.push(...jobData.preferred_skills);
        }
        
        if (skills.length > 0) {
          // Créer une liste pour les compétences
          this.elements.jobSkillsValue.innerHTML = '';
          const ul = document.createElement('ul');
          
          skills.forEach(skill => {
            const li = document.createElement('li');
            li.textContent = skill;
            ul.appendChild(li);
          });
          
          this.elements.jobSkillsValue.appendChild(ul);
        } else {
          this.elements.jobSkillsValue.textContent = 'Non spécifié';
        }
      }
      
      // Mettre à jour l'expérience
      if (this.elements.jobExperienceValue) {
        let experience = 'Non spécifié';
        
        // Chercher l'expérience dans différents champs
        if (jobData.requirements && jobData.requirements.length > 0) {
          // Chercher dans les prérequis
          const expReq = jobData.requirements.find(req => 
            req.toLowerCase().includes('expérience') || 
            req.toLowerCase().includes('ans') ||
            req.toLowerCase().includes('experience')
          );
          
          if (expReq) {
            experience = expReq;
          }
        }
        
        this.elements.jobExperienceValue.textContent = experience;
      }
      
      // Mettre à jour le type de contrat
      if (this.elements.jobContractValue) {
        this.elements.jobContractValue.textContent = jobData.contract_type || 'Non spécifié';
      }
      
      // Mettre à jour le lieu de travail
      if (this.elements.jobLocationValue) {
        this.elements.jobLocationValue.textContent = jobData.location || 'Non spécifié';
      }
      
      // Mettre à jour les responsabilités/missions
      if (this.elements.jobResponsibilitiesValue) {
        if (jobData.responsibilities && jobData.responsibilities.length > 0) {
          // Créer une liste de responsabilités
          this.elements.jobResponsibilitiesValue.innerHTML = '';
          const ul = document.createElement('ul');
          ul.className = 'responsibility-list';
          
          jobData.responsibilities.forEach(resp => {
            const li = document.createElement('li');
            li.textContent = resp;
            ul.appendChild(li);
          });
          
          this.elements.jobResponsibilitiesValue.appendChild(ul);
        } else {
          this.elements.jobResponsibilitiesValue.textContent = 'Non spécifié';
        }
      }
      
      // Mettre à jour la formation requise
      if (this.elements.jobEducationValue) {
        let education = 'Non spécifié';
        
        // Chercher la formation/éducation dans les prérequis
        if (jobData.requirements && jobData.requirements.length > 0) {
          const eduReq = jobData.requirements.find(req =>
            req.toLowerCase().includes('diplôme') ||
            req.toLowerCase().includes('formation') ||
            req.toLowerCase().includes('bac') ||
            req.toLowerCase().includes('master') ||
            req.toLowerCase().includes('ingénieur') ||
            req.toLowerCase().includes('degree') ||
            req.toLowerCase().includes('education')
          );
          
          if (eduReq) {
            education = eduReq;
          }
        }
        
        this.elements.jobEducationValue.textContent = education;
      }
      
      // Mettre à jour les avantages
      if (this.elements.jobBenefitsValue) {
        if (jobData.benefits && jobData.benefits.length > 0) {
          // Créer une liste d'avantages
          this.elements.jobBenefitsValue.innerHTML = '';
          const ul = document.createElement('ul');
          ul.className = 'benefits-list';
          
          jobData.benefits.forEach(benefit => {
            const li = document.createElement('li');
            li.textContent = benefit;
            ul.appendChild(li);
          });
          
          this.elements.jobBenefitsValue.appendChild(ul);
        } else {
          this.elements.jobBenefitsValue.textContent = 'Non spécifié';
        }
      }
      
      // Mettre à jour le salaire
      if (this.elements.jobSalaryValue) {
        this.elements.jobSalaryValue.textContent = jobData.salary || 'Non spécifié';
      }
      
      // Afficher le conteneur d'information
      if (this.elements.jobInfoContainer) {
        this.elements.jobInfoContainer.style.display = 'block';
      }
      
      // Masquer l'analyseur inline
      const inlineJobParser = document.getElementById('inline-job-parser');
      if (inlineJobParser) {
        inlineJobParser.style.display = 'none';
      }
      
      // Afficher une notification de succès
      this.showNotification('Fiche de poste analysée avec succès!', 'success');
    } else {
      this.showNotification('Aucune donnée n\'a pu être extraite de la fiche de poste.', 'error');
    }
  }

  // Activer l'édition manuelle des informations extraites
  enableManualEditing() {
    // Transformer chaque valeur en champ éditable
    const fields = [
      'jobTitleValue', 
      'jobExperienceValue', 
      'jobContractValue',
      'jobLocationValue',
      'jobEducationValue',
      'jobSalaryValue'
    ];
    
    fields.forEach(field => {
      if (this.elements[field]) {
        const element = this.elements[field];
        const currentValue = element.textContent;
        
        // Créer un input pour remplacer le texte
        const input = document.createElement('input');
        input.type = 'text';
        input.value = currentValue === 'Non spécifié' ? '' : currentValue;
        input.className = 'form-control form-control-sm';
        input.placeholder = 'Entrez une valeur...';
        
        // Remplacer le texte par l'input
        element.textContent = '';
        element.appendChild(input);
      }
    });
    
    // Cas spécial pour les compétences (liste)
    if (this.elements.jobSkillsValue) {
      const skillsElement = this.elements.jobSkillsValue;
      const currentSkills = [];
      
      // Collecter les compétences actuelles
      const listItems = skillsElement.querySelectorAll('li');
      listItems.forEach(item => {
        currentSkills.push(item.textContent);
      });
      
      // Créer un textarea pour les compétences
      const textarea = document.createElement('textarea');
      textarea.className = 'form-control form-control-sm';
      textarea.placeholder = 'Entrez les compétences, une par ligne...';
      textarea.value = currentSkills.join('\n');
      textarea.rows = 3;
      
      // Remplacer les tags par le textarea
      skillsElement.innerHTML = '';
      skillsElement.appendChild(textarea);
    }
    
    // Cas spécial pour les responsabilités (liste)
    if (this.elements.jobResponsibilitiesValue) {
      const responsibilitiesElement = this.elements.jobResponsibilitiesValue;
      const currentResponsibilities = [];
      
      // Collecter les responsabilités actuelles
      const listItems = responsibilitiesElement.querySelectorAll('li');
      listItems.forEach(item => {
        currentResponsibilities.push(item.textContent);
      });
      
      // Créer un textarea pour les responsabilités
      const textarea = document.createElement('textarea');
      textarea.className = 'form-control form-control-sm';
      textarea.placeholder = 'Entrez les responsabilités/missions, une par ligne...';
      textarea.value = currentResponsibilities.join('\n');
      textarea.rows = 4;
      
      // Remplacer la liste par le textarea
      responsibilitiesElement.innerHTML = '';
      responsibilitiesElement.appendChild(textarea);
    }
    
    // Cas spécial pour les avantages (liste)
    if (this.elements.jobBenefitsValue) {
      const benefitsElement = this.elements.jobBenefitsValue;
      const currentBenefits = [];
      
      // Collecter les avantages actuels
      const listItems = benefitsElement.querySelectorAll('li');
      listItems.forEach(item => {
        currentBenefits.push(item.textContent);
      });
      
      // Créer un textarea pour les avantages
      const textarea = document.createElement('textarea');
      textarea.className = 'form-control form-control-sm';
      textarea.placeholder = 'Entrez les avantages, un par ligne...';
      textarea.value = currentBenefits.join('\n');
      textarea.rows = 3;
      
      // Remplacer la liste par le textarea
      benefitsElement.innerHTML = '';
      benefitsElement.appendChild(textarea);
    }
    
    // Remplacer le bouton d'édition par un bouton de sauvegarde
    if (this.elements.editButton) {
      this.elements.editButton.innerHTML = '<i class="fas fa-save"></i> Enregistrer les modifications';
      
      // Changer l'action du bouton
      this.elements.editButton.removeEventListener('click', () => this.enableManualEditing());
      this.elements.editButton.addEventListener('click', () => this.saveManualEdits());
    }
  }

  // Sauvegarder les modifications manuelles
  saveManualEdits() {
    // Récupérer les valeurs des champs
    const updatedData = {};
    
    // Titre du poste
    const titleInput = this.elements.jobTitleValue.querySelector('input');
    if (titleInput) {
      updatedData.title = titleInput.value;
    }
    
    // Expérience
    const experienceInput = this.elements.jobExperienceValue.querySelector('input');
    if (experienceInput) {
      updatedData.experience = experienceInput.value;
    }
    
    // Type de contrat
    const contractInput = this.elements.jobContractValue.querySelector('input');
    if (contractInput) {
      updatedData.contract_type = contractInput.value;
    }
    
    // Lieu de travail
    const locationInput = this.elements.jobLocationValue.querySelector('input');
    if (locationInput) {
      updatedData.location = locationInput.value;
    }
    
    // Formation requise
    const educationInput = this.elements.jobEducationValue.querySelector('input');
    if (educationInput) {
      updatedData.education = educationInput.value;
    }
    
    // Salaire
    const salaryInput = this.elements.jobSalaryValue.querySelector('input');
    if (salaryInput) {
      updatedData.salary = salaryInput.value;
    }
    
    // Compétences
    const skillsTextarea = this.elements.jobSkillsValue.querySelector('textarea');
    if (skillsTextarea) {
      const skills = skillsTextarea.value.split('\n').map(skill => skill.trim()).filter(skill => skill !== '');
      updatedData.required_skills = skills;
    }
    
    // Responsabilités
    const responsibilitiesTextarea = this.elements.jobResponsibilitiesValue.querySelector('textarea');
    if (responsibilitiesTextarea) {
      const responsibilities = responsibilitiesTextarea.value.split('\n').map(item => item.trim()).filter(item => item !== '');
      updatedData.responsibilities = responsibilities;
    }
    
    // Avantages
    const benefitsTextarea = this.elements.jobBenefitsValue.querySelector('textarea');
    if (benefitsTextarea) {
      const benefits = benefitsTextarea.value.split('\n').map(item => item.trim()).filter(item => item !== '');
      updatedData.benefits = benefits;
    }
    
    // Mettre à jour les données en cache
    this.cachedJobData = { ...this.cachedJobData, ...updatedData };
    
    // Mettre à jour l'interface
    this.processAPIResponse(this.cachedJobData);
    
    // Restaurer le bouton d'édition
    if (this.elements.editButton) {
      this.elements.editButton.innerHTML = '<i class="fas fa-edit"></i> Modifier manuellement';
      
      // Changer l'action du bouton
      this.elements.editButton.removeEventListener('click', () => this.saveManualEdits());
      this.elements.editButton.addEventListener('click', () => this.enableManualEditing());
    }
    
    // Afficher une notification
    this.showNotification('Modifications sauvegardées avec succès!', 'success');
  }

  // Afficher l'indicateur de chargement
  showLoadingIndicator() {
    if (this.elements.analysisResults) {
      this.elements.analysisResults.style.display = 'block';
      this.elements.analysisResults.innerHTML = `
        <div style="text-align:center; padding: 20px;">
          <i class="fas fa-spinner fa-spin" style="font-size: 24px; color: #7C3AED;"></i>
          <p>Analyse en cours avec GPT...</p>
        </div>
      `;
    }
  }

  // Masquer l'indicateur de chargement
  hideLoadingIndicator() {
    if (this.elements.analysisResults) {
      this.elements.analysisResults.style.display = 'none';
    }
  }

  // Afficher une notification
  showNotification(message, type = 'success') {
    // Utiliser la fonction globale si disponible
    if (window.showNotification) {
      window.showNotification(message, type);
      return;
    }
    
    // Sinon, créer une notification temporaire
    const notification = document.createElement('div');
    notification.className = `notification-temp ${type}`;
    notification.textContent = message;
    
    // Styles de la notification
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.padding = '15px 20px';
    notification.style.borderRadius = '5px';
    notification.style.zIndex = '9999';
    notification.style.transition = 'all 0.3s ease';
    
    if (type === 'success') {
      notification.style.backgroundColor = '#10B981';
    } else {
      notification.style.backgroundColor = '#EF4444';
    }
    
    notification.style.color = 'white';
    
    document.body.appendChild(notification);
    
    // Supprimer après 5 secondes
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 5000);
  }

  // Obtenir des données de test pour la démo
  getTestData() {
    return {
      data: {
        title: "Développeur Full Stack JavaScript",
        company: "Tech Innovations",
        location: "Paris, France (Hybride)",
        contract_type: "CDI",
        salary: "45K€ - 55K€ selon expérience",
        required_skills: [
          "JavaScript",
          "React",
          "Node.js",
          "Express",
          "MongoDB"
        ],
        preferred_skills: [
          "TypeScript",
          "Docker",
          "AWS",
          "GraphQL"
        ],
        responsibilities: [
          "Développer des applications web complètes",
          "Collaborer avec l'équipe produit",
          "Maintenir et améliorer les applications existantes",
          "Participer aux code reviews",
          "Contribuer à l'architecture technique des projets"
        ],
        requirements: [
          "3+ ans d'expérience en développement web",
          "Diplôme en informatique ou équivalent",
          "Bonne maîtrise de l'anglais"
        ],
        benefits: [
          "Télétravail partiel (3j/semaine)",
          "RTT et 25 jours de congés",
          "Tickets restaurant (12€/jour)",
          "Mutuelle d'entreprise prise en charge à 80%",
          "Plan d'épargne entreprise",
          "Formation continue et conférences"
        ]
      }
    };
  }
}

// Initialiser le connecteur lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
  const connector = new JobParserConnector();
  
  // Rendre l'instance accessible globalement pour le débogage
  window.JobParserConnector = connector;
});

// Initialiser immédiatement si le DOM est déjà chargé
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  const connector = new JobParserConnector();
  window.JobParserConnector = connector;
}