/**
 * Script pour le formulaire candidat qui gère l'analyse des réponses
 * et s'assure que le pre-remplissage des champs fonctionne correctement.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Script d'analyse du questionnaire candidat chargé");
    
    // Vérifier si le formulaire existe
    const form = document.getElementById('questionnaire-form');
    if (!form) {
        console.error("Formulaire non trouvé");
        return;
    }
    
    // S'assurer que les fonctions de toggle sont définies au niveau global
    // pour être utilisées par le FormPrefiller
    ensureGlobalToggleFunctionsExist();
    
    // Gérer la soumission du formulaire
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (validateAllSteps()) {
                submitForm();
            }
        });
    }
    
    // Vérifier les données parsées et les appliquer si disponibles
    checkAndApplyParsedData();
});

/**
 * S'assure que les fonctions de toggle nécessaires sont disponibles globalement
 */
function ensureGlobalToggleFunctionsExist() {
    console.log("Définition des fonctions de toggle au niveau global");
    
    // Fonction pour afficher/masquer les préférences de secteur
    window.toggleSectorPreference = function(radio) {
        const container = document.getElementById('sector-preference-container');
        if (container) {
            container.style.display = radio.value === 'yes' ? 'block' : 'none';
        }
    };
    
    // Fonction pour afficher/masquer les secteurs prohibés
    window.toggleProhibitedSector = function(radio) {
        const container = document.getElementById('prohibited-sector-selection');
        if (container) {
            container.style.display = radio.value === 'yes' ? 'block' : 'none';
        }
    };
    
    // Fonction pour afficher/masquer les sections en fonction du statut d'emploi
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

/**
 * Vérifie toutes les étapes du formulaire pour validation
 */
function validateAllSteps() {
    for (let i = 1; i <= 4; i++) {
        if (!window.validateStep(i)) {
            // Afficher l'étape qui contient des erreurs
            for (let j = 1; j <= 4; j++) {
                const formStep = document.getElementById(`form-step${j}`);
                const step = document.getElementById(`step${j}`);
                
                if (j === i) {
                    formStep.classList.add('active');
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    formStep.classList.remove('active');
                    step.classList.remove('active');
                    if (j < i) {
                        step.classList.add('completed');
                    } else {
                        step.classList.remove('completed');
                    }
                }
            }
            
            // Mettre à jour la barre de progression
            const progressValues = ['0%', '33%', '66%', '100%'];
            document.getElementById('stepper-progress').style.width = progressValues[i-1];
            
            return false;
        }
    }
    
    return true;
}

/**
 * Soumet le formulaire et redirige vers la page de résultats
 */
function submitForm() {
    // Activer l'animation de chargement
    document.getElementById('loading-overlay').classList.add('active');
    
    // Collecter toutes les données du formulaire
    const formData = new FormData(document.getElementById('questionnaire-form'));
    const candidateData = {};
    
    for (const [key, value] of formData.entries()) {
        candidateData[key] = value;
    }
    
    // Ajouter l'ordre des motivations
    candidateData['motivation-order'] = document.getElementById('motivation-order').value;
    
    // Stocker les données du candidat dans sessionStorage pour la page suivante
    sessionStorage.setItem('candidateFormData', JSON.stringify(candidateData));
    
    console.log("Données du formulaire collectées:", candidateData);
    
    // Simulation d'une requête au serveur
    setTimeout(function() {
        // Redirection vers la page de correspondance
        window.location.href = 'candidate-matching-improved.html';
    }, 2000);
}

/**
 * Vérifie si des données parsées sont disponibles et les applique au formulaire
 */
function checkAndApplyParsedData() {
    console.log("Vérification des données parsées");
    
    // Vérifier l'URL pour un ID de données parsées
    const urlParams = new URLSearchParams(window.location.search);
    const dataId = urlParams.get('parsed_data_id');
    
    if (dataId) {
        console.log(`ID de données trouvé: ${dataId}`);
        // Récupérer les données depuis l'API
        fetch(`../api/parsed_data/${dataId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de la récupération des données');
                }
                return response.json();
            })
            .then(data => {
                console.log("Données parsées récupérées:", data);
                if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                    window.FormPrefiller.initialize(data);
                } else {
                    console.warn("FormPrefiller non disponible, stockage des données pour utilisation ultérieure");
                    sessionStorage.setItem('parsedCandidateData', JSON.stringify(data));
                    
                    // Tenter de charger FormPrefiller dynamiquement
                    loadFormPrefillerScript();
                }
            })
            .catch(error => {
                console.error("Erreur lors du chargement des données parsées:", error);
            });
    } else {
        // Vérifier dans sessionStorage
        try {
            const storedData = sessionStorage.getItem('parsedCandidateData');
            if (storedData) {
                console.log("Données trouvées dans sessionStorage");
                const parsedData = JSON.parse(storedData);
                
                if (window.FormPrefiller && typeof window.FormPrefiller.initialize === 'function') {
                    window.FormPrefiller.initialize(parsedData);
                } else {
                    console.warn("FormPrefiller non disponible, tentative de chargement");
                    loadFormPrefillerScript();
                }
            } else {
                console.log("Aucune donnée parsée trouvée");
            }
        } catch (error) {
            console.error("Erreur lors de la vérification des données stockées:", error);
        }
    }
}

/**
 * Charge dynamiquement le script de pré-remplissage si nécessaire
 */
function loadFormPrefillerScript() {
    if (!document.querySelector('script[src*="form-prefiller.js"]')) {
        console.log("Chargement dynamique du script form-prefiller.js");
        const script = document.createElement('script');
        script.src = "../static/scripts/form-prefiller.js";
        script.onload = function() {
            console.log("Script form-prefiller.js chargé avec succès");
            // Tenter d'initialiser après chargement
            try {
                const storedData = sessionStorage.getItem('parsedCandidateData');
                if (storedData && window.FormPrefiller) {
                    window.FormPrefiller.initialize(JSON.parse(storedData));
                }
            } catch (error) {
                console.error("Erreur après chargement du script:", error);
            }
        };
        script.onerror = function() {
            console.error("Échec du chargement du script form-prefiller.js");
        };
        document.head.appendChild(script);
    }
}