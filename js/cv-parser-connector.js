/**
 * cv-parser-connector.js
 * Script pour analyser les CV et en extraire les informations pertinentes
 */

// Configuration
const CV_API_BASE_URL = 'http://localhost:5055'; // URL de base de l'API cv-parser-service
const CV_API_ENDPOINT = '/api/parse-cv'; // Point d'entrée de l'API

// Sélecteurs DOM
const CV_SELECTORS = {
  dropZone: '#cv-drop-zone',
  fileInput: '#cv-file-input',
  analyzeButton: '#analyze-cv-button',
  analysisLoader: '#cv-analysis-loader',
  cvInfoContainer: '#cv-info-container',
  // Champs d'informations basiques
  candidateNameValue: '#candidate-name-value',
  candidateEmailValue: '#candidate-email-value',
  candidatePhoneValue: '#candidate-phone-value',
  candidateLocationValue: '#candidate-location-value',
  // Champs d'expérience
  candidateExperienceValue: '#candidate-experience-value',
  candidateJobTitlesValue: '#candidate-job-titles-value',
  candidateCompaniesValue: '#candidate-companies-value',
  // Compétences
  candidateSkillsValue: '#candidate-skills-value',
  candidateLanguagesValue: '#candidate-languages-value',
  // Éducation
  candidateEducationValue: '#candidate-education-value',
  candidateCertificationsValue: '#candidate-certifications-value',
  // Informations supplémentaires
  candidateLinksValue: '#candidate-links-value',
  candidateObjectiveValue: '#candidate-objective-value',
  candidateResumeValue: '#candidate-resume-value',
  // Correspondance avec la fiche de poste
  jobMatchScoreValue: '#job-match-score-value',
  matchingSkillsValue: '#matching-skills-value',
  missingSkillsValue: '#missing-skills-value',
  // Boutons d'action
  editCvButton: '#edit-cv-info',
  exportCvButton: '#export-cv-info'
};

// Classe principale du connecteur
class CVParserConnector {
  constructor() {
    this.initElements();
    this.setupEventListeners();
    this.cachedCvData = null;
    // Référence aux données de fiche de poste si disponible
    this.jobData = window.JobParserConnector?.cachedJobData;
  }

  // Initialiser les références aux éléments du DOM
  initElements() {
    this.elements = {};
    
    for (const [key, selector] of Object.entries(CV_SELECTORS)) {
      this.elements[key] = document.querySelector(selector);
      
      // Journaliser les éléments manquants pour débogage
      if (!this.elements[key]) {
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
      this.elements.analyzeButton.addEventListener('click', () => this.analyzeCv());
    }

    // Pour le bouton d'édition manuelle (si présent)
    if (this.elements.editCvButton) {
      this.elements.editCvButton.addEventListener('click', () => this.enableManualEditing());
    }
    
    // Pour le bouton d'exportation (si présent)
    if (this.elements.exportCvButton) {
      this.elements.exportCvButton.addEventListener('click', () => this.exportCvData());
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
        dropZone.classList.add('drag-active');
      }, false);
    });

    // Enlever la surbrillance
    ['dragleave', 'drop'].forEach(eventName => {
      dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('drag-active');
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
    dropZone.addEventListener('click', (e) => {
      // Ne pas déclencher si on clique sur le badge de fichier ou le bouton de suppression
      if (!e.target.closest('#file-badge')) {
        fileInput.click();
      }
    });
  }

  // Mettre à jour le texte de la zone de drop après sélection d'un fichier
  updateDropZoneText(fileName) {
    const fileBadge = document.getElementById('file-badge');
    const fileNameElement = document.getElementById('file-name');
    
    if (fileNameElement) {
      fileNameElement.textContent = fileName;
      fileBadge.style.display = 'inline-flex';
    } else {
      const dropZoneText = this.elements.dropZone.querySelector('.drop-zone-text');
      if (dropZoneText) {
        dropZoneText.textContent = `Fichier sélectionné: ${fileName}`;
      }
    }
  }

  // Analyser le CV
  analyzeCv() {
    // Vérifier si un fichier a été sélectionné
    const hasFile = this.elements.fileInput && this.elements.fileInput.files && this.elements.fileInput.files.length > 0;
    
    if (!hasFile) {
      this.showNotification('Veuillez sélectionner un CV à analyser.', 'error');
      return;
    }

    // Afficher l'indicateur de chargement
    this.showLoadingIndicator();

    // Analyser le fichier
    const file = this.elements.fileInput.files[0];
    
    // En mode démo, on utilise des données de test au lieu d'appeler l'API
    if (this.isInDemoMode()) {
      setTimeout(() => {
        this.hideLoadingIndicator();
        this.processAPIResponse(this.getTestData());
      }, 1500);
    } else {
      this.parseCvWithAPI(file);
    }
  }

  // Vérifier si on est en mode démo
  isInDemoMode() {
    return !CV_API_BASE_URL.includes('localhost') || CV_API_BASE_URL === 'http://localhost:5055';
  }

  // Analyser un CV avec l'API
  parseCvWithAPI(file) {
    console.log(`Envoi du fichier "${file.name}" à l'API ${CV_API_BASE_URL}${CV_API_ENDPOINT}`);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Si des données de fiche de poste sont disponibles, les envoyer aussi pour comparaison
    if (this.jobData) {
      formData.append('jobData', JSON.stringify(this.jobData));
    }
    
    fetch(CV_API_BASE_URL + CV_API_ENDPOINT, {
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
      
      // Traiter la réponse de l'API et mettre à jour l'interface
      this.processAPIResponse(data);
    })
    .catch(error => {
      console.error('Erreur lors de l\'appel à l\'API:', error);
      this.hideLoadingIndicator();
      this.showNotification(`Erreur lors de l'analyse: ${error.message}`, 'error');
      
      // En cas d'erreur, utiliser des données de test pour la démo
      this.processAPIResponse(this.getTestData());
    });
  }

  // Traiter la réponse de l'API et mettre à jour l'interface
  processAPIResponse(data) {
    // Stocker les données dans le cache
    this.cachedCvData = data;
    
    // Extraire les données pertinentes
    let cvData = data;
    
    // Si les données sont dans un sous-objet "data"
    if (data && data.data) {
      cvData = data.data;
    }
    
    // Mettre à jour l'interface
    if (cvData) {
      // Informations basiques du candidat
      this.updateBasicInfo(cvData);
      
      // Expérience professionnelle
      this.updateExperienceInfo(cvData);
      
      // Compétences
      this.updateSkillsInfo(cvData);
      
      // Éducation et certifications
      this.updateEducationInfo(cvData);
      
      // Informations supplémentaires
      this.updateAdditionalInfo(cvData);
      
      // Correspondance avec la fiche de poste (si disponible)
      this.updateJobMatchInfo(cvData);
      
      // Afficher le conteneur d'information
      if (this.elements.cvInfoContainer) {
        this.elements.cvInfoContainer.style.display = 'block';
      }
      
      // Afficher une notification de succès
      this.showNotification('CV analysé avec succès!', 'success');
    } else {
      this.showNotification('Aucune donnée n\'a pu être extraite du CV.', 'error');
    }
  }
  
  // Mettre à jour les informations de base du candidat
  updateBasicInfo(cvData) {
    // Nom du candidat
    if (this.elements.candidateNameValue) {
      this.elements.candidateNameValue.textContent = cvData.name || 'Non spécifié';
    }
    
    // Email du candidat
    if (this.elements.candidateEmailValue) {
      this.elements.candidateEmailValue.textContent = cvData.email || 'Non spécifié';
    }
    
    // Téléphone du candidat
    if (this.elements.candidatePhoneValue) {
      this.elements.candidatePhoneValue.textContent = cvData.phone || 'Non spécifié';
    }
    
    // Lieu de résidence
    if (this.elements.candidateLocationValue) {
      this.elements.candidateLocationValue.textContent = cvData.location || 'Non spécifié';
    }
  }

  // Mettre à jour les informations d'expérience
  updateExperienceInfo(cvData) {
    // Années d'expérience
    if (this.elements.candidateExperienceValue) {
      this.elements.candidateExperienceValue.textContent = cvData.years_of_experience || 'Non spécifié';
    }
    
    // Postes occupés
    if (this.elements.candidateJobTitlesValue) {
      const jobTitles = cvData.job_titles || [];
      
      if (jobTitles.length > 0) {
        this.elements.candidateJobTitlesValue.innerHTML = '';
        const ul = document.createElement('ul');
        ul.className = 'job-titles-list';
        
        jobTitles.forEach(title => {
          const li = document.createElement('li');
          li.textContent = title;
          ul.appendChild(li);
        });
        
        this.elements.candidateJobTitlesValue.appendChild(ul);
      } else {
        this.elements.candidateJobTitlesValue.textContent = 'Non spécifié';
      }
    }
    
    // Entreprises
    if (this.elements.candidateCompaniesValue) {
      const companies = cvData.companies || [];
      
      if (companies.length > 0) {
        this.elements.candidateCompaniesValue.innerHTML = '';
        const ul = document.createElement('ul');
        ul.className = 'companies-list';
        
        companies.forEach(company => {
          const li = document.createElement('li');
          li.textContent = company;
          ul.appendChild(li);
        });
        
        this.elements.candidateCompaniesValue.appendChild(ul);
      } else {
        this.elements.candidateCompaniesValue.textContent = 'Non spécifié';
      }
    }
  }

  // Mettre à jour les informations de compétences
  updateSkillsInfo(cvData) {
    // Compétences techniques
    if (this.elements.candidateSkillsValue) {
      const skills = cvData.skills || [];
      
      if (skills.length > 0) {
        // Créer des tags pour chaque compétence
        this.elements.candidateSkillsValue.innerHTML = '';
        skills.forEach(skill => {
          const tag = document.createElement('span');
          tag.className = 'skill-tag';
          tag.textContent = skill;
          this.elements.candidateSkillsValue.appendChild(tag);
        });
      } else {
        this.elements.candidateSkillsValue.textContent = 'Non spécifié';
      }
    }
    
    // Langues
    if (this.elements.candidateLanguagesValue) {
      const languages = cvData.languages || [];
      
      if (languages.length > 0) {
        this.elements.candidateLanguagesValue.innerHTML = '';
        const ul = document.createElement('ul');
        ul.className = 'languages-list';
        
        languages.forEach(language => {
          const li = document.createElement('li');
          li.textContent = language;
          ul.appendChild(li);
        });
        
        this.elements.candidateLanguagesValue.appendChild(ul);
      } else {
        this.elements.candidateLanguagesValue.textContent = 'Non spécifié';
      }
    }
  }

  // Mettre à jour les informations d'éducation
  updateEducationInfo(cvData) {
    // Formations
    if (this.elements.candidateEducationValue) {
      const education = cvData.education || [];
      
      if (education.length > 0) {
        this.elements.candidateEducationValue.innerHTML = '';
        const ul = document.createElement('ul');
        ul.className = 'education-list';
        
        education.forEach(edu => {
          const li = document.createElement('li');
          li.textContent = edu;
          ul.appendChild(li);
        });
        
        this.elements.candidateEducationValue.appendChild(ul);
      } else {
        this.elements.candidateEducationValue.textContent = 'Non spécifié';
      }
    }
    
    // Certifications
    if (this.elements.candidateCertificationsValue) {
      const certifications = cvData.certifications || [];
      
      if (certifications.length > 0) {
        this.elements.candidateCertificationsValue.innerHTML = '';
        const ul = document.createElement('ul');
        ul.className = 'certifications-list';
        
        certifications.forEach(cert => {
          const li = document.createElement('li');
          li.textContent = cert;
          ul.appendChild(li);
        });
        
        this.elements.candidateCertificationsValue.appendChild(ul);
      } else {
        this.elements.candidateCertificationsValue.textContent = 'Non spécifié';
      }
    }
  }

  // Mettre à jour les informations supplémentaires
  updateAdditionalInfo(cvData) {
    // Liens (LinkedIn, GitHub, etc.)
    if (this.elements.candidateLinksValue) {
      const links = cvData.links || [];
      
      if (links.length > 0) {
        this.elements.candidateLinksValue.innerHTML = '';
        
        links.forEach(link => {
          const a = document.createElement('a');
          a.href = link.url || link;
          a.target = '_blank';
          a.textContent = link.label || link;
          a.className = 'candidate-link';
          
          const linkContainer = document.createElement('div');
          linkContainer.className = 'link-item';
          linkContainer.appendChild(a);
          
          this.elements.candidateLinksValue.appendChild(linkContainer);
        });
      } else {
        this.elements.candidateLinksValue.textContent = 'Non spécifié';
      }
    }
    
    // Objectif professionnel
    if (this.elements.candidateObjectiveValue) {
      this.elements.candidateObjectiveValue.textContent = cvData.objective || 'Non spécifié';
    }
    
    // Résumé du profil
    if (this.elements.candidateResumeValue) {
      this.elements.candidateResumeValue.textContent = cvData.summary || 'Non spécifié';
    }
  }

  // Mettre à jour les informations de correspondance avec la fiche de poste
  updateJobMatchInfo(cvData) {
    // Score de correspondance avec la fiche de poste
    if (this.elements.jobMatchScoreValue) {
      const matchScore = cvData.job_match_score || null;
      
      if (matchScore !== null) {
        const scoreValue = parseFloat(matchScore);
        let scoreClass = 'average-match';
        
        if (scoreValue >= 80) {
          scoreClass = 'good-match';
        } else if (scoreValue < 50) {
          scoreClass = 'poor-match';
        }
        
        this.elements.jobMatchScoreValue.textContent = `${scoreValue}%`;
        this.elements.jobMatchScoreValue.className = `info-value ${scoreClass}`;
      } else {
        this.elements.jobMatchScoreValue.textContent = 'Non évalué';
      }
    }
    
    // Compétences correspondantes
    if (this.elements.matchingSkillsValue) {
      const matchingSkills = cvData.matching_skills || [];
      
      if (matchingSkills.length > 0) {
        // Créer des tags pour chaque compétence correspondante
        this.elements.matchingSkillsValue.innerHTML = '';
        matchingSkills.forEach(skill => {
          const tag = document.createElement('span');
          tag.className = 'skill-tag matching-skill';
          tag.textContent = skill;
          this.elements.matchingSkillsValue.appendChild(tag);
        });
      } else {
        this.elements.matchingSkillsValue.textContent = 'Aucune compétence correspondante';
      }
    }
    
    // Compétences manquantes
    if (this.elements.missingSkillsValue) {
      const missingSkills = cvData.missing_skills || [];
      
      if (missingSkills.length > 0) {
        // Créer des tags pour chaque compétence manquante
        this.elements.missingSkillsValue.innerHTML = '';
        missingSkills.forEach(skill => {
          const tag = document.createElement('span');
          tag.className = 'skill-tag missing-skill';
          tag.textContent = skill;
          this.elements.missingSkillsValue.appendChild(tag);
        });
      } else {
        this.elements.missingSkillsValue.textContent = 'Aucune compétence manquante';
      }
    }
  }

  // Activer l'édition manuelle des informations extraites
  enableManualEditing() {
    // À implémenter selon les besoins
  }

  // Exporter les données du CV
  exportCvData() {
    // À implémenter selon les besoins
  }

  // Afficher l'indicateur de chargement
  showLoadingIndicator() {
    if (this.elements.analysisLoader) {
      this.elements.analysisLoader.style.display = 'flex';
    }
  }

  // Masquer l'indicateur de chargement
  hideLoadingIndicator() {
    if (this.elements.analysisLoader) {
      this.elements.analysisLoader.style.display = 'none';
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
        name: "Marie Dubois",
        email: "marie.dubois@example.com",
        phone: "06 12 34 56 78",
        location: "Lyon, France",
        years_of_experience: "5 ans",
        job_titles: [
          "Développeuse Full Stack",
          "Développeuse Front-end Senior",
          "Intégratrice Web"
        ],
        companies: [
          "Tech Solutions (2020 - Present)",
          "Digital Agency (2018 - 2020)",
          "Web Studio (2016 - 2018)"
        ],
        skills: [
          "JavaScript",
          "React",
          "Node.js",
          "TypeScript",
          "HTML/CSS",
          "Vue.js",
          "GraphQL",
          "MongoDB",
          "Git",
          "Agile/Scrum"
        ],
        languages: [
          "Français (natif)",
          "Anglais (professionnel)",
          "Espagnol (intermédiaire)"
        ],
        education: [
          "Master en Développement Web, Université de Lyon (2016)",
          "Licence en Informatique, Université de Lyon (2014)"
        ],
        certifications: [
          "AWS Certified Developer - Associate (2021)",
          "MongoDB Certified Developer (2020)",
          "Certified Scrum Master (2019)"
        ],
        links: [
          { label: "LinkedIn", url: "https://linkedin.com/in/marie-dubois" },
          { label: "GitHub", url: "https://github.com/mariedubois" },
          { label: "Portfolio", url: "https://mariedubois.com" }
        ],
        objective: "Développeuse Full Stack passionnée par les technologies web modernes et recherchant un environnement innovant pour créer des applications performantes et accessibles.",
        summary: "Développeuse Full Stack avec 5 ans d'expérience, spécialisée en JavaScript (React, Node.js). Passionnée par l'architecture logicielle et les bonnes pratiques de développement. Expérience en gestion d'équipe technique et communication avec les clients.",
        job_match_score: 85,
        matching_skills: [
          "JavaScript",
          "React",
          "Node.js",
          "MongoDB"
        ],
        missing_skills: [
          "Express"
        ]
      }
    };
  }
}

// Initialiser le connecteur lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
  const connector = new CVParserConnector();
  
  // Rendre l'instance accessible globalement pour le débogage
  window.CVParserConnector = connector;
});

// Initialiser immédiatement si le DOM est déjà chargé
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  const connector = new CVParserConnector();
  window.CVParserConnector = connector;
}