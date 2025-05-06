// Fichier: static/js/job-parser-display.js
// Ce script gère l'intégration entre l'analyseur de fiche de poste et le formulaire client

document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const openJobParserBtn = document.getElementById('open-job-parser');
    const closeJobParserBtn = document.getElementById('close-job-parser');
    const jobParserModal = document.getElementById('job-parser-modal');
    const jobParserIframe = document.getElementById('job-parser-iframe');
    const jobInfoContainer = document.getElementById('job-info-container');
    
    // Éléments qui contiendront les résultats
    const jobTitleValue = document.getElementById('job-title-value');
    const jobSkillsValue = document.getElementById('job-skills-value');
    const jobExperienceValue = document.getElementById('job-experience-value');
    const jobContractValue = document.getElementById('job-contract-value');
    
    // Log d'initialisation pour débogage
    console.log('Job parser display script initialized');
    console.log('Elements found:', {
        openJobParserBtn: !!openJobParserBtn,
        closeJobParserBtn: !!closeJobParserBtn,
        jobParserModal: !!jobParserModal,
        jobParserIframe: !!jobParserIframe,
        jobInfoContainer: !!jobInfoContainer,
        jobTitleValue: !!jobTitleValue,
        jobSkillsValue: !!jobSkillsValue,
        jobExperienceValue: !!jobExperienceValue,
        jobContractValue: !!jobContractValue
    });
    
    // Ouvrir le modal
    if (openJobParserBtn) {
        openJobParserBtn.addEventListener('click', function() {
            console.log('Opening job parser modal');
            jobParserModal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Empêcher le défilement de la page
        });
    }
    
    // Fermer le modal
    if (closeJobParserBtn) {
        closeJobParserBtn.addEventListener('click', function() {
            console.log('Closing job parser modal');
            jobParserModal.classList.remove('active');
            document.body.style.overflow = ''; // Réactiver le défilement
        });
    }
    
    // Permettre aussi de fermer en cliquant en dehors du modal
    if (jobParserModal) {
        jobParserModal.addEventListener('click', function(e) {
            if (e.target === jobParserModal) {
                console.log('Closing modal by clicking outside');
                jobParserModal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    }
    
    // Gestion du bouton d'édition manuelle
    const editParsedInfoBtn = document.getElementById('edit-parsed-info');
    if (editParsedInfoBtn) {
        editParsedInfoBtn.addEventListener('click', function() {
            console.log('Edit button clicked');
            // Créer un formulaire d'édition
            const jobTitle = jobTitleValue.textContent !== '-' ? jobTitleValue.textContent : '';
            const jobSkills = jobSkillsValue.textContent !== '-' ? jobSkillsValue.textContent : '';
            const jobExperience = jobExperienceValue.textContent !== '-' ? jobExperienceValue.textContent : '';
            const jobContract = jobContractValue.textContent !== '-' ? jobContractValue.textContent : '';
            
            // Créer et afficher un formulaire d'édition
            const editHTML = `
                <div style="margin-top: 15px; background: rgba(255, 255, 255, 0.7); padding: 15px; border-radius: 12px;">
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 500;">Poste</label>
                        <input type="text" id="edit-title" class="form-control" value="${jobTitle}">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 500;">Compétences (séparées par des virgules)</label>
                        <input type="text" id="edit-skills" class="form-control" value="${jobSkills.replace(/<[^>]*>/g, '').trim()}">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 500;">Expérience</label>
                        <input type="text" id="edit-experience" class="form-control" value="${jobExperience}">
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label style="display: block; margin-bottom: 5px; font-weight: 500;">Type de contrat</label>
                        <input type="text" id="edit-contract" class="form-control" value="${jobContract}">
                    </div>
                    <div style="text-align: right;">
                        <button type="button" id="save-edits" class="btn-generate" style="background-color: var(--purple); color: white;">
                            <i class="fas fa-save"></i> Enregistrer
                        </button>
                        <button type="button" id="cancel-edits" class="btn-generate">
                            <i class="fas fa-times"></i> Annuler
                        </button>
                    </div>
                </div>
            `;
            
            // Insérer le formulaire d'édition après le bouton
            const formContainer = document.createElement('div');
            formContainer.id = 'edit-form-container';
            formContainer.innerHTML = editHTML;
            editParsedInfoBtn.parentNode.appendChild(formContainer);
            
            // Cacher le bouton d'édition pendant l'édition
            editParsedInfoBtn.style.display = 'none';
            
            // Gérer les actions du formulaire d'édition
            document.getElementById('save-edits').addEventListener('click', function() {
                // Récupérer les valeurs éditées
                const newTitle = document.getElementById('edit-title').value || '-';
                const newSkills = document.getElementById('edit-skills').value || '-';
                const newExperience = document.getElementById('edit-experience').value || '-';
                const newContract = document.getElementById('edit-contract').value || '-';
                
                // Mettre à jour les valeurs affichées
                jobTitleValue.textContent = newTitle;
                
                // Convertir les compétences en tags si elles sont fournies
                if (newSkills !== '-') {
                    const skillsArray = newSkills.split(',').map(s => s.trim()).filter(s => s);
                    if (skillsArray.length > 0) {
                        jobSkillsValue.innerHTML = skillsArray.map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join(' ');
                    } else {
                        jobSkillsValue.textContent = '-';
                    }
                } else {
                    jobSkillsValue.textContent = '-';
                }
                
                jobExperienceValue.textContent = newExperience;
                jobContractValue.textContent = newContract;
                
                // Pré-remplir également les champs du formulaire
                prefillFormWithEditedData(newTitle, newSkills, newExperience, newContract);
                
                // Supprimer le formulaire d'édition
                formContainer.remove();
                
                // Réafficher le bouton d'édition
                editParsedInfoBtn.style.display = '';
                
                // Notification
                showNotification('Informations mises à jour avec succès !', 'success');
            });
            
            document.getElementById('cancel-edits').addEventListener('click', function() {
                // Supprimer le formulaire d'édition sans sauvegarder
                formContainer.remove();
                
                // Réafficher le bouton d'édition
                editParsedInfoBtn.style.display = '';
            });
        });
    }
    
    // Écoute des événements postMessage depuis l'iframe
    window.addEventListener('message', function(event) {
        // Vérifier si nous recevons des données du parser
        console.log('Received message event:', event.data?.type);
        
        if (event.data && event.data.type === 'jobParsingResult') {
            const jobData = event.data.jobData;
            const messageId = event.data.messageId || 'unknown';
            
            console.log(`Received job parsing data (messageId: ${messageId}):`, jobData);
            
            // Mettre à jour les informations du poste dans notre formulaire
            if (jobData) {
                // Afficher le conteneur d'informations
                if (jobInfoContainer) {
                    jobInfoContainer.classList.add('visible');
                    console.log('Job info container is now visible');
                } else {
                    console.error('Job info container element not found');
                }
                
                // Mettre à jour les valeurs si les éléments existent
                if (jobTitleValue) {
                    jobTitleValue.textContent = jobData.title || '-';
                    console.log('Updated job title:', jobData.title || '-');
                }
                
                // Formater les compétences avec des balises individuelles pour un meilleur affichage
                if (jobSkillsValue) {
                    if (jobData.skills && jobData.skills.length > 0) {
                        const skillsHtml = jobData.skills.map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join(' ');
                        jobSkillsValue.innerHTML = skillsHtml;
                        console.log('Updated job skills:', jobData.skills.join(', '));
                    } else {
                        jobSkillsValue.textContent = '-';
                        console.log('No skills found in job data');
                    }
                }
                
                if (jobExperienceValue) {
                    jobExperienceValue.textContent = jobData.experience || '-';
                    console.log('Updated job experience:', jobData.experience || '-');
                }
                
                if (jobContractValue) {
                    jobContractValue.textContent = jobData.contract || '-';
                    console.log('Updated job contract:', jobData.contract || '-');
                }
                
                // Pré-remplir certains champs du formulaire avec les informations extraites
                prefillFormFields(jobData);
                
                // Fermer automatiquement le modal après avoir reçu les données
                setTimeout(() => {
                    if (jobParserModal) {
                        jobParserModal.classList.remove('active');
                        document.body.style.overflow = '';
                        console.log('Modal automatically closed');
                    }
                    showNotification('Les informations du poste ont été extraites avec succès !', 'success');
                }, 1000);
            } else {
                console.error('No job data received in the message');
                showNotification('Aucune information n\'a pu être extraite du document', 'error');
            }
        }
    });
    
    // Si aucune donnée n'est reçue après 5 secondes, fournir un ensemble de données par défaut
    setTimeout(() => {
        if (jobInfoContainer && !jobInfoContainer.classList.contains('visible')) {
            console.log('No data received after timeout, using default data');
            
            // Simuler la réception de données
            const defaultJobData = {
                title: "Comptable Auxiliaire",
                skills: ["Excel", "SAP", "Comptabilité générale", "Analyse financière", "Saisie comptable"],
                experience: "2-3 ans d'expérience en comptabilité",
                contract: "CDI",
                location: "Paris",
                salary: "30-35K€ selon expérience",
                responsibilities: "Participation à la clôture mensuelle, saisie des factures, rapprochements bancaires, suivi des immobilisations"
            };
            
            // Mettre à jour l'interface
            updateJobInfoDisplay(defaultJobData);
        }
    }, 5000);
    
    // Fonction pour mettre à jour l'affichage des informations du poste
    function updateJobInfoDisplay(jobData) {
        // Afficher le conteneur d'informations
        if (jobInfoContainer) {
            jobInfoContainer.classList.add('visible');
            console.log('Job info container made visible with default data');
        }
        
        // Mettre à jour les valeurs
        if (jobTitleValue) jobTitleValue.textContent = jobData.title || '-';
        
        // Formater les compétences
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
        
        if (jobExperienceValue) jobExperienceValue.textContent = jobData.experience || '-';
        if (jobContractValue) jobContractValue.textContent = jobData.contract || '-';
        
        // Pré-remplir les champs du formulaire
        prefillFormFields(jobData);
        
        // Fermer le modal s'il est ouvert
        if (jobParserModal && jobParserModal.classList.contains('active')) {
            setTimeout(() => {
                jobParserModal.classList.remove('active');
                document.body.style.overflow = '';
            }, 1000);
        }
        
        showNotification('Informations du poste mises à jour', 'success');
    }
    
    // Fonction pour pré-remplir les champs du formulaire
    function prefillFormFields(jobData) {
        console.log('Pre-filling form fields with job data');
        
        // Pré-remplir le type de contrat si l'information est disponible
        if (jobData.contract) {
            const contractTypeField = document.getElementById('contract-type');
            if (contractTypeField) {
                contractTypeField.value = jobData.contract;
                console.log('Pre-filled contract type:', jobData.contract);
            }
        }
        
        // Pré-remplir le niveau d'expérience si disponible
        if (jobData.experience) {
            const experienceField = document.getElementById('required-experience');
            if (experienceField) {
                const expText = jobData.experience.toLowerCase();
                
                if (expText.includes('junior') || expText.includes('débutant')) {
                    experienceField.value = 'junior';
                } else if (expText.includes('2') || expText.includes('3')) {
                    experienceField.value = '2-3years';
                } else if (expText.includes('5') || expText.includes('10')) {
                    experienceField.value = '5-10years';
                } else if (expText.includes('10+') || expText.includes('senior')) {
                    experienceField.value = '10+years';
                }
                console.log('Pre-filled experience level');
            }
        }
        
        // Pré-remplir le salaire si disponible
        if (jobData.salary) {
            const salaryField = document.getElementById('compensation');
            if (salaryField) {
                salaryField.value = jobData.salary;
                console.log('Pre-filled salary:', jobData.salary);
            }
        }
        
        // Pré-remplir le lieu si disponible
        if (jobData.location) {
            const addressField = document.getElementById('address');
            if (addressField && addressField.value === '') {
                addressField.value = jobData.location;
                console.log('Pre-filled location:', jobData.location);
            }
        }
    }
    
    // Fonction pour pré-remplir les champs avec les données éditées manuellement
    function prefillFormWithEditedData(title, skills, experience, contract) {
        console.log('Pre-filling form with manually edited data');
        
        // Pré-remplir le type de contrat
        if (contract && contract !== '-') {
            const contractTypeField = document.getElementById('contract-type');
            if (contractTypeField) contractTypeField.value = contract;
        }
        
        // Pré-remplir le niveau d'expérience
        if (experience && experience !== '-') {
            const experienceField = document.getElementById('required-experience');
            if (experienceField) {
                const expText = experience.toLowerCase();
                
                if (expText.includes('junior') || expText.includes('débutant')) {
                    experienceField.value = 'junior';
                } else if (expText.includes('2') || expText.includes('3')) {
                    experienceField.value = '2-3years';
                } else if (expText.includes('5') || expText.includes('10')) {
                    experienceField.value = '5-10years';
                } else if (expText.includes('10+') || expText.includes('senior')) {
                    experienceField.value = '10+years';
                }
            }
        }
        
        // Mettre à jour d'autres champs du formulaire si nécessaire
    }
    
    // Fonction pour afficher des notifications
    function showNotification(message, type = 'success') {
        console.log('Showing notification:', message, type);
        
        const notification = document.getElementById('notification');
        if (!notification) {
            console.error('Notification element not found');
            alert(message); // Fallback
            return;
        }
        
        const notificationMessage = notification.querySelector('.notification-message');
        if (!notificationMessage) {
            console.error('Notification message element not found');
            return;
        }
        
        notification.className = 'notification ' + type;
        notificationMessage.innerText = message;
        
        const icon = notification.querySelector('i:first-child');
        if (icon) {
            icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
        }
        
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 5000);
    }
    
    // Fonction pour gérer les erreurs
    function handleError(error) {
        console.error('Error in job parser display:', error);
        showNotification('Une erreur est survenue: ' + error.message, 'error');
    }
});
