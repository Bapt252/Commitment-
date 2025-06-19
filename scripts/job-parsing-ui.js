/**
 * Script pour activer le parsing de fiche de poste - VERSION CORRIGÉE
 * Ce script assure que la section de parsing de fiche de poste est correctement affichée
 * et initialisée lorsqu'un utilisateur indique qu'il a un besoin de recrutement.
 */

// Variable globale pour l'instance de l'API
let jobParserInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation du job parsing UI corrigé...');
    
    // Initialiser l'API de parsing
    initJobParserAPI();
    
    // Initialiser l'interface
    initJobParsingSection();
});

/**
 * Initialise l'API de parsing avec la bonne configuration
 */
function initJobParserAPI() {
    if (window.JobParserAPI) {
        console.log('✅ JobParserAPI trouvée, initialisation...');
        
        // Créer une instance avec la bonne configuration
        jobParserInstance = new window.JobParserAPI({
            apiUrl: 'http://localhost:5055/api/parse-job', // Port corrigé : 5055 au lieu de 5053
            debug: true,
            enablePDFCleaning: true
        });
        
        console.log('✅ Instance JobParserAPI créée avec succès');
    } else {
        console.error('❌ JobParserAPI non trouvée - vérifiez que job-parser-api.js est chargé');
    }
}

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
            
            // Proposer une analyse immédiate pour les PDF
            if (file.type === 'application/pdf' && jobParserInstance) {
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
            });
        }
    }
    
    // Bouton d'analyse de texte principal - CORRIGÉ
    if (analyzeButton && jobTextarea) {
        analyzeButton.addEventListener('click', function() {
            const textContent = jobTextarea.value.trim();
            
            if (textContent) {
                console.log('🔍 Analyse du texte déclenchée...');
                parseJobText(textContent);
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
    
    // Fonction pour analyser le texte - VERSION CORRIGÉE
    function parseJobText(text) {
        console.log("🔍 Début de l'analyse du texte...");
        console.log("📝 Longueur du texte:", text.length);
        
        // Afficher l'indicateur de chargement
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'flex';
        
        // Utiliser l'instance correcte de l'API
        if (jobParserInstance) {
            console.log("✅ Utilisation de l'API JobParser...");
            
            jobParserInstance.parseJobText(text)
                .then(result => {
                    console.log("✅ Analyse terminée avec succès:", result);
                    
                    // Sauvegarder les résultats
                    sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                    
                    // Afficher les résultats
                    showJobResults(result);
                    
                    // Cacher le loader
                    if (loader) loader.style.display = 'none';
                    
                    showNotification('🎯 Analyse terminée ! Les informations ont été extraites avec succès.', 'success');
                })
                .catch(error => {
                    console.error("❌ Erreur lors de l'analyse:", error);
                    showNotification("Une erreur est survenue lors de l'analyse. Veuillez réessayer.", 'error');
                    
                    // Cacher le loader
                    if (loader) loader.style.display = 'none';
                });
        } else {
            console.warn("⚠️ API de parsing non initialisée, utilisation du fallback");
            
            // Fallback amélioré avec des données plus réalistes
            setTimeout(() => {
                const result = {
                    title: "Poste à analyser",
                    company: "",
                    location: "À déterminer",
                    contract_type: "À préciser",
                    skills: ["Analyse en cours..."],
                    experience: "À définir selon le poste",
                    education: "",
                    salary: "Selon profil",
                    responsibilities: ["Responsabilités en cours d'extraction..."],
                    benefits: []
                };
                
                // Sauvegarder les résultats
                sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                
                // Afficher les résultats
                showJobResults(result);
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
                
                showNotification('⚠️ Analyse fallback utilisée. Pour une analyse complète, vérifiez que l\'API backend est démarrée.', 'info');
            }, 1500);
        }
    }
    
    // Fonction pour analyser un fichier - VERSION CORRIGÉE
    function parseJobFile(file) {
        console.log("📄 Début de l'analyse du fichier:", file.name);
        
        // Afficher l'indicateur de chargement
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'flex';
        
        // Utiliser l'instance correcte de l'API
        if (jobParserInstance) {
            console.log("✅ Utilisation de l'API JobParser pour fichier...");
            
            jobParserInstance.parseJobFile(file)
                .then(result => {
                    console.log("✅ Analyse de fichier terminée avec succès:", result);
                    
                    // Sauvegarder les résultats
                    sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                    
                    // Afficher les résultats
                    showJobResults(result);
                    
                    // Cacher le loader
                    if (loader) loader.style.display = 'none';
                    
                    showNotification('🎯 Analyse de fichier terminée ! Les informations ont été extraites avec succès.', 'success');
                })
                .catch(error => {
                    console.error("❌ Erreur lors de l'analyse du fichier:", error);
                    showNotification("Une erreur est survenue lors de l'analyse du fichier. Veuillez réessayer.", 'error');
                    
                    // Cacher le loader
                    if (loader) loader.style.display = 'none';
                });
        } else {
            console.warn("⚠️ API de parsing non initialisée, utilisation du fallback");
            
            // Fallback pour fichier
            setTimeout(() => {
                const result = {
                    title: `Poste extrait de ${file.name}`,
                    company: "",
                    location: "À déterminer",
                    contract_type: "À préciser",
                    skills: ["Analyse en cours..."],
                    experience: "À définir selon le fichier",
                    education: "",
                    salary: "Selon profil",
                    responsibilities: ["Responsabilités en cours d'extraction..."],
                    benefits: []
                };
                
                // Sauvegarder les résultats
                sessionStorage.setItem('parsedJobData', JSON.stringify(result));
                
                // Afficher les résultats
                showJobResults(result);
                
                // Cacher le loader
                if (loader) loader.style.display = 'none';
                
                showNotification('⚠️ Analyse fallback utilisée. Pour une analyse complète, vérifiez que l\'API backend est démarrée.', 'info');
            }, 1500);
        }
    }
}

/**
 * Affiche les résultats d'analyse dans l'interface
 * @param {Object} data - Les résultats de l'analyse
 */
function showJobResults(data) {
    console.log("📊 Affichage des résultats d'analyse:", data);
    
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
    if (jobInfoContainer) {
        jobInfoContainer.style.display = 'block';
        // Animation d'apparition
        jobInfoContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
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
            ul.style.marginLeft = '20px';
            data.responsibilities.forEach(resp => {
                const li = document.createElement('li');
                li.textContent = resp;
                li.style.marginBottom = '5px';
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
            ul.style.marginLeft = '20px';
            data.benefits.forEach(benefit => {
                const li = document.createElement('li');
                li.textContent = benefit;
                li.style.marginBottom = '5px';
                ul.appendChild(li);
            });
            jobBenefitsValue.appendChild(ul);
        } else if (typeof data.benefits === 'string' && data.benefits) {
            jobBenefitsValue.textContent = data.benefits;
        } else {
            jobBenefitsValue.textContent = 'Non spécifié';
        }
    }
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
        const notificationDiv = document.createElement('div');
        notificationDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 9999;
            max-width: 400px;
            font-size: 14px;
        `;
        notificationDiv.textContent = message;
        document.body.appendChild(notificationDiv);
        
        setTimeout(() => {
            document.body.removeChild(notificationDiv);
        }, 5000);
    }
}

// Exposer les fonctions utiles
window.JobParsingUI = {
    showJobResults,
    jobParserInstance: () => jobParserInstance
};

console.log('✅ Job Parsing UI corrigé chargé avec succès');
