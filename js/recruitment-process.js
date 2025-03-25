/**
 * Script pour rendre le processus de recrutement modulable et personnalisable
 * Ce script permet:
 * - D'ajouter de nouvelles étapes
 * - De supprimer des étapes existantes
 * - De modifier le titre et la description des étapes
 * - D'ajouter des participants aux étapes
 */

document.addEventListener('DOMContentLoaded', function() {
    initRecruitmentProcess();
});

/**
 * Utilitaire pour trouver un élément contenant un texte spécifique
 */
function findElementByText(selector, text) {
    const elements = document.querySelectorAll(selector);
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].textContent.includes(text)) {
            return elements[i];
        }
    }
    return null;
}

/**
 * Initialise toutes les fonctionnalités du processus de recrutement
 */
function initRecruitmentProcess() {
    // Initialiser les boutons existants
    initExistingButtons();
    
    // Rendre les titres et descriptions éditables
    makeContentEditable();
    
    // Ajouter l'écouteur pour le bouton d'ajout d'étape
    const addStepBtn = document.querySelector('.add-step-btn');
    if (addStepBtn) {
        addStepBtn.addEventListener('click', addNewStep);
    }
    
    // Sauvegarder le processus au moment de la soumission du formulaire
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            saveRecruitmentProcess();
            alert('Le processus de recrutement a été enregistré avec succès!');
            return false;
        });
    }
    
    // Activer le bouton "Enregistrer comme brouillon"
    const saveAsDraftBtn = findElementByText('button', 'Enregistrer comme brouillon');
    if (saveAsDraftBtn) {
        saveAsDraftBtn.addEventListener('click', function() {
            saveRecruitmentProcess();
            alert('Le processus de recrutement a été enregistré comme brouillon!');
        });
    }
}

/**
 * Initialise les boutons sur les étapes existantes
 */
function initExistingButtons() {
    // Initialiser les boutons Supprimer
    document.querySelectorAll('.flow-step button').forEach(button => {
        if (button.textContent.includes('Supprimer')) {
            button.addEventListener('click', function() {
                const flowStep = this.closest('.flow-step');
                if (flowStep) {
                    if (confirm('Êtes-vous sûr de vouloir supprimer cette étape?')) {
                        flowStep.remove();
                        reindexSteps();
                    }
                }
            });
        } else if (button.textContent.includes('Ajouter un participant')) {
            button.addEventListener('click', function() {
                openParticipantModal(this.closest('.flow-step'));
            });
        } else if (button.textContent.includes('Options')) {
            button.addEventListener('click', function() {
                openOptionsModal(this.closest('.flow-step'));
            });
        } else if (button.textContent.includes('Terminé')) {
            button.addEventListener('click', function() {
                markStepAsCompleted(this.closest('.flow-step'));
            });
        }
    });
}

/**
 * Rend les titres et descriptions des étapes éditables
 */
function makeContentEditable() {
    document.querySelectorAll('.flow-step-title span:first-child').forEach(titleSpan => {
        titleSpan.setAttribute('contenteditable', 'true');
        titleSpan.addEventListener('blur', function() {
            if (this.textContent.trim() === '') {
                this.textContent = 'Nouvelle étape';
            }
        });
    });
    
    document.querySelectorAll('.flow-step-description').forEach(description => {
        description.setAttribute('contenteditable', 'true');
        description.addEventListener('blur', function() {
            if (this.textContent.trim() === '') {
                this.textContent = 'Description de cette étape';
            }
        });
    });
}

/**
 * Ajoute une nouvelle étape au processus de recrutement
 */
function addNewStep() {
    const flowSteps = document.querySelectorAll('.flow-step');
    const newStepNumber = flowSteps.length + 1;
    
    const newStepHTML = `
        <div class="flow-step">
            <div class="flow-step-icon">${newStepNumber}</div>
            <div class="flow-step-content">
                <div class="flow-step-title">
                    <span contenteditable="true">Nouvelle étape</span>
                    <span class="tooltip" data-tooltip="Définir cette étape">
                        <i class="fas fa-info-circle"></i>
                    </span>
                </div>
                <p class="flow-step-description" contenteditable="true">Description de cette étape</p>
                <div class="flow-step-actions">
                    <button type="button" class="flow-action-btn btn-danger">
                        <i class="fas fa-times"></i> Supprimer
                    </button>
                    <button type="button" class="flow-action-btn">
                        <i class="fas fa-user-plus"></i> Ajouter un participant
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Insérer la nouvelle étape avant le bouton d'ajout
    const addStepBtn = document.querySelector('.add-step-btn').parentElement;
    addStepBtn.insertAdjacentHTML('beforebegin', newStepHTML);
    
    // Initialiser les boutons de la nouvelle étape
    const newStep = addStepBtn.previousElementSibling;
    const deleteBtn = newStep.querySelector('button:first-child');
    deleteBtn.addEventListener('click', function() {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette étape?')) {
            newStep.remove();
            reindexSteps();
        }
    });
    
    const addParticipantBtn = newStep.querySelector('button:last-child');
    addParticipantBtn.addEventListener('click', function() {
        openParticipantModal(newStep);
    });
}

/**
 * Réindexe les numéros des étapes après une suppression
 */
function reindexSteps() {
    document.querySelectorAll('.flow-step').forEach((step, index) => {
        step.querySelector('.flow-step-icon').textContent = index + 1;
    });
}

/**
 * Ouvre une modal pour ajouter un participant à une étape
 */
function openParticipantModal(step) {
    // Créer la modal si elle n'existe pas déjà
    let modal = document.getElementById('participant-modal');
    if (!modal) {
        const modalHTML = `
            <div id="participant-modal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h2>Ajouter un participant</h2>
                    <div class="form-group">
                        <label for="participant-name">Nom du participant:</label>
                        <input type="text" id="participant-name" class="form-control" placeholder="Nom et prénom">
                    </div>
                    <div class="form-group">
                        <label for="participant-role">Rôle:</label>
                        <select id="participant-role" class="form-control">
                            <option value="interviewer">Interviewer</option>
                            <option value="observateur">Observateur</option>
                            <option value="decision-maker">Décideur</option>
                            <option value="rh">Ressources Humaines</option>
                            <option value="technique">Expert technique</option>
                        </select>
                    </div>
                    <button id="add-participant-btn" class="btn btn-primary">Ajouter</button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('participant-modal');
        
        // Gérer la fermeture de la modal
        const closeBtn = modal.querySelector('.close');
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Afficher la modal
    modal.style.display = 'block';
    
    // Gérer l'ajout du participant
    const addParticipantBtn = document.getElementById('add-participant-btn');
    const stepTitle = step.querySelector('.flow-step-title span:first-child').textContent;
    
    // Créer une fonction unique pour cet événement
    const addParticipantHandler = function() {
        const name = document.getElementById('participant-name').value;
        const role = document.getElementById('participant-role').value;
        
        if (name.trim() === '') {
            alert('Veuillez entrer un nom pour le participant.');
            return;
        }
        
        // Ajouter le participant à l'étape
        const participantsList = step.querySelector('.participants-list');
        if (!participantsList) {
            // Créer la liste des participants si elle n'existe pas
            const participantsHTML = `
                <div class="participants-list">
                    <h4>Participants:</h4>
                    <ul></ul>
                </div>
            `;
            step.querySelector('.flow-step-description').insertAdjacentHTML('afterend', participantsHTML);
        }
        
        const participantsUl = step.querySelector('.participants-list ul');
        const participantHTML = `
            <li data-role="${role}">
                <span>${name}</span> (${getRoleFrenchName(role)})
                <button type="button" class="remove-participant">×</button>
            </li>
        `;
        participantsUl.insertAdjacentHTML('beforeend', participantHTML);
        
        // Ajouter l'événement pour supprimer un participant
        const removeBtn = participantsUl.lastElementChild.querySelector('.remove-participant');
        removeBtn.addEventListener('click', function() {
            this.parentElement.remove();
            if (participantsUl.children.length === 0) {
                step.querySelector('.participants-list').remove();
            }
        });
        
        // Fermer la modal
        modal.style.display = 'none';
        document.getElementById('participant-name').value = '';
        
        // Nettoyer l'événement pour éviter les doublons
        addParticipantBtn.removeEventListener('click', addParticipantHandler);
    };
    
    // Supprimer les gestionnaires d'événements précédents et ajouter le nouveau
    addParticipantBtn.replaceWith(addParticipantBtn.cloneNode(true));
    document.getElementById('add-participant-btn').addEventListener('click', addParticipantHandler);
}

/**
 * Obtient le nom français d'un rôle
 */
function getRoleFrenchName(role) {
    const roles = {
        'interviewer': 'Interviewer',
        'observateur': 'Observateur',
        'decision-maker': 'Décideur',
        'rh': 'RH',
        'technique': 'Expert technique'
    };
    return roles[role] || role;
}

/**
 * Ouvre une modal d'options pour une étape
 */
function openOptionsModal(step) {
    // Créer la modal si elle n'existe pas déjà
    let modal = document.getElementById('options-modal');
    if (!modal) {
        const modalHTML = `
            <div id="options-modal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h2>Options de l'étape</h2>
                    <div class="form-group">
                        <label for="step-duration">Durée estimée:</label>
                        <select id="step-duration" class="form-control">
                            <option value="15">15 minutes</option>
                            <option value="30">30 minutes</option>
                            <option value="45">45 minutes</option>
                            <option value="60" selected>1 heure</option>
                            <option value="90">1h30</option>
                            <option value="120">2 heures</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="step-location">Lieu:</label>
                        <select id="step-location" class="form-control">
                            <option value="visio">Visioconférence</option>
                            <option value="phone">Téléphone</option>
                            <option value="office">Dans nos locaux</option>
                            <option value="external">Site externe</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="step-required">Étape obligatoire:</label>
                        <input type="checkbox" id="step-required" checked>
                    </div>
                    <button id="save-options-btn" class="btn btn-primary">Enregistrer</button>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('options-modal');
        
        // Gérer la fermeture de la modal
        const closeBtn = modal.querySelector('.close');
        closeBtn.addEventListener('click', function() {
            modal.style.display = 'none';
        });
        
        window.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Afficher la modal
    modal.style.display = 'block';
    
    // Gérer l'enregistrement des options
    const saveOptionsBtn = document.getElementById('save-options-btn');
    const stepTitle = step.querySelector('.flow-step-title span:first-child').textContent;
    
    // Créer une fonction unique pour cet événement
    const saveOptionsHandler = function() {
        const duration = document.getElementById('step-duration').value;
        const location = document.getElementById('step-location').value;
        const required = document.getElementById('step-required').checked;
        
        // Stocker les options dans des attributs data-
        step.dataset.duration = duration;
        step.dataset.location = location;
        step.dataset.required = required;
        
        // Ajouter un indicateur visuel si nécessaire
        let optionsTag = step.querySelector('.options-tag');
        if (!optionsTag) {
            const optionsTagHTML = `
                <div class="options-tag">
                    <span>${getDurationText(duration)}</span> | 
                    <span>${getLocationText(location)}</span> | 
                    <span>${required ? 'Obligatoire' : 'Optionnelle'}</span>
                </div>
            `;
            step.querySelector('.flow-step-description').insertAdjacentHTML('afterend', optionsTagHTML);
        } else {
            optionsTag.innerHTML = `
                <span>${getDurationText(duration)}</span> | 
                <span>${getLocationText(location)}</span> | 
                <span>${required ? 'Obligatoire' : 'Optionnelle'}</span>
            `;
        }
        
        // Fermer la modal
        modal.style.display = 'none';
        
        // Nettoyer l'événement pour éviter les doublons
        saveOptionsBtn.removeEventListener('click', saveOptionsHandler);
    };
    
    // Supprimer les gestionnaires d'événements précédents et ajouter le nouveau
    saveOptionsBtn.replaceWith(saveOptionsBtn.cloneNode(true));
    document.getElementById('save-options-btn').addEventListener('click', saveOptionsHandler);
}

/**
 * Obtient le texte de durée à partir de la valeur en minutes
 */
function getDurationText(minutes) {
    if (minutes < 60) {
        return `${minutes} min`;
    } else if (minutes === '60') {
        return '1h';
    } else if (minutes === '90') {
        return '1h30';
    } else if (minutes === '120') {
        return '2h';
    }
    return `${minutes} min`;
}

/**
 * Obtient le texte de lieu à partir de la valeur
 */
function getLocationText(location) {
    const locations = {
        'visio': 'Visioconférence',
        'phone': 'Téléphone',
        'office': 'Nos locaux',
        'external': 'Site externe'
    };
    return locations[location] || location;
}

/**
 * Marque une étape comme terminée
 */
function markStepAsCompleted(step) {
    step.classList.add('completed');
    const completeButton = findElementByText(step.querySelectorAll('button'), 'Terminé');
    if (completeButton) {
        completeButton.textContent = 'Terminé ✓';
        completeButton.classList.add('btn-success');
    }
}

/**
 * Sauvegarde le processus de recrutement actuel
 */
function saveRecruitmentProcess() {
    const flowSteps = document.querySelectorAll('.flow-step');
    const process = [];
    
    flowSteps.forEach((step, index) => {
        const title = step.querySelector('.flow-step-title span:first-child').textContent;
        const description = step.querySelector('.flow-step-description').textContent;
        
        // Collecter les participants
        const participants = [];
        const participantElements = step.querySelectorAll('.participants-list li');
        participantElements.forEach(el => {
            participants.push({
                name: el.querySelector('span').textContent,
                role: el.dataset.role
            });
        });
        
        // Collecter les options
        const options = {
            duration: step.dataset.duration || '60',
            location: step.dataset.location || 'visio',
            required: step.dataset.required === 'true' || step.dataset.required === true || true
        };
        
        process.push({
            order: index + 1,
            title: title,
            description: description,
            participants: participants,
            options: options,
            completed: step.classList.contains('completed')
        });
    });
    
    // Sauvegarder dans le localStorage
    localStorage.setItem('recruitmentProcess', JSON.stringify(process));
    
    // Dans une application réelle, on enverrait ces données au serveur
    console.log('Processus sauvegardé:', process);
    
    return process;
}

/**
 * Charge un processus de recrutement sauvegardé
 */
function loadRecruitmentProcess() {
    const savedProcess = localStorage.getItem('recruitmentProcess');
    if (!savedProcess) {
        console.log('Aucun processus sauvegardé trouvé.');
        return;
    }
    
    try {
        const process = JSON.parse(savedProcess);
        
        // Supprimer toutes les étapes existantes
        document.querySelectorAll('.flow-step').forEach(step => step.remove());
        
        // Ajouter les étapes sauvegardées
        process.forEach(stepData => {
            addSavedStep(stepData);
        });
        
        console.log('Processus chargé avec succès.');
    } catch (error) {
        console.error('Erreur lors du chargement du processus:', error);
    }
}

/**
 * Ajoute une étape sauvegardée au processus
 */
function addSavedStep(stepData) {
    const stepHTML = `
        <div class="flow-step${stepData.completed ? ' completed' : ''}">
            <div class="flow-step-icon">${stepData.order}</div>
            <div class="flow-step-content">
                <div class="flow-step-title">
                    <span contenteditable="true">${stepData.title}</span>
                    <span class="tooltip" data-tooltip="Définir cette étape">
                        <i class="fas fa-info-circle"></i>
                    </span>
                </div>
                <p class="flow-step-description" contenteditable="true">${stepData.description}</p>
                ${stepData.options ? `
                <div class="options-tag">
                    <span>${getDurationText(stepData.options.duration)}</span> | 
                    <span>${getLocationText(stepData.options.location)}</span> | 
                    <span>${stepData.options.required ? 'Obligatoire' : 'Optionnelle'}</span>
                </div>
                ` : ''}
                ${stepData.participants && stepData.participants.length > 0 ? `
                <div class="participants-list">
                    <h4>Participants:</h4>
                    <ul>
                        ${stepData.participants.map(p => `
                        <li data-role="${p.role}">
                            <span>${p.name}</span> (${getRoleFrenchName(p.role)})
                            <button type="button" class="remove-participant">×</button>
                        </li>
                        `).join('')}
                    </ul>
                </div>
                ` : ''}
                <div class="flow-step-actions">
                    <button type="button" class="flow-action-btn btn-danger">
                        <i class="fas fa-times"></i> Supprimer
                    </button>
                    ${stepData.completed ? `
                    <button type="button" class="flow-action-btn btn-success">
                        <i class="fas fa-check"></i> Terminé ✓
                    </button>
                    ` : `
                    <button type="button" class="flow-action-btn">
                        <i class="fas fa-user-plus"></i> Ajouter un participant
                    </button>
                    `}
                </div>
            </div>
        </div>
    `;
    
    // Insérer l'étape avant le bouton d'ajout
    const addStepBtn = document.querySelector('.add-step-btn').parentElement;
    addStepBtn.insertAdjacentHTML('beforebegin', stepHTML);
    
    // Initialiser les boutons
    const newStep = addStepBtn.previousElementSibling;
    initStepButtons(newStep);
    
    // Définir les attributs data-
    if (stepData.options) {
        newStep.dataset.duration = stepData.options.duration;
        newStep.dataset.location = stepData.options.location;
        newStep.dataset.required = stepData.options.required;
    }
}

/**
 * Initialise les boutons d'une étape
 */
function initStepButtons(step) {
    const deleteBtn = step.querySelector('button:first-child');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            if (confirm('Êtes-vous sûr de vouloir supprimer cette étape?')) {
                step.remove();
                reindexSteps();
            }
        });
    }
    
    const secondBtn = step.querySelector('button:last-child');
    if (secondBtn) {
        if (secondBtn.textContent.includes('Ajouter un participant')) {
            secondBtn.addEventListener('click', function() {
                openParticipantModal(step);
            });
        } else if (secondBtn.textContent.includes('Terminé')) {
            secondBtn.addEventListener('click', function() {
                step.classList.remove('completed');
                secondBtn.textContent = 'Ajouter un participant';
                secondBtn.classList.remove('btn-success');
                secondBtn.innerHTML = '<i class="fas fa-user-plus"></i> Ajouter un participant';
                
                // Mettre à jour l'écouteur d'événements
                secondBtn.removeEventListener('click', arguments.callee);
                secondBtn.addEventListener('click', function() {
                    openParticipantModal(step);
                });
            });
        }
    }
    
    // Initialiser les boutons de suppression de participants
    step.querySelectorAll('.remove-participant').forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
            const participantsUl = step.querySelector('.participants-list ul');
            if (participantsUl && participantsUl.children.length === 0) {
                step.querySelector('.participants-list').remove();
            }
        });
    });
}
