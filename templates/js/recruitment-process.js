// Script de gestion du processus de recrutement modulable
document.addEventListener('DOMContentLoaded', function() {
    const processContainer = document.querySelector('.recruitment-steps-container');
    const addStepButton = document.querySelector('.add-step-button');
    let steps = [];
    
    // Étapes prédéfinies (à charger depuis la base de données en production)
    const predefinedSteps = [
        { id: 'cv', name: 'Validation du CV', description: 'Première analyse du profil', icon: 'file-text' },
        { id: 'call', name: 'Call de pré-qualification', description: 'Premier contact téléphonique', icon: 'phone' },
        { id: 'visio', name: 'Entretien visio', description: 'Évaluation des compétences', icon: 'video' },
        { id: 'presentiel', name: 'Entretien présentiel', description: 'Discussion approfondie', icon: 'users' },
        { id: 'test', name: 'Test technique', description: 'Évaluation pratique des compétences', icon: 'code' },
        { id: 'decision', name: 'Décision finale', description: 'Validation et offre', icon: 'check-circle' }
    ];
    
    // Fonction pour initialiser le processus
    function initProcess() {
        // Charger les étapes existantes si elles existent dans localStorage
        const savedSteps = localStorage.getItem('recruitmentSteps');
        steps = savedSteps ? JSON.parse(savedSteps) : [
            { id: 'cv', name: 'Validation du CV', description: 'Première analyse du profil', members: [], required: true, customFields: [] },
            { id: 'call', name: 'Call de pré-qualification', description: 'Premier contact téléphonique', members: [], required: false, customFields: [] },
            { id: 'visio', name: 'Entretien visio', description: 'Évaluation des compétences', members: [], required: true, customFields: [] },
            { id: 'presentiel', name: 'Entretien présentiel', description: 'Discussion approfondie', members: [], required: true, customFields: [] }
        ];
        
        renderSteps();
        initDragAndDrop();
    }
    
    // Fonction pour rendre les étapes
    function renderSteps() {
        processContainer.innerHTML = '';
        
        steps.forEach((step, index) => {
            const stepEl = createStepElement(step, index);
            processContainer.appendChild(stepEl);
        });
        
        updateProgressIndicator();
    }
    
    // Créer un élément d'étape
    function createStepElement(step, index) {
        const stepEl = document.createElement('div');
        stepEl.className = 'recruitment-step';
        stepEl.dataset.id = step.id;
        stepEl.dataset.index = index;
        
        const stepHeader = document.createElement('div');
        stepHeader.className = 'step-header';
        
        const stepContent = document.createElement('div');
        stepContent.className = 'step-content';
        
        // Header avec titre et actions
        stepHeader.innerHTML = `
            <div class="step-title">
                <h3>${step.name}</h3>
                <span class="step-index">${index + 1}</span>
            </div>
            <div class="step-actions">
                <button class="btn-edit-step" data-index="${index}"><i class="fas fa-edit"></i></button>
                ${step.required ? '' : `<button class="btn-remove-step" data-index="${index}"><i class="fas fa-trash"></i></button>`}
                <div class="step-handle"><i class="fas fa-grip-lines"></i></div>
            </div>
        `;
        
        // Contenu de l'étape
        stepContent.innerHTML = `
            <p class="step-description">${step.description}</p>
            <div class="step-members">
                <h4>Participants</h4>
                <div class="members-list">
                    ${step.members && step.members.length ? step.members.map(member => `
                        <div class="member-badge">
                            <span>${member.name}</span>
                            <button class="remove-member" data-step="${index}" data-member="${member.id}">×</button>
                        </div>
                    `).join('') : '<p class="no-members">Aucun participant assigné</p>'}
                </div>
                <button class="btn-assign-member" data-index="${index}">
                    <i class="fas fa-user-plus"></i> Associer un membre
                </button>
            </div>
            
            ${step.customFields && step.customFields.length ? `
                <div class="custom-fields">
                    <h4>Champs personnalisés</h4>
                    <div class="fields-list">
                        ${step.customFields.map(field => `
                            <div class="field-item">
                                <span>${field.name}: ${field.type}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        stepEl.appendChild(stepHeader);
        stepEl.appendChild(stepContent);
        
        // Event listeners
        stepEl.querySelector('.btn-edit-step')?.addEventListener('click', () => editStep(index));
        stepEl.querySelector('.btn-remove-step')?.addEventListener('click', () => removeStep(index));
        stepEl.querySelector('.btn-assign-member')?.addEventListener('click', () => showMemberSelector(index));
        
        stepEl.querySelectorAll('.remove-member').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const memberId = e.target.dataset.member;
                removeMember(index, memberId);
            });
        });
        
        return stepEl;
    }
    
    // Initialiser le drag and drop
    function initDragAndDrop() {
        new Sortable(processContainer, {
            animation: 150,
            handle: '.step-handle',
            ghostClass: 'step-ghost',
            chosenClass: 'step-chosen',
            dragClass: 'step-drag',
            onEnd: function(evt) {
                const oldIndex = evt.oldIndex;
                const newIndex = evt.newIndex;
                
                if (oldIndex !== newIndex) {
                    // Réorganiser les étapes
                    const stepToMove = steps.splice(oldIndex, 1)[0];
                    steps.splice(newIndex, 0, stepToMove);
                    
                    // Mettre à jour l'interface
                    renderSteps();
                    saveSteps();
                }
            }
        });
    }
    
    // Afficher modal d'ajout d'étape
    function showAddStepModal() {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Ajouter une étape</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="predefined-steps">
                        <h3>Étapes prédéfinies</h3>
                        <div class="step-options">
                            ${predefinedSteps.map(step => `
                                <div class="step-option" data-id="${step.id}">
                                    <i class="fas fa-${step.icon}"></i>
                                    <h4>${step.name}</h4>
                                    <p>${step.description}</p>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="custom-step-form">
                        <h3>Ou créer une étape personnalisée</h3>
                        <form id="customStepForm">
                            <div class="form-group">
                                <label for="stepName">Nom de l'étape</label>
                                <input type="text" id="stepName" required>
                            </div>
                            <div class="form-group">
                                <label for="stepDescription">Description</label>
                                <textarea id="stepDescription"></textarea>
                            </div>
                            <button type="submit" class="btn-primary">Créer une étape personnalisée</button>
                        </form>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelectorAll('.step-option').forEach(option => {
            option.addEventListener('click', () => {
                const stepId = option.dataset.id;
                const stepTemplate = predefinedSteps.find(s => s.id === stepId);
                
                // Ajouter l'étape avec un ID unique
                const newStep = {
                    ...stepTemplate,
                    id: `${stepId}-${Date.now()}`,
                    members: [],
                    required: false,
                    customFields: []
                };
                
                steps.push(newStep);
                renderSteps();
                saveSteps();
                
                document.body.removeChild(modal);
            });
        });
        
        modal.querySelector('#customStepForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const stepName = document.getElementById('stepName').value;
            const stepDescription = document.getElementById('stepDescription').value;
            
            const newStep = {
                id: `custom-${Date.now()}`,
                name: stepName,
                description: stepDescription,
                members: [],
                required: false,
                customFields: []
            };
            
            steps.push(newStep);
            renderSteps();
            saveSteps();
            
            document.body.removeChild(modal);
        });
    }
    
    // Éditer une étape
    function editStep(index) {
        const step = steps[index];
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Modifier l'étape</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="editStepForm">
                        <div class="form-group">
                            <label for="editStepName">Nom de l'étape</label>
                            <input type="text" id="editStepName" value="${step.name}" required>
                        </div>
                        <div class="form-group">
                            <label for="editStepDescription">Description</label>
                            <textarea id="editStepDescription">${step.description}</textarea>
                        </div>
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="editStepRequired" ${step.required ? 'checked' : ''}>
                                Étape obligatoire
                            </label>
                        </div>
                        
                        <div class="custom-fields-section">
                            <h3>Champs personnalisés</h3>
                            <div id="customFieldsList">
                                ${step.customFields && step.customFields.map((field, i) => `
                                    <div class="custom-field-item" data-index="${i}">
                                        <span>${field.name} (${field.type})</span>
                                        <button type="button" class="remove-field" data-index="${i}">×</button>
                                    </div>
                                `).join('') || ''}
                            </div>
                            
                            <div class="add-field-form">
                                <div class="form-row">
                                    <div class="form-group">
                                        <input type="text" id="newFieldName" placeholder="Nom du champ">
                                    </div>
                                    <div class="form-group">
                                        <select id="newFieldType">
                                            <option value="text">Texte</option>
                                            <option value="textarea">Zone de texte</option>
                                            <option value="number">Nombre</option>
                                            <option value="date">Date</option>
                                            <option value="file">Fichier</option>
                                            <option value="checkbox">Case à cocher</option>
                                            <option value="radio">Boutons radio</option>
                                            <option value="select">Liste déroulante</option>
                                        </select>
                                    </div>
                                    <button type="button" id="addCustomField">Ajouter</button>
                                </div>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn-primary">Enregistrer les modifications</button>
                    </form>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.querySelectorAll('.remove-field').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const fieldIndex = parseInt(e.target.dataset.index);
                step.customFields.splice(fieldIndex, 1);
                
                // Mettre à jour la liste dans le modal
                document.getElementById('customFieldsList').innerHTML = step.customFields.map((field, i) => `
                    <div class="custom-field-item" data-index="${i}">
                        <span>${field.name} (${field.type})</span>
                        <button type="button" class="remove-field" data-index="${i}">×</button>
                    </div>
                `).join('');
                
                // Re-attacher les event listeners
                modal.querySelectorAll('.remove-field').forEach(newBtn => {
                    newBtn.addEventListener('click', (e) => {
                        const fieldIndex = parseInt(e.target.dataset.index);
                        step.customFields.splice(fieldIndex, 1);
                    });
                });
            });
        });
        
        // Ajouter un champ personnalisé
        modal.querySelector('#addCustomField').addEventListener('click', () => {
            const fieldName = document.getElementById('newFieldName').value;
            const fieldType = document.getElementById('newFieldType').value;
            
            if (fieldName.trim() === '') {
                alert('Veuillez saisir un nom pour le champ');
                return;
            }
            
            if (!step.customFields) {
                step.customFields = [];
            }
            
            step.customFields.push({
                name: fieldName,
                type: fieldType
            });
            
            // Mettre à jour la liste
            document.getElementById('customFieldsList').innerHTML = step.customFields.map((field, i) => `
                <div class="custom-field-item" data-index="${i}">
                    <span>${field.name} (${field.type})</span>
                    <button type="button" class="remove-field" data-index="${i}">×</button>
                </div>
            `).join('');
            
            // Re-attacher les event listeners
            modal.querySelectorAll('.remove-field').forEach(newBtn => {
                newBtn.addEventListener('click', (e) => {
                    const fieldIndex = parseInt(e.target.dataset.index);
                    step.customFields.splice(fieldIndex, 1);
                    e.target.parentElement.remove();
                });
            });
            
            // Réinitialiser le formulaire
            document.getElementById('newFieldName').value = '';
            document.getElementById('newFieldType').value = 'text';
        });
        
        // Soumettre le formulaire
        modal.querySelector('#editStepForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Mettre à jour les données de l'étape
            steps[index] = {
                ...step,
                name: document.getElementById('editStepName').value,
                description: document.getElementById('editStepDescription').value,
                required: document.getElementById('editStepRequired').checked
            };
            
            renderSteps();
            saveSteps();
            
            document.body.removeChild(modal);
        });
    }
    
    // Supprimer une étape
    function removeStep(index) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette étape ?')) {
            steps.splice(index, 1);
            renderSteps();
            saveSteps();
        }
    }
    
    // Afficher sélecteur de membres
    function showMemberSelector(stepIndex) {
        // Simuler une liste de membres (à remplacer par des données réelles)
        const teamMembers = [
            { id: 1, name: 'Sophie Martin', role: 'RH' },
            { id: 2, name: 'Thomas Dubois', role: 'Manager' },
            { id: 3, name: 'Julie Lambert', role: 'Tech Lead' },
            { id: 4, name: 'Maxime Leroux', role: 'CTO' },
            { id: 5, name: 'Camille Petit', role: 'Designer' }
        ];
        
        const step = steps[stepIndex];
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Associer des membres à l'étape "${step.name}"</h2>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="current-members">
                        <h3>Membres déjà associés</h3>
                        <div class="members-container">
                            ${step.members && step.members.length ? step.members.map(member => `
                                <div class="member-item selected">
                                    <input type="checkbox" id="member-${member.id}" data-id="${member.id}" checked>
                                    <label for="member-${member.id}">
                                        <span class="member-name">${member.name}</span>
                                        <span class="member-role">${member.role || ''}</span>
                                    </label>
                                </div>
                            `).join('') : '<p>Aucun membre associé</p>'}
                        </div>
                    </div>
                    
                    <div class="available-members">
                        <h3>Membres disponibles</h3>
                        <input type="text" class="search-members" placeholder="Rechercher un membre...">
                        <div class="members-container">
                            ${teamMembers
                                .filter(m => !step.members || !step.members.some(sm => sm.id === m.id))
                                .map(member => `
                                    <div class="member-item">
                                        <input type="checkbox" id="member-${member.id}" data-id="${member.id}">
                                        <label for="member-${member.id}">
                                            <span class="member-name">${member.name}</span>
                                            <span class="member-role">${member.role || ''}</span>
                                        </label>
                                    </div>
                                `).join('')}
                        </div>
                    </div>
                    
                    <button class="btn-primary" id="saveMembersBtn">Enregistrer</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Event listeners
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        // Recherche de membres
        modal.querySelector('.search-members').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const memberItems = modal.querySelectorAll('.available-members .member-item');
            
            memberItems.forEach(item => {
                const memberName = item.querySelector('.member-name').textContent.toLowerCase();
                const memberRole = item.querySelector('.member-role').textContent.toLowerCase();
                
                if (memberName.includes(searchTerm) || memberRole.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
        
        // Enregistrer les membres sélectionnés
        modal.querySelector('#saveMembersBtn').addEventListener('click', () => {
            // Récupérer tous les membres sélectionnés
            const selectedMemberIds = Array.from(
                modal.querySelectorAll('input[type="checkbox"]:checked')
            ).map(cb => parseInt(cb.dataset.id));
            
            // Mettre à jour les membres de l'étape
            steps[stepIndex].members = teamMembers.filter(m => selectedMemberIds.includes(m.id));
            
            renderSteps();
            saveSteps();
            
            document.body.removeChild(modal);
        });
    }
    
    // Supprimer un membre d'une étape
    function removeMember(stepIndex, memberId) {
        const step = steps[stepIndex];
        
        if (step.members) {
            step.members = step.members.filter(m => m.id != memberId);
            renderSteps();
            saveSteps();
        }
    }
    
    // Sauvegarder les étapes
    function saveSteps() {
        localStorage.setItem('recruitmentSteps', JSON.stringify(steps));
    }
    
    // Mettre à jour l'indicateur de progression
    function updateProgressIndicator() {
        const totalSteps = steps.length;
        const progressBar = document.querySelector('.progress-bar');
        const etapeIndicator = document.querySelector('.step-indicator');
        
        if (progressBar) {
            progressBar.style.width = `${(4 / totalSteps) * 100}%`;
        }
        
        if (etapeIndicator) {
            etapeIndicator.textContent = `Étape 4/${totalSteps}`;
        }
    }
    
    // Initialiser les événements
    function initEvents() {
        // Bouton d'ajout d'étape
        addStepButton.addEventListener('click', showAddStepModal);
    }
    
    // Initialiser l'application
    initProcess();
    initEvents();
});