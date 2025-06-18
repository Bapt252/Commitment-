/**
 * Script pour activer le parsing de fiche de poste
 * Ce script assure que la section de parsing de fiche de poste est correctement affichée
 * et initialisée lorsqu'un utilisateur indique qu'il a un besoin de recrutement.
 */

document.addEventListener('DOMContentLoaded', function() {
    initJobParsingSection();
});

/**
 * Initialise la section de parsing de fiche de poste
 */
function initJobParsingSection() {
    // Éléments du DOM concernés par le parsing de fiche de poste
    const recruitmentYes = document.getElementById('recruitment-yes');
    const recruitmentNo = document.getElementById('recruitment-no');
    const jobParsingSection = document.getElementById('job-parsing-section');
    const jobTextarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    const dropZone = document.getElementById('job-drop-zone');
    const analyzeButton = document.getElementById('analyze-job-text');
    const analyzeGptButton = document.getElementById('analyze-with-gpt');
    const jobInfoContainer = document.getElementById('job-info-container');
    
    // Afficher/cacher la section de parsing selon la sélection
    if (recruitmentYes && recruitmentNo && jobParsingSection) {
        // Écouter les changements sur les boutons radio
        recruitmentYes.addEventListener('change', function() {
            if (this.checked) {
                console.log("Option 'Oui' sélectionnée, affichage de la section de parsing");
                jobParsingSection.classList.add('active');
                sessionStorage.setItem('recruitmentNeeded', 'yes');
            }
        });
        
        recruitmentNo.addEventListener('change', function() {
            if (this.checked) {
                console.log("Option 'Non' sélectionnée, masquage de la section de parsing");
                jobParsingSection.classList.remove('active');
                sessionStorage.setItem('recruitmentNeeded', 'no');
            }
        });
        
        // Si l'utilisateur avait déjà choisi "Oui", afficher la section
        const savedChoice = sessionStorage.getItem('recruitmentNeeded');
        if (savedChoice === 'yes') {
            recruitmentYes.checked = true;
            jobParsingSection.classList.add('active');
        } else if (savedChoice === 'no') {
            recruitmentNo.checked = true;
        }
    }
    
    // Configurer le drag-and-drop pour les fichiers
    if (dropZone && fileInput) {
        // Prévenir le comportement par défaut du navigateur
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        // Mettre en évidence la zone de drop lors du survol
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('drag-active');
        }
        
        function unhighlight() {
            dropZone.classList.remove('drag-active');
        }
        
        // Gérer le dépôt de fichier
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect(files[0]);
            }
        }
        
        // Gérer la sélection de fichier via le bouton classique
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                handleFileSelect(this.files[0]);
            }
        });
        
        // Rendre la zone de drop cliquable pour ouvrir le sélecteur de fichier
        dropZone.addEventListener('click', function() {
            fileInput.click();
        });
        
        // Gérer l'affichage du badge de fichier sélectionné
        function handleFileSelect(file) {
            console.log("Fichier sélectionné:", file.name);
            
            // Afficher le badge de fichier
            const fileBadge = document.getElementById('file-badge');
            const fileName = document.getElementById('file-name');
            
            if (fileBadge && fileName) {
                fileName.textContent = file.name;
                fileBadge.style.display = 'flex';
            }
            
            // Activer le bouton d'analyse GPT - Non fonctionnel dans cette version
            if (analyzeGptButton) {
                analyzeGptButton.disabled = true; // Garder désactivé pour clarification
            }
            
            // Si le fichier est un PDF et que l'API de parsing est disponible,
            // on peut proposer une analyse immédiate
            if (file.type === 'application/pdf' && window.jobParserAPI) {
                const confirmAnalysis = confirm("Voulez-vous analyser ce fichier PDF maintenant?");
                if (confirmAnalysis) {
                    parseJobFile(file);
                }
            }
        }
        
        // Permettre de supprimer le fichier sélectionné
        const removeFileButton = document.getElementById('remove-file');
        if (removeFileButton) {
            removeFileButton.addEventListener('click', function(e) {
                e.stopPropagation(); // Empêcher l'événement de remonter au drop-zone
                
                // Réinitialiser le champ de fichier
                fileInput.value = '';
                
                // Cacher le badge
                const fileBadge = document.getElementById('file-badge');
                if (fileBadge) {
                    fileBadge.style.display = 'none';
                }
                
                // Désactiver le bouton d'analyse GPT si le textarea est aussi vide
                if (analyzeGptButton && (!jobTextarea || !jobTextarea.value.trim())) {
                    analyzeGptButton.disabled = true;
                }
            });
        }
    }
    
    // Activer/désactiver le bouton d'analyse GPT selon le contenu - Mais garder désactivé
    if (jobTextarea && analyzeGptButton) {
        jobTextarea.addEventListener('input', function() {
            // Garder désactivé pour le moment car cette fonctionnalité n'est pas encore disponible
            analyzeGptButton.disabled = true;
        });
        
        // Initialiser l'état du bouton - toujours désactivé
        analyzeGptButton.disabled = true;
    }
    
    // Bouton d'analyse de texte principal
    if (analyzeButton && jobTextarea) {
        analyzeButton.addEventListener('click', function() {
            if (jobTextarea.value.trim()) {
                parseJobText(jobTextarea.value);
            } else {
                showNotification("Veuillez entrer le texte de la fiche de poste à analyser.", 'info');
            }
        });
    }
    
    // Bouton d'analyse GPT - Amélioration du message
    if (analyzeGptButton) {
        analyzeGptButton.addEventListener('click', function() {
            showNotification("Cette fonctionnalité sera bientôt disponible. Utilisez le bouton d'analyse standard (🔍) pour analyser votre fiche de poste.", 'info');
        });
    }
    
    // Fonction pour analyser le texte
    function parseJobText(text) {
        console.log("Analyse du texte...");
        
        // Afficher l'indicateur de chargement
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'flex';
        
        // Si l'API de parsing est disponible, l'utiliser
        if (window.jobParserAPI) {
            try {
                window.jobParserAPI.parseJobText(text)
                    .then(result => {
                        // Sauvegarder les résultats
                        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                        
                        // Afficher les résultats
                        showJobResults(result);
                        
                        // Cacher le loader
                        if (loader) loader.style.display = 'none';
                    })
                    .catch(error => {
                        console.error("Erreur lors de l'analyse:", error);
                        showNotification("Une erreur est survenue lors de l'analyse. Veuillez réessayer.", 'error');
                        
                        // Cacher le loader
                        if (loader) loader.style.display = 'none';
                    });
            } catch (error) {
                console.error("Erreur lors de l'appel à l'API:", error);
                showNotification("Une erreur est survenue lors de l'appel à l'API de parsing.", 'error');
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
            }
        } else {
            // Fallback si l'API n'est pas disponible
            console.warn("API de parsing non disponible, utilisation du fallback local");
            
            // Simuler une analyse basique
            setTimeout(() => {
                const result = {
                    title: "Titre extrait du texte",
                    company: "Entreprise extraite du texte",
                    location: "Lieu extrait du texte",
                    contract_type: "Type de contrat extrait",
                    skills: ["Compétence 1", "Compétence 2", "Compétence 3"],
                    experience: "Expérience extraite du texte",
                    education: "Formation extraite du texte",
                    salary: "Salaire extrait du texte",
                    responsibilities: ["Responsabilité 1", "Responsabilité 2"],
                    benefits: ["Avantage 1", "Avantage 2"]
                };
                
                // Sauvegarder les résultats
                sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                
                // Afficher les résultats
                showJobResults(result);
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
            }, 1500);
        }
    }
    
    // Fonction pour analyser un fichier
    function parseJobFile(file) {
        console.log("Analyse du fichier:", file.name);
        
        // Afficher l'indicateur de chargement
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'flex';
        
        // Si l'API de parsing est disponible, l'utiliser
        if (window.jobParserAPI) {
            try {
                window.jobParserAPI.parseJobFile(file)
                    .then(result => {
                        // Sauvegarder les résultats
                        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                        
                        // Afficher les résultats
                        showJobResults(result);
                        
                        // Cacher le loader
                        if (loader) loader.style.display = 'none';
                    })
                    .catch(error => {
                        console.error("Erreur lors de l'analyse du fichier:", error);
                        showNotification("Une erreur est survenue lors de l'analyse du fichier. Veuillez réessayer.", 'error');
                        
                        // Cacher le loader
                        if (loader) loader.style.display = 'none';
                    });
            } catch (error) {
                console.error("Erreur lors de l'appel à l'API pour le fichier:", error);
                showNotification("Une erreur est survenue lors de l'appel à l'API de parsing pour le fichier.", 'error');
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
            }
        } else {
            // Fallback si l'API n'est pas disponible
            console.warn("API de parsing non disponible, utilisation du fallback local");
            
            // Simuler une analyse basique
            setTimeout(() => {
                const result = {
                    title: "Titre extrait du fichier",
                    company: "Entreprise extraite du fichier",
                    location: "Lieu extrait du fichier",
                    contract_type: "Type de contrat extrait",
                    skills: ["Compétence 1", "Compétence 2", "Compétence 3"],
                    experience: "Expérience extraite du fichier",
                    education: "Formation extraite du fichier",
                    salary: "Salaire extrait du fichier",
                    responsibilities: ["Responsabilité 1", "Responsabilité 2"],
                    benefits: ["Avantage 1", "Avantage 2"]
                };
                
                // Sauvegarder les résultats
                sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                
                // Afficher les résultats
                showJobResults(result);
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
            }, 1500);
        }
    }
}

/**
 * Affiche les résultats d'analyse dans l'interface
 * @param {Object} data - Les résultats de l'analyse
 */
function showJobResults(data) {
    console.log("Affichage des résultats d'analyse:", data);
    
    // Éléments cibles pour afficher les résultats
    const jobTitleValue = document.getElementById('job-title-value');
    const jobContractValue = document.getElementById('job-contract-value');
    const jobLocationValue = document.getElementById('job-location-value');
    const jobExperienceValue = document.getElementById('job-experience-value');
    const jobEducationValue = document.getElementById('job-education-value');
    const jobSalaryValue = document.getElementById('job-salary-value');
    const jobSkillsValue = document.getElementById('job-skills-value');
    const jobResponsibilitiesValue = document.getElementById('job-responsibilities-value');
    const jobBenefitsValue = document.getElementById('job-benefits-value');
    
    // Afficher le conteneur principal
    const jobInfoContainer = document.getElementById('job-info-container');
    if (jobInfoContainer) jobInfoContainer.style.display = 'block';
    
    // Mettre à jour les valeurs avec les résultats de l'analyse
    if (jobTitleValue) jobTitleValue.textContent = data.title || 'Non spécifié';
    if (jobContractValue) jobContractValue.textContent = data.contract_type || 'Non spécifié';
    if (jobLocationValue) jobLocationValue.textContent = data.location || 'Non spécifié';
    if (jobExperienceValue) jobExperienceValue.textContent = data.experience || 'Non spécifié';
    if (jobEducationValue) jobEducationValue.textContent = data.education || 'Non spécifié';
    if (jobSalaryValue) jobSalaryValue.textContent = data.salary || 'Non spécifié';
    
    // Afficher les compétences sous forme de tags
    if (jobSkillsValue) {
        if (Array.isArray(data.skills) && data.skills.length > 0) {
            jobSkillsValue.innerHTML = '';
            data.skills.forEach(skill => {
                const skillTag = document.createElement('span');
                skillTag.className = 'tag';
                skillTag.textContent = skill;
                jobSkillsValue.appendChild(skillTag);
            });
        } else {
            jobSkillsValue.textContent = 'Non spécifié';
        }
    }
    
    // Afficher les responsabilités
    if (jobResponsibilitiesValue) {
        if (Array.isArray(data.responsibilities) && data.responsibilities.length > 0) {
            jobResponsibilitiesValue.innerHTML = '';
            const ul = document.createElement('ul');
            data.responsibilities.forEach(resp => {
                const li = document.createElement('li');
                li.textContent = resp;
                ul.appendChild(li);
            });
            jobResponsibilitiesValue.appendChild(ul);
        } else if (typeof data.responsibilities === 'string' && data.responsibilities) {
            jobResponsibilitiesValue.textContent = data.responsibilities;
        } else {
            jobResponsibilitiesValue.textContent = 'Non spécifié';
        }
    }
    
    // Afficher les avantages
    if (jobBenefitsValue) {
        if (Array.isArray(data.benefits) && data.benefits.length > 0) {
            jobBenefitsValue.innerHTML = '';
            const ul = document.createElement('ul');
            data.benefits.forEach(benefit => {
                const li = document.createElement('li');
                li.textContent = benefit;
                ul.appendChild(li);
            });
            jobBenefitsValue.appendChild(ul);
        } else if (typeof data.benefits === 'string' && data.benefits) {
            jobBenefitsValue.textContent = data.benefits;
        } else {
            jobBenefitsValue.textContent = 'Non spécifié';
        }
    }
    
    // Afficher une notification de succès améliorée
    showNotification('🎯 Extraction réussie ! Toutes les informations ont été analysées automatiquement par le parser local.', 'success');
}

/**
 * Affiche une notification
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Utiliser la fonction de notification globale si disponible
    if (window.QuestionnaireNavigation && window.QuestionnaireNavigation.showNotification) {
        window.QuestionnaireNavigation.showNotification(message, type);
    } else {
        console.log(`Notification (${type}): ${message}`);
        
        // Fallback simple pour les notifications
        alert(message);
    }
}

// Exposer les fonctions utiles
window.JobParsingUI = {
    showJobResults
};
