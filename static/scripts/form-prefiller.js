/**
 * Form-prefiller.js - Script pour pré-remplir automatiquement le formulaire candidat
 * avec les données parsées depuis le backend.
 */

// Définir l'objet FormPrefiller dans l'espace global
window.FormPrefiller = (function() {
  // Stockage des données parsées
  let parsedData = null;

  /**
   * Initialise le système de pré-remplissage
   * @param {Object} data - Données parsées depuis le backend
   */
  function initialize(data) {
    if (!data) {
      console.warn("Aucune donnée fournie pour le pré-remplissage du formulaire");
      return;
    }

    parsedData = data;
    console.log("Données de pré-remplissage chargées:", parsedData);

    // Convertir les données du format backend au format du formulaire
    transformCvDataToFormData();

    // Attend que le DOM soit chargé avant de pré-remplir le formulaire
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fillForm);
    } else {
      fillForm();
    }
  }

  /**
   * Transforme les données du format backend (parsing CV) au format du formulaire
   */
  function transformCvDataToFormData() {
    if (!parsedData || !parsedData.data) {
      console.warn("Données invalides pour la transformation");
      return;
    }

    const cvData = parsedData.data;

    // Créer une structure de données compatible avec le formulaire
    const formData = {
      personalInfo: {
        fullName: "",
        jobTitle: ""
      },
      mobility: {
        transportMethods: [],
        commuteTimes: {},
        address: "",
        officePreference: ""
      },
      motivations: {
        order: ["remuneration", "evolution", "flexibility", "location", "other"],
        otherMotivation: "",
        structureTypes: [],
        hasSectorPreference: false,
        preferredSectors: [],
        hasProhibitedSectors: false,
        prohibitedSectors: [],
        salaryRange: ""
      },
      availability: {
        timeframe: "1month",
        currentlyEmployed: false,
        listeningReason: "",
        contractEndReason: "",
        noticePeriod: "",
        noticeNegotiable: null,
        recruitmentStatus: "no-leads"
      }
    };

    // Remplir les informations personnelles
    if (cvData.personal_info) {
      formData.personalInfo.fullName = cvData.personal_info.name || "";
      // Ajouter l'adresse si disponible
      if (cvData.personal_info.address) {
        formData.mobility.address = cvData.personal_info.address;
      }
    }

    // Remplir le poste souhaité
    if (cvData.position) {
      formData.personalInfo.jobTitle = cvData.position;
    }

    // Estimer des valeurs par défaut pour les moyens de transport
    // Par défaut, on suppose que la personne utilise les transports en commun et peut-être un véhicule
    formData.mobility.transportMethods = ["public-transport"];
    formData.mobility.commuteTimes = {
      "public-transport": "30"
    };

    // Estimer une fourchette de salaire basée sur le poste (valeurs fictives à ajuster)
    const positionToSalaryMap = {
      "comptable": "32K€ - 45K€ brut annuel",
      "auditeur": "40K€ - 55K€ brut annuel",
      "contrôleur": "35K€ - 50K€ brut annuel",
      "directeur": "70K€ - 90K€ brut annuel",
      "analyste": "35K€ - 50K€ brut annuel",
      "responsable": "45K€ - 60K€ brut annuel",
      "développeur": "40K€ - 60K€ brut annuel"
    };

    // Essayer de déterminer une fourchette de salaire basée sur le poste
    if (cvData.position) {
      const position = cvData.position.toLowerCase();
      for (const [key, value] of Object.entries(positionToSalaryMap)) {
        if (position.includes(key)) {
          formData.motivations.salaryRange = value;
          break;
        }
      }
      // Si aucune correspondance n'est trouvée, utiliser une fourchette par défaut
      if (!formData.motivations.salaryRange) {
        formData.motivations.salaryRange = "35K€ - 50K€ brut annuel";
      }
    }

    // Déterminer le statut d'emploi actuel basé sur les expériences professionnelles
    if (cvData.experience && cvData.experience.length > 0) {
      const latestExperience = cvData.experience[0]; // Supposé être la plus récente
      if (latestExperience.end_date && 
          (latestExperience.end_date.toLowerCase().includes("présent") || 
           latestExperience.end_date.toLowerCase().includes("present") ||
           latestExperience.end_date === "")) {
        formData.availability.currentlyEmployed = true;
        formData.availability.listeningReason = "no-evolution"; // Valeur par défaut
      } else {
        formData.availability.currentlyEmployed = false;
        formData.availability.contractEndReason = "no-evolution"; // Valeur par défaut
      }
    }

    // Détection automatique des types de structures basée sur l'expérience
    const structureDetection = {
      startup: ["startup", "jeune pousse", "incubateur", "innovation"],
      pme: ["pme", "sme", "petite entreprise", "moyenne entreprise"],
      group: ["groupe", "grande entreprise", "multinationale", "corporation"]
    };

    if (cvData.experience) {
      const allExperienceText = cvData.experience.map(exp => 
        `${exp.company || ""} ${exp.description || ""}`).join(" ").toLowerCase();
      
      for (const [type, keywords] of Object.entries(structureDetection)) {
        if (keywords.some(keyword => allExperienceText.includes(keyword))) {
          formData.motivations.structureTypes.push(type);
        }
      }
    }

    // Si aucun type de structure n'a été détecté, ajouter une valeur par défaut
    if (formData.motivations.structureTypes.length === 0) {
      formData.motivations.structureTypes.push("no-preference");
    }

    // Détection des langues pour déterminer si la personne a des préférences de secteur
    // Ex: Si la personne parle plusieurs langues, elle pourrait être intéressée par l'international
    if (cvData.languages && cvData.languages.length > 1) {
      const hasAdvancedEnglish = cvData.languages.some(lang => 
        lang.language.toLowerCase().includes("anglais") && 
        ["courant", "bilingue", "c1", "c2"].some(level => 
          lang.level.toLowerCase().includes(level))
      );

      if (hasAdvancedEnglish) {
        formData.motivations.hasSectorPreference = true;
        formData.motivations.preferredSectors = ["tech", "finance"];
      }
    }

    // Détection des logiciels pour déterminer les secteurs d'activité potentiels
    const softwareToSectorMap = {
      "sap": "tech",
      "sage": "finance",
      "cegid": "finance",
      "dynamics": "finance",
      "oracle": "tech",
      "salesforce": "tech",
      "adobe": "media",
      "autocad": "construction",
      "revit": "construction"
    };

    if (cvData.softwares && cvData.softwares.length > 0) {
      const detectedSectors = new Set();
      
      for (const software of cvData.softwares) {
        const softwareLower = software.toLowerCase();
        for (const [key, sector] of Object.entries(softwareToSectorMap)) {
          if (softwareLower.includes(key)) {
            detectedSectors.add(sector);
          }
        }
      }
      
      if (detectedSectors.size > 0) {
        formData.motivations.hasSectorPreference = true;
        formData.motivations.preferredSectors = Array.from(detectedSectors);
      }
    }

    // Mise à jour des données parsées avec les données transformées
    parsedData = formData;
  }

  /**
   * Remplit tous les champs du formulaire avec les données disponibles
   */
  function fillForm() {
    if (!parsedData || !document.getElementById('questionnaire-form')) {
      return;
    }

    console.log("Début du pré-remplissage du formulaire...");

    // Remplir les informations personnelles (étape 1)
    if (parsedData.personalInfo) {
      // Remplir le nom et prénom
      if (parsedData.personalInfo.fullName) {
        setInputValue('full-name', parsedData.personalInfo.fullName);
      }

      // Remplir l'intitulé de poste
      if (parsedData.personalInfo.jobTitle) {
        setInputValue('job-title', parsedData.personalInfo.jobTitle);
      }
    }

    // Remplir les informations de mobilité et préférences (étape 2)
    if (parsedData.mobility) {
      // Cocher les moyens de transport
      if (parsedData.mobility.transportMethods && Array.isArray(parsedData.mobility.transportMethods)) {
        parsedData.mobility.transportMethods.forEach(method => {
          setCheckboxValue('transport-method', method, true);
        });
        
        // Déclencher l'événement pour afficher les questions de temps de trajet
        triggerTransportMethodsChange();
        
        // Remplir les temps de trajet pour chaque moyen de transport
        if (parsedData.mobility.commuteTimes) {
          Object.keys(parsedData.mobility.commuteTimes).forEach(transportType => {
            const commuteTime = parsedData.mobility.commuteTimes[transportType];
            setSelectValue(`commute-time-${transportType}`, commuteTime);
          });
        }
      }

      // Remplir l'adresse
      if (parsedData.mobility.address) {
        setInputValue('address', parsedData.mobility.address);
      }

      // Définir la préférence de bureau
      if (parsedData.mobility.officePreference) {
        setRadioValue('office-preference', parsedData.mobility.officePreference);
      }
    }

    // Remplir les motivations et secteurs (étape 3)
    if (parsedData.motivations) {
      // Réorganiser les priorités de motivation
      if (parsedData.motivations.order && Array.isArray(parsedData.motivations.order)) {
        reorderMotivations(parsedData.motivations.order);
      }

      // Remplir "autre" motivation si disponible
      if (parsedData.motivations.otherMotivation) {
        setInputValue('other-motivation', parsedData.motivations.otherMotivation);
        document.getElementById('other-motivation-container').style.display = 'block';
      }

      // Cocher les types de structure
      if (parsedData.motivations.structureTypes && Array.isArray(parsedData.motivations.structureTypes)) {
        parsedData.motivations.structureTypes.forEach(type => {
          setCheckboxValue('structure-type', type, true);
        });
      }

      // Définir la préférence de secteur
      if (parsedData.motivations.hasSectorPreference !== undefined) {
        setRadioValue('has-sector-preference', parsedData.motivations.hasSectorPreference ? 'yes' : 'no');
        toggleSectorPreference({ value: parsedData.motivations.hasSectorPreference ? 'yes' : 'no' });

        // Sélectionner les secteurs préférés
        if (parsedData.motivations.preferredSectors && Array.isArray(parsedData.motivations.preferredSectors)) {
          setMultiSelectValues('sector-preference', parsedData.motivations.preferredSectors);
        }

        // Définir les secteurs prohibés
        if (parsedData.motivations.hasProhibitedSectors !== undefined) {
          setRadioValue('has-prohibited-sector', parsedData.motivations.hasProhibitedSectors ? 'yes' : 'no');
          toggleProhibitedSector({ value: parsedData.motivations.hasProhibitedSectors ? 'yes' : 'no' });

          // Sélectionner les secteurs prohibés
          if (parsedData.motivations.prohibitedSectors && Array.isArray(parsedData.motivations.prohibitedSectors)) {
            setMultiSelectValues('prohibited-sector', parsedData.motivations.prohibitedSectors);
          }
        }
      }

      // Remplir la fourchette de salaire
      if (parsedData.motivations.salaryRange) {
        setInputValue('salary-range', parsedData.motivations.salaryRange);
      }
    }

    // Remplir la disponibilité et situation actuelle (étape 4)
    if (parsedData.availability) {
      // Définir la disponibilité
      if (parsedData.availability.timeframe) {
        setRadioValue('availability', parsedData.availability.timeframe);
      }

      // Définir si actuellement en poste
      if (parsedData.availability.currentlyEmployed !== undefined) {
        setRadioValue('currently-employed', parsedData.availability.currentlyEmployed ? 'yes' : 'no');
        toggleEmploymentStatus({ value: parsedData.availability.currentlyEmployed ? 'yes' : 'no' });

        if (parsedData.availability.currentlyEmployed) {
          // Remplir les informations pour les candidats en poste
          if (parsedData.availability.listeningReason) {
            setRadioValue('listening-reason', parsedData.availability.listeningReason);
          }

          if (parsedData.availability.noticePeriod) {
            setSelectValue('notice-period', parsedData.availability.noticePeriod);
          }

          if (parsedData.availability.noticeNegotiable !== undefined) {
            const noticeValue = parsedData.availability.noticeNegotiable === null ? 'unknown' : 
                               (parsedData.availability.noticeNegotiable ? 'yes' : 'no');
            setRadioValue('notice-negotiable', noticeValue);
          }
        } else {
          // Remplir les informations pour les candidats non en poste
          if (parsedData.availability.contractEndReason) {
            setRadioValue('contract-end-reason', parsedData.availability.contractEndReason);
          }
        }
      }

      // Définir l'état du processus de recrutement
      if (parsedData.availability.recruitmentStatus) {
        setRadioValue('recruitment-status', parsedData.availability.recruitmentStatus);
      }
    }

    console.log("Pré-remplissage du formulaire terminé");
    
    // Afficher une notification pour informer l'utilisateur
    if (window.showNotification) {
      window.showNotification("Formulaire pré-rempli avec vos informations", "success");
    }
  }

  // Fonctions utilitaires pour manipuler les éléments du formulaire

  /**
   * Définit la valeur d'un champ de texte
   */
  function setInputValue(id, value) {
    const input = document.getElementById(id);
    if (input) {
      input.value = value;
      // Simuler un événement de changement pour déclencher les validations
      const event = new Event('input', { bubbles: true });
      input.dispatchEvent(event);
    }
  }

  /**
   * Définit la valeur d'un bouton radio
   */
  function setRadioValue(name, value) {
    const radio = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (radio) {
      radio.checked = true;
      // Simuler un événement de changement
      const event = new Event('change', { bubbles: true });
      radio.dispatchEvent(event);
    }
  }

  /**
   * Coche ou décoche une case à cocher
   */
  function setCheckboxValue(name, value, checked) {
    const checkbox = document.querySelector(`input[name="${name}"][value="${value}"]`);
    if (checkbox) {
      checkbox.checked = checked;
      // Simuler un événement de changement
      const event = new Event('change', { bubbles: true });
      checkbox.dispatchEvent(event);
    }
  }

  /**
   * Définit la valeur d'un menu déroulant
   */
  function setSelectValue(id, value) {
    const select = document.getElementById(id);
    if (select) {
      select.value = value;
      // Simuler un événement de changement
      const event = new Event('change', { bubbles: true });
      select.dispatchEvent(event);
    }
  }

  /**
   * Sélectionne plusieurs valeurs dans une liste déroulante multiple
   */
  function setMultiSelectValues(id, values) {
    const select = document.getElementById(id);
    if (select && Array.isArray(values)) {
      // Désélectionner tout d'abord
      Array.from(select.options).forEach(option => {
        option.selected = false;
      });
      
      // Sélectionner les valeurs spécifiées
      values.forEach(value => {
        const option = select.querySelector(`option[value="${value}"]`);
        if (option) {
          option.selected = true;
        }
      });
      
      // Simuler un événement de changement
      const event = new Event('change', { bubbles: true });
      select.dispatchEvent(event);
    }
  }

  /**
   * Réorganise les éléments de motivation selon l'ordre spécifié
   */
  function reorderMotivations(order) {
    const motivationsList = document.getElementById('motivation-priorities');
    if (!motivationsList || !Array.isArray(order)) return;

    // Clone la liste actuelle d'éléments
    const items = Array.from(motivationsList.querySelectorAll('.motivation-item'));
    const itemsMap = {};
    
    // Créer une map des éléments par valeur
    items.forEach(item => {
      const value = item.getAttribute('data-value');
      itemsMap[value] = item;
    });

    // Vider la liste
    motivationsList.innerHTML = '';
    
    // Réinsérer les éléments dans le nouvel ordre
    order.forEach((value, index) => {
      if (itemsMap[value]) {
        const item = itemsMap[value];
        
        // Mettre à jour le numéro
        const numberSpan = item.querySelector('.motivation-number');
        if (numberSpan) {
          numberSpan.textContent = index + 1;
        }
        
        motivationsList.appendChild(item);
      }
    });
    
    // Mettre à jour le champ caché avec l'ordre actuel
    const motivationOrderInput = document.getElementById('motivation-order');
    if (motivationOrderInput) {
      motivationOrderInput.value = order.join(',');
      
      // Mettre à jour l'affichage du champ "Autre" selon la position
      const otherIndex = order.indexOf('other');
      if (otherIndex < 3) {
        document.getElementById('other-motivation-container').style.display = 'block';
        document.getElementById('other-motivation').setAttribute('required', '');
      }
    }
  }

  /**
   * Déclenche l'événement change sur les checkbox de moyens de transport
   * pour activer les questions de temps de trajet
   */
  function triggerTransportMethodsChange() {
    const checkedTransports = document.querySelectorAll('input[name="transport-method"]:checked');
    if (checkedTransports.length > 0) {
      const event = new Event('change', { bubbles: true });
      checkedTransports[0].dispatchEvent(event);
    }
  }

  // Exposer les fonctions publiques
  return {
    initialize: initialize,
    fillForm: fillForm
  };
})();

/**
 * Lorsque le DOM est chargé, nous vérifions s'il y a des données 
 * disponibles pour le pré-remplissage automatique.
 */
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si l'URL contient des paramètres GET pour récupérer les données
  const urlParams = new URLSearchParams(window.location.search);
  const dataId = urlParams.get('parsed_data_id');
  
  if (dataId) {
    // Faire une requête pour récupérer les données parsées
    fetch(`../api/parsed_data/${dataId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Erreur lors de la récupération des données');
        }
        return response.json();
      })
      .then(data => {
        // Initialiser le pré-remplissage avec les données récupérées
        window.FormPrefiller.initialize(data);
      })
      .catch(error => {
        console.error("Erreur lors du chargement des données parsées:", error);
      });
  } else {
    // Essayer de récupérer les données depuis sessionStorage (si disponible)
    try {
      const storedData = sessionStorage.getItem('parsedCandidateData');
      if (storedData) {
        window.FormPrefiller.initialize(JSON.parse(storedData));
      }
    } catch (error) {
      console.warn("Pas de données de pré-remplissage disponibles:", error);
    }
  }
});