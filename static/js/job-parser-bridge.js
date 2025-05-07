/**
 * Script de pont pour améliorer la communication entre le modal d'analyse de fiche de poste
 * et la page principale du questionnaire client.
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Job parser bridge initialized');
    
    // Éléments du DOM
    const openJobParserBtn = document.getElementById('open-job-parser');
    const closeJobParserBtn = document.getElementById('close-job-parser');
    const jobParserModal = document.getElementById('job-parser-modal');
    const jobParserIframe = document.getElementById('job-parser-iframe');
    
    // Vérifier si la page a les éléments nécessaires
    const isParentPage = openJobParserBtn && jobParserModal;
    const isIframePage = window !== window.parent;
    
    console.log('Page configuration:', { 
        isParentPage, 
        isIframePage, 
        hasOpenButton: !!openJobParserBtn,
        hasModal: !!jobParserModal 
    });
    
    // Amélioration pour la page parente (questionnaire client)
    if (isParentPage) {
        console.log('Enhancing parent page functionality');
        
        // S'assurer que l'iframe est rechargée à chaque ouverture pour éviter les problèmes de cache
        if (openJobParserBtn) {
            openJobParserBtn.addEventListener('click', function() {
                console.log('Open button clicked - refreshing iframe');
                
                // Rechargez l'iframe pour garantir un état propre
                if (jobParserIframe) {
                    // On sauvegarde le src original
                    const originalSrc = jobParserIframe.src;
                    
                    // On vide puis restaure le src pour forcer un rechargement
                    jobParserIframe.src = '';
                    setTimeout(() => {
                        jobParserIframe.src = originalSrc;
                    }, 50);
                }
            });
        }
        
        // Amélioration de l'écoute des messages depuis l'iframe
        window.addEventListener('message', function(event) {
            console.log('Parent received message:', event.data?.type);
            
            // Vérifier si c'est un message de notre iframe
            if (event.data && event.data.type === 'jobParsingResult') {
                console.log('Job parsing result received in parent:', event.data);
                
                // Traiter le résultat
                const jobData = event.data.jobData;
                
                // Mettre à jour les éléments d'affichage
                updateJobDisplay(jobData);
                
                // Fermer automatiquement le modal après traitement
                if (jobParserModal) {
                    jobParserModal.classList.remove('active');
                    document.body.style.overflow = '';
                }
                
                // Afficher une notification
                if (window.showNotification) {
                    window.showNotification('Les informations du poste ont été extraites avec succès !', 'success');
                }
            }
        });
        
        // Fonction pour mettre à jour l'affichage des informations du poste
        function updateJobDisplay(jobData) {
            if (!jobData) return;
            
            const jobTitleValue = document.getElementById('job-title-value');
            const jobSkillsValue = document.getElementById('job-skills-value');
            const jobExperienceValue = document.getElementById('job-experience-value');
            const jobContractValue = document.getElementById('job-contract-value');
            const jobInfoContainer = document.getElementById('job-info-container');
            
            // Rendre le conteneur visible
            if (jobInfoContainer) {
                jobInfoContainer.style.display = 'block';
            }
            
            // Mettre à jour les valeurs
            if (jobTitleValue) {
                jobTitleValue.textContent = jobData.title || '-';
            }
            
            if (jobSkillsValue) {
                if (jobData.skills && jobData.skills.length > 0) {
                    const skillsHtml = jobData.skills.map(skill => 
                        `<span class="skill-tag">${skill}</span>`
                    ).join(' ');
                    jobSkillsValue.innerHTML = skillsHtml;
                } else {
                    jobSkillsValue.textContent = '-';
                }
            }
            
            if (jobExperienceValue) {
                jobExperienceValue.textContent = jobData.experience || '-';
            }
            
            if (jobContractValue) {
                jobContractValue.textContent = jobData.contract || '-';
            }
            
            // Pré-remplir d'autres champs du formulaire
            if (jobData.contract) {
                const contractTypeField = document.getElementById('contract-type');
                if (contractTypeField) {
                    contractTypeField.value = jobData.contract;
                }
            }
        }
    }
    
    // Amélioration pour la page iframe (job-description-parser.html)
    if (isIframePage) {
        console.log('Enhancing iframe page functionality');
        
        // Fonction pour envoyer des données à la page parente
        window.sendToParent = function(data) {
            console.log('Sending data to parent:', data);
            if (window.parent) {
                window.parent.postMessage(data, '*');
                return true;
            }
            return false;
        };
        
        // Vérifier si le parent est accessible
        try {
            if (window.parent && window.parent !== window) {
                console.log('Parent window accessible');
            }
        } catch (e) {
            console.error('Unable to access parent window:', e);
        }
    }
    
    console.log('Job parser bridge ready');
});