/**
 * Gestionnaire du processus de recrutement personnalisé
 * Permet de personnaliser le flux de recrutement avec les fonctionnalités suivantes :
 * - Ajout/suppression d'étapes
 * - Édition du titre et de la description des étapes
 * - Ajout/gestion de participants
 * - Sauvegarde et chargement des modèles de processus
 * - Modification du statut des étapes
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des variables
    const flowContainer = document.querySelector('.flow-container');
    const addStepBtn = document.querySelector('.add-step-btn');
    const processFlowSection = document.querySelector('.process-flow');
    
    // Templates pour les différentes étapes prédéfinies
    const stepTemplates = {
        'entretien_telephonique': {
            title: 'Entretien téléphonique',
            description: 'Premier contact de 15-20 minutes pour évaluer l\'adéquation',
            icon: 'fa-phone-alt'
        },
        'test_technique': {
            title: 'Test technique',
            description: 'Évaluation des compétences techniques spécifiques au poste',
            icon: 'fa-code'
        },
        'entretien_video': {
            title: 'Entretien vidéo',
            description: 'Discussion approfondie sur les compétences et l\'expérience',
            icon: 'fa-video'
        },
        'entretien_equipe': {
            title: 'Rencontre avec l\'équipe',
            description: 'Présentation à l\'équipe et évaluation de la dynamique de groupe',
            icon: 'fa-users'
        },
        'assessment': {
            title: 'Assessment Center',
            description: 'Série d\'exercices pratiques pour évaluer les compétences',
            icon: 'fa-tasks'
        },
        'negociation': {
            title: 'Négociation',
            description: 'Discussion des conditions contractuelles et de la rémunération',
            icon: 'fa-handshake'
        }
    };
    
    // État des participants
    let participants = {
        // ID étape: [array de participants]
    };
    
    // ID unique pour les étapes
    let currentStepId = 6; // On commence à 6 car il y a déjà 5 étapes par défaut
    
    /**
     * Initialise les fonctionnalités du processus de recrutement
     */
    function initRecruitmentProcess() {
        // Ajouter un ID à chaque étape existante pour les actions ultérieures
        let existingSteps = document.querySelectorAll('.flow-step');
        existingSteps.forEach((step, index) => {
            step.setAttribute('data-step-id', index + 1);
            
            // Initialiser les participants pour les étapes existantes
            participants[index + 1] = [];
            
            // Ajouter les gestionnaires d'événements aux boutons existants
            addEventListenersToStepActions(step);
        });
        
        // Gestionnaire du bouton d'ajout d'étape
        addStepBtn.addEventListener('click', addNewStep);
        
        // Ajouter le bouton d'enregistrement du modèle
        addSaveTemplateButton();
        
        // Ajouter le menu déroulant des modèles prédéfinis
        addPredefinedTemplatesDropdown();
    }
    
    /**
     * Ajoute une nouvelle étape au processus
     * @param {Object} template - Template optionnel pour l'étape
     */
    function addNewStep(event, template = null) {
        const steps = document.querySelectorAll('.flow-step');
        const newStepNumber = steps.length + 1;
        currentStepId++;
        
        // Créer le titre et la description en fonction du template ou utiliser des valeurs par défaut
        let title = 'Nouvelle étape';
        let description = 'Description de cette étape';
        let icon = 'fa-clipboard-check';
        
        if (template) {
            title = template.title;
            description = template.description;
            icon = template.icon || icon;
        }
        
        // Créer un nouvel élément d'étape
        const newStep = document.createElement('div');
        newStep.className = 'flow-step';
        newStep.setAttribute('data-step-id', currentStepId);
        
        newStep.innerHTML = `
            <div class="flow-step-icon">${newStepNumber}</div>
            <div class="flow-step-content">
                <div class="flow-step-title">
                    <span class="step-title-text">${title}</span>
                    <span class="tooltip" data-tooltip="Éditer cette étape">
                        <i class="fas fa-info-circle edit-step-btn"></i>
                    </span>
                </div>
                <p class="flow-step-description">${description}</p>
                <div class="flow-step-actions">
                    <button type="button" class="flow-action-btn btn-danger delete-step-btn">
                        <i class="fas fa-times"></i> Supprimer
                    </button>
                    <button type="button" class="flow-action-btn add-participant-btn">
                        <i class="fas fa-user-plus"></i> Ajouter un participant
                    </button>
                    <button type="button" class="flow-action-btn change-status-btn">
                        <i class="fas fa-exchange-alt"></i> Statut
                    </button>
                </div>
                <div class="participants-container" style="display: none;"></div>
            </div>
        `;
        
        // Créer un connecteur pour la connexion
        const connector = document.createElement('div');
        connector.className = 'flow-connector';
        connector.innerHTML = '<div class="flow-connector-line"></div>';
        
        // Insérer l'étape et le connecteur avant le bouton d'ajout
        flowContainer.insertBefore(connector, addStepBtn);
        flowContainer.insertBefore(newStep, connector);
        
        // Initialiser les participants pour cette étape
        participants[currentStepId] = [];
        
        // Ajouter les gestionnaires d'événements aux boutons
        addEventListenersToStepActions(newStep);
        
        // Mettre à jour les numéros de toutes les étapes
        updateStepNumbers();
        
        // Afficher une notification
        showNotification('Étape ajoutée avec succès');
    }
    
    /**
     * Ajoute tous les gestionnaires d'événements nécessaires à une étape
     * @param {HTMLElement} step - L'élément d'étape
     */
    function addEventListenersToStepActions(step) {
        // Gestionnaire de suppression d'étape
        const deleteBtn = step.querySelector('.delete-step-btn');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                deleteStep(step);
            });
        }
        
        // Gestionnaire d'ajout de participant
        const addParticipantBtn = step.querySelector('.add-participant-btn');
        if (addParticipantBtn) {
            addParticipantBtn.addEventListener('click', function() {
                addParticipant(step);
            });
        }
        
        // Gestionnaire d'édition d'étape
        const editBtn = step.querySelector('.edit-step-btn');
        if (editBtn) {
            editBtn.addEventListener('click', function() {
                editStep(step);
            });
        }
        
        // Gestionnaire de changement de statut
        const statusBtn = step.querySelector('.change-status-btn');
        if (statusBtn) {
            statusBtn.addEventListener('click', function() {
                changeStepStatus(step);
            });
        }
    }
    
    /**
     * Supprime une étape du processus
     * @param {HTMLElement} step - L'étape à supprimer
     */
    function deleteStep(step) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette étape ?')) {
            const stepId = step.getAttribute('data-step-id');
            
            // Supprimer l'étape du DOM
            const connector = step.nextElementSibling;
            if (connector && connector.classList.contains('flow-connector')) {
                flowContainer.removeChild(connector);
            }
            flowContainer.removeChild(step);
            
            // Supprimer les participants de cette étape
            delete participants[stepId];
            
            // Mettre à jour les numéros des étapes
            updateStepNumbers();
            
            // Afficher une notification
            showNotification('Étape supprimée avec succès');
        }
    }
    
    /**
     * Met à jour les numéros d'étapes après un ajout ou une suppression
     */
    function updateStepNumbers() {
        const steps = document.querySelectorAll('.flow-step');
        steps.forEach((step, index) => {
            const stepIcon = step.querySelector('.flow-step-icon');
            if (stepIcon) {
                stepIcon.textContent = index + 1;
            }
        });
    }
    
    /**
     * Ouvre une modal pour éditer une étape
     * @param {HTMLElement} step - L'étape à éditer
     */
    function editStep(step) {
        const stepId = step.getAttribute('data-step-id');
        const titleElement = step.querySelector('.step-title-text');
        const descriptionElement = step.querySelector('.flow-step-description');
        
        const currentTitle = titleElement.textContent;
        const currentDescription = descriptionElement.textContent;
        
        // Créer une modal d'édition
        const modal = document.createElement('div');
        modal.className = 'edit-step-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '9999';
        
        modal.innerHTML = `
            <div class="modal-content" style="background-color: white; padding: 20px; border-radius: 10px; width: 500px; max-width: 90%;">
                <h3 style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    Éditer l'étape
                    <button class="close-modal" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
                </h3>
                <div class="form-group" style="margin-bottom: 15px;">
                    <label for="step-title" style="display: block; margin-bottom: 5px; font-weight: 500;">Titre de l'étape</label>
                    <input type="text" id="step-title" class="form-control" value="${currentTitle}" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="step-description" style="display: block; margin-bottom: 5px; font-weight: 500;">Description</label>
                    <textarea id="step-description" class="form-control" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">${currentDescription}</textarea>
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="step-icon" style="display: block; margin-bottom: 5px; font-weight: 500;">Icône (optionnel)</label>
                    <select id="step-icon" class="form-control" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <option value="fa-clipboard-check">✓ Liste de contrôle</option>
                        <option value="fa-phone-alt">📞 Téléphone</option>
                        <option value="fa-video">📹 Vidéo</option>
                        <option value="fa-users">👥 Équipe</option>
                        <option value="fa-code">💻 Code</option>
                        <option value="fa-tasks">📋 Tâches</option>
                        <option value="fa-handshake">🤝 Négociation</option>
                        <option value="fa-check-circle">✅ Validation</option>
                        <option value="fa-user-plus">👤 Recrutement</option>
                    </select>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="cancel-btn" style="padding: 10px 15px; border: 1px solid #ddd; background-color: white; border-radius: 5px; cursor: pointer;">Annuler</button>
                    <button class="save-btn" style="padding: 10px 15px; border: none; background-color: #7c3aed; color: white; border-radius: 5px; cursor: pointer;">Enregistrer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Gestionnaires d'événements de la modal
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const saveBtn = modal.querySelector('.save-btn');
        
        function closeModal() {
            document.body.removeChild(modal);
        }
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        saveBtn.addEventListener('click', function() {
            const newTitle = modal.querySelector('#step-title').value.trim();
            const newDescription = modal.querySelector('#step-description').value.trim();
            const newIcon = modal.querySelector('#step-icon').value;
            
            if (newTitle && newDescription) {
                // Mettre à jour les valeurs
                titleElement.textContent = newTitle;
                descriptionElement.textContent = newDescription;
                
                // Afficher une notification
                showNotification('Étape mise à jour avec succès');
                
                closeModal();
            } else {
                alert('Veuillez remplir tous les champs obligatoires.');
            }
        });
    }
    
    /**
     * Ajoute un participant à une étape
     * @param {HTMLElement} step - L'étape concernée
     */
    function addParticipant(step) {
        const stepId = step.getAttribute('data-step-id');
        const participantsContainer = step.querySelector('.participants-container');
        
        // Créer une modal pour ajouter un participant
        const modal = document.createElement('div');
        modal.className = 'add-participant-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '9999';
        
        modal.innerHTML = `
            <div class="modal-content" style="background-color: white; padding: 20px; border-radius: 10px; width: 500px; max-width: 90%;">
                <h3 style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    Ajouter un participant
                    <button class="close-modal" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
                </h3>
                <div class="form-group" style="margin-bottom: 15px;">
                    <label for="participant-name" style="display: block; margin-bottom: 5px; font-weight: 500;">Nom du participant</label>
                    <input type="text" id="participant-name" class="form-control" placeholder="Ex: Jean Dupont" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <div class="form-group" style="margin-bottom: 15px;">
                    <label for="participant-role" style="display: block; margin-bottom: 5px; font-weight: 500;">Rôle</label>
                    <select id="participant-role" class="form-control" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                        <option value="Recruteur">Recruteur</option>
                        <option value="Manager">Manager</option>
                        <option value="RH">Ressources Humaines</option>
                        <option value="Technique">Expert technique</option>
                        <option value="Direction">Direction</option>
                        <option value="Autre">Autre</option>
                    </select>
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="participant-email" style="display: block; margin-bottom: 5px; font-weight: 500;">Email (optionnel)</label>
                    <input type="email" id="participant-email" class="form-control" placeholder="Ex: jean.dupont@entreprise.com" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="cancel-btn" style="padding: 10px 15px; border: 1px solid #ddd; background-color: white; border-radius: 5px; cursor: pointer;">Annuler</button>
                    <button class="save-btn" style="padding: 10px 15px; border: none; background-color: #7c3aed; color: white; border-radius: 5px; cursor: pointer;">Ajouter</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Gestionnaires d'événements de la modal
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const saveBtn = modal.querySelector('.save-btn');
        
        function closeModal() {
            document.body.removeChild(modal);
        }
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        saveBtn.addEventListener('click', function() {
            const name = modal.querySelector('#participant-name').value.trim();
            const role = modal.querySelector('#participant-role').value;
            const email = modal.querySelector('#participant-email').value.trim();
            
            if (name) {
                // Ajouter le participant à l'état
                participants[stepId].push({ name, role, email });
                
                // Mettre à jour l'affichage des participants
                updateParticipantsDisplay(step);
                
                // Afficher une notification
                showNotification('Participant ajouté avec succès');
                
                closeModal();
            } else {
                alert('Veuillez au moins remplir le nom du participant.');
            }
        });
    }
    
    /**
     * Met à jour l'affichage des participants pour une étape
     * @param {HTMLElement} step - L'étape concernée
     */
    function updateParticipantsDisplay(step) {
        const stepId = step.getAttribute('data-step-id');
        const participantsContainer = step.querySelector('.participants-container');
        
        // Vider le conteneur
        participantsContainer.innerHTML = '';
        
        // S'il y a des participants, afficher le conteneur
        if (participants[stepId] && participants[stepId].length > 0) {
            participantsContainer.style.display = 'block';
            
            // Créer la liste des participants
            const participantsList = document.createElement('div');
            participantsList.className = 'participants-list';
            participantsList.style.marginTop = '10px';
            participantsList.style.padding = '10px';
            participantsList.style.backgroundColor = 'rgba(124, 58, 237, 0.05)';
            participantsList.style.borderRadius = '5px';
            
            // Ajouter le titre
            const title = document.createElement('h4');
            title.textContent = 'Participants';
            title.style.fontSize = '0.9rem';
            title.style.fontWeight = '600';
            title.style.marginBottom = '8px';
            participantsList.appendChild(title);
            
            // Ajouter chaque participant
            participants[stepId].forEach((participant, index) => {
                const participantItem = document.createElement('div');
                participantItem.className = 'participant-item';
                participantItem.style.display = 'flex';
                participantItem.style.justifyContent = 'space-between';
                participantItem.style.alignItems = 'center';
                participantItem.style.padding = '5px 0';
                participantItem.style.borderBottom = index < participants[stepId].length - 1 ? '1px solid rgba(124, 58, 237, 0.1)' : 'none';
                
                participantItem.innerHTML = `
                    <div>
                        <span style="font-weight: 500;">${participant.name}</span>
                        <span style="font-size: 0.8rem; color: #64748b; margin-left: 5px;">(${participant.role})</span>
                    </div>
                    <button class="remove-participant-btn" data-index="${index}" style="background: none; border: none; color: #ef4444; cursor: pointer; font-size: 0.8rem;">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                
                participantsList.appendChild(participantItem);
            });
            
            participantsContainer.appendChild(participantsList);
            
            // Ajouter les gestionnaires d'événements pour supprimer les participants
            const removeButtons = participantsContainer.querySelectorAll('.remove-participant-btn');
            removeButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    const index = parseInt(btn.getAttribute('data-index'));
                    participants[stepId].splice(index, 1);
                    updateParticipantsDisplay(step);
                    showNotification('Participant supprimé');
                });
            });
        } else {
            participantsContainer.style.display = 'none';
        }
    }
    
    /**
     * Change le statut d'une étape (active, terminée, etc.)
     * @param {HTMLElement} step - L'étape concernée
     */
    function changeStepStatus(step) {
        // Créer une modal pour changer le statut
        const modal = document.createElement('div');
        modal.className = 'change-status-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '9999';
        
        modal.innerHTML = `
            <div class="modal-content" style="background-color: white; padding: 20px; border-radius: 10px; width: 400px; max-width: 90%;">
                <h3 style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    Changer le statut
                    <button class="close-modal" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
                </h3>
                <div class="status-options" style="display: flex; flex-direction: column; gap: 10px;">
                    <button class="status-option" data-status="pending" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: white; text-align: left; cursor: pointer;">
                        <i class="fas fa-clock" style="color: #f59e0b; margin-right: 10px;"></i> En attente
                    </button>
                    <button class="status-option" data-status="active" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: white; text-align: left; cursor: pointer;">
                        <i class="fas fa-spinner" style="color: #3b82f6; margin-right: 10px;"></i> En cours
                    </button>
                    <button class="status-option" data-status="completed" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: white; text-align: left; cursor: pointer;">
                        <i class="fas fa-check" style="color: #10b981; margin-right: 10px;"></i> Terminée
                    </button>
                    <button class="status-option" data-status="skipped" style="padding: 10px; border: 1px solid #ddd; border-radius: 5px; background-color: white; text-align: left; cursor: pointer;">
                        <i class="fas fa-forward" style="color: #6b7280; margin-right: 10px;"></i> Ignorée
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Gestionnaires d'événements de la modal
        const closeBtn = modal.querySelector('.close-modal');
        closeBtn.addEventListener('click', function() {
            document.body.removeChild(modal);
        });
        
        const statusOptions = modal.querySelectorAll('.status-option');
        statusOptions.forEach(option => {
            option.addEventListener('click', function() {
                const status = this.getAttribute('data-status');
                
                // Supprimer toutes les classes de statut existantes
                step.classList.remove('active', 'completed', 'pending', 'skipped');
                
                // Ajouter la nouvelle classe de statut
                step.classList.add(status);
                
                // Mettre à jour l'apparence en fonction du statut
                const stepIcon = step.querySelector('.flow-step-icon');
                
                if (status === 'completed') {
                    stepIcon.innerHTML = '<i class="fas fa-check"></i>';
                    stepIcon.style.backgroundColor = '#10b981';
                    stepIcon.style.color = 'white';
                    stepIcon.style.borderColor = '#10b981';
                } else if (status === 'active') {
                    stepIcon.textContent = step.querySelector('.flow-step-icon').textContent;
                    stepIcon.style.backgroundColor = '#7c3aed';
                    stepIcon.style.color = 'white';
                    stepIcon.style.borderColor = '#7c3aed';
                } else if (status === 'pending') {
                    stepIcon.textContent = step.querySelector('.flow-step-icon').textContent;
                    stepIcon.style.backgroundColor = '#f59e0b';
                    stepIcon.style.color = 'white';
                    stepIcon.style.borderColor = '#f59e0b';
                } else if (status === 'skipped') {
                    stepIcon.innerHTML = '<i class="fas fa-forward"></i>';
                    stepIcon.style.backgroundColor = '#6b7280';
                    stepIcon.style.color = 'white';
                    stepIcon.style.borderColor = '#6b7280';
                }
                
                // Afficher une notification
                showNotification('Statut mis à jour');
                
                document.body.removeChild(modal);
            });
        });
    }
    
    /**
     * Ajoute un bouton pour sauvegarder le modèle actuel
     */
    function addSaveTemplateButton() {
        const saveTemplateBtn = document.createElement('button');
        saveTemplateBtn.className = 'btn btn-secondary save-template-btn';
        saveTemplateBtn.style.marginLeft = '10px';
        saveTemplateBtn.innerHTML = '<i class="fas fa-save"></i> Enregistrer ce processus';
        
        const actionButtons = document.querySelector('.action-buttons');
        actionButtons.prepend(saveTemplateBtn);
        
        saveTemplateBtn.addEventListener('click', function() {
            saveProcessTemplate();
        });
    }
    
    /**
     * Ajoute un menu déroulant pour les modèles prédéfinis
     */
    function addPredefinedTemplatesDropdown() {
        // Créer le conteneur pour le sélecteur de modèles
        const templateSelectorContainer = document.createElement('div');
        templateSelectorContainer.className = 'template-selector-container';
        templateSelectorContainer.style.display = 'flex';
        templateSelectorContainer.style.alignItems = 'center';
        templateSelectorContainer.style.marginBottom = '20px';
        
        templateSelectorContainer.innerHTML = `
            <h4 style="margin: 0 15px 0 0; font-size: 1rem; font-weight: 600;">Modèles de processus</h4>
            <select id="process-template-selector" class="form-control" style="max-width: 250px;">
                <option value="">Sélectionner un modèle prédéfini</option>
                <option value="technique">Recrutement technique</option>
                <option value="manager">Recrutement manager</option>
                <option value="commercial">Recrutement commercial</option>
                <option value="rapide">Processus rapide</option>
                <option value="approfondi">Processus approfondi</option>
            </select>
            <button id="apply-template-btn" class="btn" style="margin-left: 10px; padding: 8px 16px; background-color: #7c3aed; color: white; border: none; border-radius: 5px; cursor: pointer;">
                <i class="fas fa-check"></i> Appliquer
            </button>
        `;
        
        // Insérer avant le conteneur du flux
        processFlowSection.insertBefore(templateSelectorContainer, flowContainer);
        
        // Ajouter le gestionnaire d'événements pour appliquer un modèle
        const applyTemplateBtn = document.getElementById('apply-template-btn');
        applyTemplateBtn.addEventListener('click', function() {
            const templateSelector = document.getElementById('process-template-selector');
            const selectedTemplate = templateSelector.value;
            
            if (selectedTemplate) {
                applyProcessTemplate(selectedTemplate);
            } else {
                alert('Veuillez sélectionner un modèle de processus.');
            }
        });
    }
    
    /**
     * Sauvegarde le processus actuel comme modèle
     */
    function saveProcessTemplate() {
        // Créer une modal pour nommer et sauvegarder le modèle
        const modal = document.createElement('div');
        modal.className = 'save-template-modal';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.display = 'flex';
        modal.style.justifyContent = 'center';
        modal.style.alignItems = 'center';
        modal.style.zIndex = '9999';
        
        modal.innerHTML = `
            <div class="modal-content" style="background-color: white; padding: 20px; border-radius: 10px; width: 500px; max-width: 90%;">
                <h3 style="margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center;">
                    Enregistrer le processus comme modèle
                    <button class="close-modal" style="background: none; border: none; font-size: 20px; cursor: pointer;">&times;</button>
                </h3>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="template-name" style="display: block; margin-bottom: 5px; font-weight: 500;">Nom du modèle</label>
                    <input type="text" id="template-name" class="form-control" placeholder="Ex: Processus technique" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label for="template-description" style="display: block; margin-bottom: 5px; font-weight: 500;">Description (optionnelle)</label>
                    <textarea id="template-description" class="form-control" rows="3" placeholder="Décrivez brièvement ce modèle de processus" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 10px;">
                    <button class="cancel-btn" style="padding: 10px 15px; border: 1px solid #ddd; background-color: white; border-radius: 5px; cursor: pointer;">Annuler</button>
                    <button class="save-btn" style="padding: 10px 15px; border: none; background-color: #7c3aed; color: white; border-radius: 5px; cursor: pointer;">Enregistrer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Gestionnaires d'événements de la modal
        const closeBtn = modal.querySelector('.close-modal');
        const cancelBtn = modal.querySelector('.cancel-btn');
        const saveBtn = modal.querySelector('.save-btn');
        
        function closeModal() {
            document.body.removeChild(modal);
        }
        
        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);
        
        saveBtn.addEventListener('click', function() {
            const templateName = modal.querySelector('#template-name').value.trim();
            const templateDescription = modal.querySelector('#template-description').value.trim();
            
            if (templateName) {
                // Collecter les données du processus actuel
                const steps = document.querySelectorAll('.flow-step');
                const processData = {
                    name: templateName,
                    description: templateDescription,
                    steps: []
                };
                
                steps.forEach(step => {
                    const stepId = step.getAttribute('data-step-id');
                    const title = step.querySelector('.step-title-text').textContent;
                    const description = step.querySelector('.flow-step-description').textContent;
                    
                    processData.steps.push({
                        title,
                        description,
                        participants: participants[stepId] || []
                    });
                });
                
                // Sauvegarder dans localStorage
                const savedTemplates = JSON.parse(localStorage.getItem('recruitmentProcessTemplates') || '{}');
                savedTemplates[templateName] = processData;
                localStorage.setItem('recruitmentProcessTemplates', JSON.stringify(savedTemplates));
                
                // Ajouter au sélecteur de modèles
                const templateSelector = document.getElementById('process-template-selector');
                const option = document.createElement('option');
                option.value = templateName;
                option.textContent = templateName;
                templateSelector.appendChild(option);
                
                showNotification('Modèle de processus enregistré avec succès');
                closeModal();
            } else {
                alert('Veuillez entrer un nom pour le modèle.');
            }
        });
    }
    
    /**
     * Applique un modèle de processus prédéfini
     * @param {string} templateName - Le nom du modèle à appliquer
     */
    function applyProcessTemplate(templateName) {
        // Demander confirmation
        if (!confirm('Êtes-vous sûr de vouloir appliquer ce modèle ? Cela remplacera le processus actuel.')) {
            return;
        }
        
        // Supprimer toutes les étapes actuelles sauf la première
        const steps = document.querySelectorAll('.flow-step');
        
        // Garder une référence à la première étape
        const firstStep = steps[0];
        
        // Supprimer toutes les étapes sauf la première et leurs connecteurs
        for (let i = 1; i < steps.length; i++) {
            const stepToRemove = steps[i];
            const connectorBefore = stepToRemove.previousElementSibling;
            if (connectorBefore && connectorBefore.classList.contains('flow-connector')) {
                flowContainer.removeChild(connectorBefore);
            }
            flowContainer.removeChild(stepToRemove);
        }
        
        // Réinitialiser les participants
        participants = {};
        participants[1] = []; // Pour la première étape
        
        // Mettre à jour le titre et la description de la première étape selon le modèle
        if (templateName === 'technique') {
            firstStep.querySelector('.step-title-text').textContent = 'Évaluation initiale du CV';
            firstStep.querySelector('.flow-step-description').textContent = 'Analyse du profil technique et des compétences requises';
            
            // Ajouter les étapes spécifiques au recrutement technique
            addNewStep(null, stepTemplates.entretien_telephonique);
            addNewStep(null, stepTemplates.test_technique);
            addNewStep(null, {
                title: 'Revue de code',
                description: 'Analyse d\'un exemple de code fourni par le candidat',
                icon: 'fa-code'
            });
            addNewStep(null, stepTemplates.entretien_video);
            addNewStep(null, stepTemplates.entretien_equipe);
            addNewStep(null, stepTemplates.negociation);
            
        } else if (templateName === 'manager') {
            firstStep.querySelector('.step-title-text').textContent = 'Présélection des candidats';
            firstStep.querySelector('.flow-step-description').textContent = 'Étude des profils et sélection des candidats potentiels';
            
            // Ajouter les étapes spécifiques au recrutement manager
            addNewStep(null, stepTemplates.entretien_telephonique);
            addNewStep(null, {
                title: 'Assessment Center',
                description: 'Évaluation des compétences managériales et de leadership',
                icon: 'fa-tasks'
            });
            addNewStep(null, {
                title: 'Entretien avec la Direction',
                description: 'Discussion approfondie sur la vision et les objectifs',
                icon: 'fa-handshake'
            });
            addNewStep(null, stepTemplates.entretien_equipe);
            addNewStep(null, stepTemplates.negociation);
            
        } else if (templateName === 'commercial') {
            firstStep.querySelector('.step-title-text').textContent = 'Qualification initiale';
            firstStep.querySelector('.flow-step-description').textContent = 'Évaluation de l\'expérience commerciale et des résultats';
            
            // Ajouter les étapes spécifiques au recrutement commercial
            addNewStep(null, stepTemplates.entretien_telephonique);
            addNewStep(null, {
                title: 'Mise en situation de vente',
                description: 'Exercice pratique de pitch et négociation',
                icon: 'fa-chart-line'
            });
            addNewStep(null, stepTemplates.entretien_video);
            addNewStep(null, {
                title: 'Rencontre avec l\'équipe commerciale',
                description: 'Présentation de l\'équipe et de la dynamique de travail',
                icon: 'fa-users'
            });
            addNewStep(null, stepTemplates.negociation);
            
        } else if (templateName === 'rapide') {
            firstStep.querySelector('.step-title-text').textContent = 'Entretien téléphonique';
            firstStep.querySelector('.flow-step-description').textContent = 'Premier contact pour évaluer les compétences et motivations';
            
            // Ajouter les étapes pour un processus rapide
            addNewStep(null, {
                title: 'Entretien avec le manager',
                description: 'Discussion approfondie sur les compétences et l\'expérience',
                icon: 'fa-user-tie'
            });
            addNewStep(null, stepTemplates.negociation);
            
        } else if (templateName === 'approfondi') {
            firstStep.querySelector('.step-title-text').textContent = 'Présélection des CV';
            firstStep.querySelector('.flow-step-description').textContent = 'Analyse détaillée des profils et première sélection';
            
            // Ajouter les étapes pour un processus approfondi
            addNewStep(null, stepTemplates.entretien_telephonique);
            addNewStep(null, {
                title: 'Tests d\'aptitude',
                description: 'Évaluation des compétences techniques et comportementales',
                icon: 'fa-clipboard-check'
            });
            addNewStep(null, stepTemplates.entretien_video);
            addNewStep(null, stepTemplates.assessment);
            addNewStep(null, {
                title: 'Vérification des références',
                description: 'Contact avec les anciens employeurs ou collaborateurs',
                icon: 'fa-user-check'
            });
            addNewStep(null, stepTemplates.entretien_equipe);
            addNewStep(null, {
                title: 'Entretien final',
                description: 'Dernière validation avant proposition',
                icon: 'fa-stamp'
            });
            addNewStep(null, stepTemplates.negociation);
        }
        
        // Vérifier si c'est un modèle sauvegardé
        const savedTemplates = JSON.parse(localStorage.getItem('recruitmentProcessTemplates') || '{}');
        if (savedTemplates[templateName]) {
            // Appliquer le modèle sauvegardé
            const savedTemplate = savedTemplates[templateName];
            
            // Mettre à jour la première étape
            if (savedTemplate.steps && savedTemplate.steps.length > 0) {
                firstStep.querySelector('.step-title-text').textContent = savedTemplate.steps[0].title;
                firstStep.querySelector('.flow-step-description').textContent = savedTemplate.steps[0].description;
                
                // Ajouter les participants de la première étape
                if (savedTemplate.steps[0].participants) {
                    participants[1] = savedTemplate.steps[0].participants;
                    updateParticipantsDisplay(firstStep);
                }
                
                // Ajouter les autres étapes du modèle
                for (let i = 1; i < savedTemplate.steps.length; i++) {
                    const stepData = savedTemplate.steps[i];
                    
                    // Ajouter l'étape
                    addNewStep(null, {
                        title: stepData.title,
                        description: stepData.description
                    });
                    
                    // Récupérer l'étape nouvellement créée
                    const newStepElement = document.querySelectorAll('.flow-step')[i];
                    const newStepId = newStepElement.getAttribute('data-step-id');
                    
                    // Ajouter les participants
                    if (stepData.participants) {
                        participants[newStepId] = stepData.participants;
                        updateParticipantsDisplay(newStepElement);
                    }
                }
            }
        }
        
        // Afficher une notification
        showNotification('Modèle de processus appliqué avec succès');
    }
    
    /**
     * Affiche une notification à l'utilisateur
     * @param {string} message - Le message à afficher
     */
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.right = '20px';
        notification.style.backgroundColor = 'rgba(124, 58, 237, 0.9)';
        notification.style.color = 'white';
        notification.style.padding = '12px 20px';
        notification.style.borderRadius = '5px';
        notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        notification.style.zIndex = '9999';
        notification.style.transition = 'all 0.3s ease';
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(20px)';
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <i class="fas fa-check-circle"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Animation d'entrée
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateY(0)';
        }, 10);
        
        // Disparaître après 3 secondes
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(20px)';
            
            // Supprimer du DOM après la fin de l'animation
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Ajouter CSS pour les nouvelles fonctionnalités
    function addCustomStyles() {
        const styleSheet = document.createElement('style');
        styleSheet.type = 'text/css';
        styleSheet.textContent = `
            /* Animation pour les modales */
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Styles pour les étapes avec statut */
            .flow-step.active .flow-step-icon {
                background-color: #7c3aed;
                color: white;
                border-color: #7c3aed;
            }
            
            .flow-step.completed .flow-step-icon {
                background-color: #10b981;
                color: white;
                border-color: #10b981;
            }
            
            .flow-step.pending .flow-step-icon {
                background-color: #f59e0b;
                color: white;
                border-color: #f59e0b;
            }
            
            .flow-step.skipped .flow-step-icon {
                background-color: #6b7280;
                color: white;
                border-color: #6b7280;
            }
            
            /* Hover sur les boutons d'action */
            .flow-action-btn:hover {
                background-color: rgba(124, 58, 237, 0.1);
            }
            
            /* Style du menu déroulant */
            .template-selector-container select:focus {
                border-color: #7c3aed;
                outline: none;
                box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.1);
            }
            
            /* Styles pour les participants */
            .participants-list {
                transition: all 0.3s ease;
            }
            
            .participant-item:hover {
                background-color: rgba(124, 58, 237, 0.05);
            }
            
            /* Bouton d'enregistrement de template */
            .save-template-btn:hover {
                background-color: rgba(124, 58, 237, 0.1);
                color: #7c3aed;
            }
        `;
        
        document.head.appendChild(styleSheet);
    }
    
    // Initialiser les fonctionnalités
    addCustomStyles();
    initRecruitmentProcess();
});