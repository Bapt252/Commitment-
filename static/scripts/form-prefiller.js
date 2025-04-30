/**
 * Form-prefiller.js - Script pour pré-remplir automatiquement le formulaire candidat
 * avec les données parsées depuis le backend.
 * Version améliorée avec support des données simulées dans un environnement de démonstration
 */

// Définir l'objet FormPrefiller dans l'espace global
window.FormPrefiller = (function() {
  // Stockage des données parsées
  let parsedData = null;
  
  // Constante pour détecter l'environnement
  const IS_DEMO_ENV = window.location.hostname.includes('github.io') || 
                    window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1';

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
    
    // Détecter si les données sont simulées
    const isSimulatedData = parsedData.isSimulated === true || IS_DEMO_ENV;
    if (isSimulatedData && !parsedData.isSimulated) {
      parsedData.isSimulated = true;
      console.log("Données marquées comme simulées (environnement démo)");
    }

    // S'assurer que les fonctions de toggle du formulaire sont définies
    ensureGlobalToggleFunctionsExist();

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
   * S'assure que les fonctions de toggle nécessaires pour le formulaire sont définies
   */
  function ensureGlobalToggleFunctionsExist() {
    if (typeof window.toggleSectorPreference !== 'function') {
        window.toggleSectorPreference = function(radio) {
            const container = document.getElementById('sector-preference-container');
            if (container) {
                container.style.display = radio.value === 'yes' ? 'block' : 'none';
            }
        };
    }
    
    if (typeof window.toggleProhibitedSector !== 'function') {
        window.toggleProhibitedSector = function(radio) {
            const container = document.getElementById('prohibited-sector-selection');
            if (container) {
                container.style.display = radio.value === 'yes' ? 'block' : 'none';
            }
        };
    }
    
    if (typeof window.toggleEmploymentStatus !== 'function') {
        window.toggleEmploymentStatus = function(radio) {
            const employedSection = document.getElementById('employed-section');
            const unemployedSection = document.getElementById('unemployed-section');
            
            if (employedSection && unemployedSection) {
                employedSection.style.display = radio.value === 'yes' ? 'block' : 'none';
                unemployedSection.style.display = radio.value === 'yes' ? 'none' : 'block';
                
                // Gérer les attributs required
                if (radio.value === 'yes') {
                    document.querySelectorAll('#employed-section input[type="radio"][name="listening-reason"]').forEach(input => {
                        input.setAttribute('required', '');
                    });
                    document.getElementById('notice-period')?.setAttribute('required', '');
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
                    document.getElementById('notice-period')?.removeAttribute('required');
                    document.querySelectorAll('#employed-section input[type="radio"][name="notice-negotiable"]').forEach(input => {
                        input.removeAttribute('required');
                    });
                }
            }
        };
    }
  }

  /**
   * Transforme les données du format backend (parsing CV) au format du formulaire
   */
  function transformCvDataToFormData() {
    if (!parsedData) {
      console.warn("Données invalides pour la transformation");
      return;
    }

    // Vérifier si nous avons un format de données brutes ou déjà transformées
    if (parsedData.personalInfo) {
      console.log("Les données sont déjà au format du formulaire");
      return; // Pas besoin de transformer
    }

    // Vérifier si nous avons des données du CV parser au format différent
    let cvData;
    if (parsedData.data) {
      cvData = parsedData.data;
      console.log("Données CV détectées au format backend standard");
    } else if (parsedData.fullData) {
      // Nouveau format du DataTransferService
      cvData = parsedData.fullData.data || parsedData.fullData;
      console.log("Données CV détectées au format DataTransferService");
    } else {
      // Si nous avons reçu directement un objet de données JSON du localStorage
      cvData = parsedData;
      console.log("Données CV détectées au format objet direct");
    }

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
    
    // Préserver le marqueur de données simulées s'il existe
    if (parsedData.isSimulated) {
      formData.isSimulated = true;
    }

    // Remplir les informations personnelles
    if (cvData.personal_info) {
      formData.personalInfo.fullName = cvData.personal_info.name || "";
      // Ajouter l'adresse si disponible
      if (cvData.personal_info.address) {
        formData.mobility.address = cvData.personal_info.address;
      }
    } else if (cvData.name) {
      // Format alternatif
      formData.personalInfo.fullName = cvData.name || "";
    }

    // Remplir le poste souhaité (avec plus de sources possibles)
    if (parsedData.current_position) {
      formData.personalInfo.jobTitle = parsedData.current_position;
    } else if (cvData.current_position) {
      formData.personalInfo.jobTitle = cvData.current_position;
    } else if (cvData.jobTitle) {
      // Format alternatif
      formData.personalInfo.jobTitle = cvData.jobTitle;
    } else if (cvData.work_experience && cvData.work_experience.length > 0) {
      // Utiliser le titre du poste le plus récent comme fallback
      formData.personalInfo.jobTitle = cvData.work_experience[0].title || "";
    } else if (cvData.position) {
      // Format direct
      formData.personalInfo.jobTitle = cvData.position;
    } else if (cvData.experience && cvData.experience.length > 0) {
      // Format alternatif pour l'expérience
      formData.personalInfo.jobTitle = cvData.experience[0].title || "";
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
    const effectivePosition = formData.personalInfo.jobTitle.toLowerCase();
    if (effectivePosition) {
      for (const [key, value] of Object.entries(positionToSalaryMap)) {
        if (effectivePosition.includes(key)) {
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
    const workExperience = cvData.work_experience || cvData.experience || [];
    if (workExperience && workExperience.length > 0) {
      const latestExperience = workExperience[0]; // Supposé être la plus récente
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

    if (workExperience && workExperience.length > 0) {
      const allExperienceText = workExperience.map(exp => 
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
    const languages = cvData.languages || [];
    if (languages && languages.length > 1) {
      const hasAdvancedEnglish = languages.some(lang => {
        const langName = lang.language || "";
        const langLevel = lang.level || "";
        return langName.toLowerCase().includes("anglais") && 
               ["courant", "bilingue", "c1", "c2"].some(level => 
                 langLevel.toLowerCase().includes(level));
      });

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

    const software = cvData.software || cvData.softwares || [];
    if (software && software.length > 0) {
      const detectedSectors = new Set();
      
      for (const sw of software) {
        const softwareLower = typeof sw === 'string' ? sw.toLowerCase() : '';
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
    console.log("Transformation des données terminée:", parsedData);
  }

  /**
   * Ajoute un indicateur visuel pour les données simulées/mockées
   */
  function addSimulatedDataIndicator() {
    // Vérifier si l'indicateur existe déjà
    if (document.querySelector('.demo-mode-indicator')) {
      return;
    }
    
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
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
      
      // Ajouter un badge sur les champs pré-remplis
      setTimeout(() => {
        const filledFields = document.querySelectorAll('input[type="text"]:not([value=""]), textarea:not(:empty)');
        filledFields.forEach(field => {
          // Ajouter un badge uniquement si le champ n'en a pas déjà un
          if (!field.parentElement.querySelector('.simulated-data-badge')) {
            const wrapper = document.createElement('div');
            wrapper.style.position = 'relative';
            wrapper.style.display = 'inline-block';
            wrapper.style.width = '100%';
            
            // Déplacer le champ dans le wrapper
            field.parentNode.insertBefore(wrapper, field);
            wrapper.appendChild(field);
            
            // Créer le badge
            const badge = document.createElement('span');
            badge.className = 'simulated-data-badge';
            badge.textContent = 'Demo';
            badge.style.position = 'absolute';
            badge.style.top = '-8px';
            badge.style.right = '0';
            badge.style.backgroundColor = 'var(--purple)';
            badge.style.color = 'white';
            badge.style.fontSize = '10px';
            badge.style.padding = '2px 6px';
            badge.style.borderRadius = '10px';
            badge.style.fontWeight = 'bold';
            badge.style.zIndex = '1';
            
            wrapper.appendChild(badge);
          }
        });
      }, 500);
    }
  }

  /**
   * Remplit tous les champs du formulaire avec les données disponibles
   */
  function fillForm() {
    if (!parsedData) {
      console.warn("Aucune donnée disponible pour le pré-remplissage");
      return;
    }
    
    const formElement = document.getElementById('questionnaire-form');
    if (!formElement) {
      console.warn("Formulaire non trouvé dans le DOM");
      return;
    }

    console.log("Début du pré-remplissage du formulaire avec les données:", parsedData);
    
    // Vérifier si les données sont simulées
    const isSimulatedData = parsedData.isSimulated === true || IS_DEMO_ENV;
    if (isSimulatedData) {
      console.log("Les données sont marquées comme simulées - ajout d'indicateurs visuels");
    }

    try {
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
          setTimeout(() => {
            if (parsedData.mobility.commuteTimes) {
              Object.keys(parsedData.mobility.commuteTimes).forEach(transportType => {
                const commuteTime = parsedData.mobility.commuteTimes[transportType];
                setSelectValue(`commute-time-${transportType}`, commuteTime);
              });
            }
          }, 100); // Petit délai pour s'assurer que les éléments sont créés
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
          const container = document.getElementById('other-motivation-container');
          if (container) {
            container.style.display = 'block';
          }
        }

        // Cocher les types de structure
        if (parsedData.motivations.structureTypes && Array.isArray(parsedData.motivations.structureTypes)) {
          parsedData.motivations.structureTypes.forEach(type => {
            setCheckboxValue('structure-type', type, true);
          });
        }

        // Définir la préférence de secteur
        if (typeof parsedData.motivations.hasSectorPreference !== 'undefined') {
          setRadioValue('has-sector-preference', parsedData.motivations.hasSectorPreference ? 'yes' : 'no');
          
          // Appel de la fonction de toggle avec un objet simulant le radio
          if (typeof window.toggleSectorPreference === 'function') {
            window.toggleSectorPreference({ value: parsedData.motivations.hasSectorPreference ? 'yes' : 'no' });
          }

          // Sélectionner les secteurs préférés si la préférence est oui
          if (parsedData.motivations.hasSectorPreference && 
              parsedData.motivations.preferredSectors && 
              Array.isArray(parsedData.motivations.preferredSectors)) {
            setTimeout(() => {
              setMultiSelectValues('sector-preference', parsedData.motivations.preferredSectors);
            }, 100);
          }

          // Définir les secteurs prohibés
          if (typeof parsedData.motivations.hasProhibitedSectors !== 'undefined') {
            setRadioValue('has-prohibited-sector', parsedData.motivations.hasProhibitedSectors ? 'yes' : 'no');
            
            if (typeof window.toggleProhibitedSector === 'function') {
              window.toggleProhibitedSector({ value: parsedData.motivations.hasProhibitedSectors ? 'yes' : 'no' });
            }

            // Sélectionner les secteurs prohibés
            if (parsedData.motivations.hasProhibitedSectors && 
                parsedData.motivations.prohibitedSectors && 
                Array.isArray(parsedData.motivations.prohibitedSectors)) {
              setTimeout(() => {
                setMultiSelectValues('prohibited-sector', parsedData.motivations.prohibitedSectors);
              }, 100);
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
        if (typeof parsedData.availability.currentlyEmployed !== 'undefined') {
          setRadioValue('currently-employed', parsedData.availability.currentlyEmployed ? 'yes' : 'no');
          
          if (typeof window.toggleEmploymentStatus === 'function') {
            window.toggleEmploymentStatus({ value: parsedData.availability.currentlyEmployed ? 'yes' : 'no' });
          }

          if (parsedData.availability.currentlyEmployed) {
            // Remplir les informations pour les candidats en poste
            if (parsedData.availability.listeningReason) {
              setTimeout(() => {
                setRadioValue('listening-reason', parsedData.availability.listeningReason);
              }, 100);
            }

            if (parsedData.availability.noticePeriod) {
              setTimeout(() => {
                setSelectValue('notice-period', parsedData.availability.noticePeriod);
              }, 100);
            }

            if (parsedData.availability.noticeNegotiable !== null) {
              setTimeout(() => {
                const noticeValue = parsedData.availability.noticeNegotiable === null ? 'unknown' : 
                                  (parsedData.availability.noticeNegotiable ? 'yes' : 'no');
                setRadioValue('notice-negotiable', noticeValue);
              }, 100);
            }
          } else {
            // Remplir les informations pour les candidats non en poste
            if (parsedData.availability.contractEndReason) {
              setTimeout(() => {
                setRadioValue('contract-end-reason', parsedData.availability.contractEndReason);
              }, 100);
            }
          }
        }

        // Définir l'état du processus de recrutement
        if (parsedData.availability.recruitmentStatus) {
          setRadioValue('recruitment-status', parsedData.availability.recruitmentStatus);
        }
      }

      console.log("Pré-remplissage du formulaire terminé avec succès");
      
      // Ajouter un indicateur visuel pour les données simulées si nécessaire
      if (isSimulatedData) {
        addSimulatedDataIndicator();
      }
      
      // Afficher une notification pour informer l'utilisateur
      if (window.showNotification) {
        if (isSimulatedData) {
          window.showNotification("Formulaire pré-rempli avec des données d'exemple (mode démo)", "info");
        } else {
          window.showNotification("Formulaire pré-rempli avec vos informations", "success");
        }
      }
    } catch (error) {
      console.error("Erreur lors du pré-remplissage du formulaire:", error);
      if (window.showNotification) {
        window.showNotification("Une erreur est survenue lors du pré-remplissage", "error");
      }
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
      console.log(`Champ '${id}' rempli avec: ${value}`);
    } else {
      console.warn(`Élément '${id}' non trouvé dans le DOM`);
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
      console.log(`Radio '${name}' défini sur: ${value}`);
    } else {
      console.warn(`Radio '${name}' avec valeur '${value}' non trouvé dans le DOM`);
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
      console.log(`Checkbox '${name}[${value}]' défini sur: ${checked}`);
    } else {
      console.warn(`Checkbox '${name}' avec valeur '${value}' non trouvé dans le DOM`);
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
      console.log(`Select '${id}' défini sur: ${value}`);
    } else {
      console.warn(`Select '${id}' non trouvé dans le DOM`);
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
        } else {
          console.warn(`Option '${value}' non trouvée dans le select '${id}'`);
        }
      });
      
      // Simuler un événement de changement
      const event = new Event('change', { bubbles: true });
      select.dispatchEvent(event);
      console.log(`MultiSelect '${id}' défini avec les valeurs:`, values);
    } else {
      console.warn(`MultiSelect '${id}' non trouvé dans le DOM ou valeurs invalides`);
    }
  }

  /**
   * Réorganise les éléments de motivation selon l'ordre spécifié
   */
  function reorderMotivations(order) {
    const motivationsList = document.getElementById('motivation-priorities');
    if (!motivationsList || !Array.isArray(order)) {
      console.warn("Liste des motivations non trouvée ou ordre invalide");
      return;
    }

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
      } else {
        console.warn(`Élément de motivation avec valeur '${value}' non trouvé`);
      }
    });
    
    // Mettre à jour le champ caché avec l'ordre actuel
    const motivationOrderInput = document.getElementById('motivation-order');
    if (motivationOrderInput) {
      motivationOrderInput.value = order.join(',');
      
      // Mettre à jour l'affichage du champ "Autre" selon la position
      const otherIndex = order.indexOf('other');
      if (otherIndex < 3) {
        const otherContainer = document.getElementById('other-motivation-container');
        if (otherContainer) {
          otherContainer.style.display = 'block';
        }
        const otherInput = document.getElementById('other-motivation');
        if (otherInput) {
          otherInput.setAttribute('required', '');
        }
      }
    }

    console.log(`Motivations réorganisées selon l'ordre:`, order);
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
      console.log("Événement déclenché pour les moyens de transport");
    } else {
      console.warn("Aucun moyen de transport coché trouvé");
    }
  }

  // Exposer les fonctions publiques
  return {
    initialize: initialize,
    fillForm: fillForm,
    isDemo: IS_DEMO_ENV
  };
})();

/**
 * Lorsque le DOM est chargé, nous vérifions s'il y a des données 
 * disponibles pour le pré-remplissage automatique.
 */
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM chargé - Vérification des données pour le pré-remplissage");
  
  // Détecter l'environnement
  const IS_DEMO_ENV = window.location.hostname.includes('github.io') || 
                      window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1';
  
  // Vérifier si l'adaptateur API est disponible
  if (IS_DEMO_ENV && !window.ApiAdapter && !document.querySelector('script[src*="api-adapter.js"]')) {
    console.log("Chargement automatique de l'adaptateur API pour l'environnement démo");
    const script = document.createElement('script');
    script.src = "../static/scripts/api-adapter.js";
    script.onload = function() {
      console.log("Adaptateur API chargé avec succès");
      initFormPrefiller();
    };
    document.head.appendChild(script);
  } else {
    initFormPrefiller();
  }
  
  function initFormPrefiller() {
    // Vérifier si l'URL contient des paramètres GET pour récupérer les données
    const urlParams = new URLSearchParams(window.location.search);
    const dataId = urlParams.get('parsed_data_id');
    
    if (dataId) {
      console.log(`ID de données parsées trouvé: ${dataId}`);
      
      // Vérifier si l'adaptateur API est disponible
      if (window.ApiAdapter) {
        console.log("Utilisation de l'adaptateur API pour récupérer les données");
        window.ApiAdapter.get(`/parsed_data/${dataId}`)
          .then(data => {
            console.log("Données récupérées avec succès via adaptateur");
            // Initialiser le pré-remplissage avec les données récupérées
            window.FormPrefiller.initialize(data);
          })
          .catch(error => {
            console.error("Erreur lors du chargement des données via adaptateur:", error);
            tryLocalStorageFallback();
          });
      } else {
        // Méthode traditionnelle
        fetch(`../api/parsed_data/${dataId}`)
          .then(response => {
            if (!response.ok) {
              throw new Error('Erreur lors de la récupération des données');
            }
            return response.json();
          })
          .then(data => {
            console.log("Données récupérées avec succès depuis l'API");
            // Initialiser le pré-remplissage avec les données récupérées
            window.FormPrefiller.initialize(data);
          })
          .catch(error => {
            console.error("Erreur lors du chargement des données parsées:", error);
            // En cas d'erreur, essayer de récupérer depuis le stockage local
            tryLocalStorageFallback();
          });
      }
    } else {
      console.log("Aucun ID de données trouvé dans l'URL - Vérification des stockages locaux");
      tryLocalStorageFallback();
    }
  }
  
  // Fonction pour tenter de récupérer les données depuis le stockage local
  function tryLocalStorageFallback() {
    try {
      // Tableau des clés à vérifier dans l'ordre de priorité
      const storageSources = [
        { type: 'localStorage', key: 'parsedCvData' },
        { type: 'sessionStorage', key: 'parsedCvData' },
        { type: 'localStorage', key: 'parsedCandidateData' },
        { type: 'sessionStorage', key: 'parsedCandidateData' }
      ];
      
      let storedData = null;
      let sourceFound = null;
      
      // Parcourir toutes les sources possibles jusqu'à trouver des données
      for (const source of storageSources) {
        const data = window[source.type].getItem(source.key);
        if (data) {
          storedData = data;
          sourceFound = `${source.type}.${source.key}`;
          break;
        }
      }
      
      if (storedData) {
        console.log(`Données trouvées dans ${sourceFound}:`, storedData.substring(0, 100) + "...");
        
        try {
          const parsedData = JSON.parse(storedData);
          
          // Marquer comme données simulées en mode démo
          if (IS_DEMO_ENV && !parsedData.isSimulated) {
            parsedData.isSimulated = true;
          }
          
          window.FormPrefiller.initialize(parsedData);
        } catch (parseError) {
          console.error("Erreur lors du parsing des données stockées:", parseError);
          
          // En mode démo, essayer de charger les données d'exemple
          if (IS_DEMO_ENV) {
            loadExampleData();
          }
        }
      } else {
        console.log("Aucune donnée trouvée dans les stockages locaux");
        
        // Si en mode démo, utiliser les données d'exemple
        if (IS_DEMO_ENV) {
          loadExampleData();
        } else {
          // Si aucune donnée n'est trouvée, vérifier si DataTransferService est disponible
          if (window.DataTransferService && typeof window.DataTransferService.prefillEssentialFields === 'function') {
            console.log("Tentative de pré-remplissage avec DataTransferService");
            window.DataTransferService.prefillEssentialFields();
          }
        }
      }
    } catch (error) {
      console.warn("Erreur lors de la récupération des données:", error);
      
      // En mode démo, charger les données d'exemple en dernier recours
      if (IS_DEMO_ENV) {
        loadExampleData();
      }
    }
  }
  
  // Fonction pour charger les données d'exemple en mode démo
  function loadExampleData() {
    console.log("Chargement des données d'exemple pour le mode démo");
    const script = document.createElement('script');
    script.src = "../static/scripts/parsed-data-example.js";
    script.onload = function() {
      if (typeof mockParsedData !== 'undefined') {
        console.log("Données d'exemple chargées avec succès");
        mockParsedData.isSimulated = true;
        window.FormPrefiller.initialize(mockParsedData);
      } else {
        console.error("Impossible de charger les données d'exemple");
      }
    };
    document.head.appendChild(script);
  }
});