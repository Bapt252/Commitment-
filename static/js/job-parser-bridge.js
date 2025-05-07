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
                    setTimeout(() => {
                        jobParserModal.classList.remove('active');
                        document.body.style.overflow = '';
                    }, 1500); // Délai pour permettre à l'utilisateur de voir que l'analyse est terminée
                }
                
                // Afficher une notification
                if (window.showNotification) {
                    window.showNotification('Les informations du poste ont été extraites avec succès !', 'success');
                }
            }
        });
        
        // Fonction pour mettre à jour l'affichage des informations du poste
        function updateJobDisplay(jobData) {
            if (!jobData) {
                console.error('No job data provided to updateJobDisplay');
                return;
            }
            
            console.log('Updating job display with data:', jobData);
            
            const jobTitleValue = document.getElementById('job-title-value');
            const jobSkillsValue = document.getElementById('job-skills-value');
            const jobExperienceValue = document.getElementById('job-experience-value');
            const jobContractValue = document.getElementById('job-contract-value');
            const jobInfoContainer = document.getElementById('job-info-container');
            
            // Rendre le conteneur visible
            if (jobInfoContainer) {
                jobInfoContainer.style.display = 'block';
                // Ajouter la classe visible si elle est utilisée
                jobInfoContainer.classList.add('visible');
            }
            
            // Mettre à jour les valeurs
            if (jobTitleValue) {
                jobTitleValue.textContent = jobData.title || '-';
                console.log('Updated job title to:', jobData.title || '-');
            } else {
                console.warn('job-title-value element not found');
            }
            
            if (jobSkillsValue) {
                if (jobData.skills && jobData.skills.length > 0) {
                    const skillsHtml = jobData.skills.map(skill => 
                        `<span class="skill-tag">${skill}</span>`
                    ).join(' ');
                    jobSkillsValue.innerHTML = skillsHtml;
                    console.log('Updated job skills with HTML tags');
                } else {
                    jobSkillsValue.textContent = '-';
                    console.log('No skills to display');
                }
            } else {
                console.warn('job-skills-value element not found');
            }
            
            if (jobExperienceValue) {
                jobExperienceValue.textContent = jobData.experience || '-';
                console.log('Updated job experience to:', jobData.experience || '-');
            } else {
                console.warn('job-experience-value element not found');
            }
            
            if (jobContractValue) {
                jobContractValue.textContent = jobData.contract || '-';
                console.log('Updated job contract to:', jobData.contract || '-');
            } else {
                console.warn('job-contract-value element not found');
            }
            
            // Pré-remplir d'autres champs du formulaire
            if (jobData.contract) {
                const contractTypeField = document.getElementById('contract-type');
                if (contractTypeField) {
                    contractTypeField.value = jobData.contract;
                    console.log('Pre-filled contract-type field with:', jobData.contract);
                }
            }
            
            // Tenter de mapper l'expérience à un niveau prédéfini
            if (jobData.experience) {
                const experienceField = document.getElementById('required-experience');
                if (experienceField) {
                    const expText = jobData.experience.toLowerCase();
                    
                    if (expText.includes('junior') || expText.includes('débutant')) {
                        experienceField.value = 'junior';
                    } else if (expText.includes('2') || expText.includes('3')) {
                        experienceField.value = '2-3years';
                    } else if (expText.includes('5') || (expText.includes('10') && !expText.includes('10+'))) {
                        experienceField.value = '5-10years';
                    } else if (expText.includes('10+') || expText.includes('senior')) {
                        experienceField.value = '10+years';
                    }
                    console.log('Mapped experience to dropdown value');
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
                try {
                    window.parent.postMessage(data, '*');
                    console.log('Message sent to parent successfully');
                    return true;
                } catch (e) {
                    console.error('Error sending message to parent:', e);
                    return false;
                }
            }
            console.warn('Parent window not accessible');
            return false;
        };
        
        // Fonction pour tester la communication
        window.testParentCommunication = function() {
            console.log('Testing communication with parent window');
            return window.sendToParent({
                type: 'testCommunication',
                message: 'Hello from iframe!',
                timestamp: new Date().toISOString()
            });
        };
        
        // Test de communication automatique après un court délai
        setTimeout(() => {
            console.log('Running automatic communication test...');
            window.testParentCommunication();
        }, 1500);
        
        // Vérifier si le parent est accessible
        try {
            if (window.parent && window.parent !== window) {
                console.log('Parent window is accessible');
                
                // Écouter les messages du parent
                window.addEventListener('message', function(event) {
                    console.log('Iframe received message:', event.data);
                    
                    // Si le parent demande un test, répondre
                    if (event.data && event.data.type === 'testCommunication') {
                        window.sendToParent({
                            type: 'testResponse',
                            message: 'Iframe received your message',
                            originalMessage: event.data.message,
                            timestamp: new Date().toISOString()
                        });
                    }
                });
                
                // Notifier le parent que l'iframe est prête
                window.sendToParent({
                    type: 'iframeReady',
                    message: 'Iframe is loaded and ready',
                    timestamp: new Date().toISOString()
                });
            }
        } catch (e) {
            console.error('Unable to access parent window:', e);
        }
        
        // Capture les événements d'analyse pour les envoyer au parent
        document.addEventListener('analysisComplete', function(e) {
            if (e.detail && e.detail.data) {
                console.log('Analysis complete event captured with data:', e.detail.data);
                
                // Standardiser le format des données pour la communication
                const jobData = {
                    title: e.detail.data.title || '',
                    skills: e.detail.data.required_skills || [],
                    experience: e.detail.data.experience || '',
                    contract: e.detail.data.contract_type || ''
                };
                
                // Envoyer les données au parent
                window.sendToParent({
                    type: 'jobParsingResult',
                    jobData: jobData,
                    messageId: new Date().getTime()
                });
            }
        });
    }
    
    console.log('Job parser bridge ready');
});
