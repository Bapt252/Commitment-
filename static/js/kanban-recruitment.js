/**
 * Système Kanban pour la gestion des recrutements
 * Ce script gère les fonctionnalités de drag-and-drop et la gestion des candidats
 * dans un tableau Kanban pour le suivi du processus de recrutement.
 */

// Données simulées (dans une application réelle, ces données viendraient d'une API ou d'une base de données)
let jobOffers = [
    {
        id: 'job1',
        title: 'Développeur Full-Stack',
        salary: '45-55K€',
        location: 'Paris, France',
        type: 'cdi',
        deadline: '2025-04-30',
        description: 'Nous recherchons un développeur Full-Stack expérimenté pour rejoindre notre équipe technique.',
        skills: 'JavaScript, React, Node.js, MongoDB, Express'
    }
];

let candidates = [
    {
        id: 'candidate1',
        jobId: 'job1',
        column: 'candidatures',
        name: 'Marie Dupont',
        email: 'marie.dupont@email.com',
        phone: '+33 6 12 34 56 78',
        experience: '5 ans d\'expérience',
        matching: 'high',
        notes: 'Candidate très prometteuse avec une bonne expérience dans les technologies requises.',
        date: '2025-03-20'
    },
    {
        id: 'candidate2',
        jobId: 'job1',
        column: 'candidatures',
        name: 'Thomas Martin',
        email: 'thomas.martin@email.com',
        phone: '+33 6 23 45 67 89',
        experience: '3 ans d\'expérience',
        matching: 'medium',
        notes: 'Bonnes compétences techniques mais manque d\'expérience sur React.',
        date: '2025-03-18'
    },
    {
        id: 'candidate3',
        jobId: 'job1',
        column: 'candidatures',
        name: 'Julie Lefebvre',
        email: 'julie.lefebvre@email.com',
        phone: '+33 6 34 56 78 90',
        experience: '7 ans d\'expérience',
        matching: 'high',
        notes: 'Excellente expérience, notamment en architecture logicielle.',
        date: '2025-03-15'
    },
    {
        id: 'candidate4',
        jobId: 'job1',
        column: 'pre-selection',
        name: 'David Bernard',
        email: 'david.bernard@email.com',
        phone: '+33 6 45 67 89 01',
        experience: '4 ans d\'expérience',
        matching: 'high',
        notes: 'Très bon développeur front-end avec une bonne connaissance de React.',
        date: '2025-03-10'
    },
    {
        id: 'candidate5',
        jobId: 'job1',
        column: 'pre-selection',
        name: 'Sophie Dubois',
        email: 'sophie.dubois@email.com',
        phone: '+33 6 56 78 90 12',
        experience: '6 ans d\'expérience',
        matching: 'medium',
        notes: 'Solide expérience en développement back-end Node.js.',
        date: '2025-03-08'
    },
    {
        id: 'candidate6',
        jobId: 'job1',
        column: 'entretiens',
        name: 'Pierre Moreau',
        email: 'pierre.moreau@email.com',
        phone: '+33 6 67 89 01 23',
        experience: '8 ans d\'expérience',
        matching: 'high',
        notes: 'Expert en architecture microservices et DevOps.',
        date: '2025-03-05'
    }
];

// Interviews planifiés
let interviews = [];

document.addEventListener('DOMContentLoaded', function() {
    initKanban();
    setupEventListeners();
});

/**
 * Initialise le système Kanban
 */
function initKanban() {
    // 1. Mise à jour des filtres de job
    updateJobFilters();
    
    // 2. Chargement des candidats dans le Kanban
    renderCandidates();
    
    // 3. Mise à jour des compteurs
    updateColumnCounts();
}

/**
 * Met à jour les options de filtrage par offre d'emploi
 */
function updateJobFilters() {
    const filterSelect = document.getElementById('filter-job-offers');
    
    // Vider les options existantes sauf "Toutes les offres"
    while (filterSelect.options.length > 1) {
        filterSelect.remove(1);
    }
    
    // Ajouter les offres d'emploi comme options
    jobOffers.forEach(job => {
        const option = document.createElement('option');
        option.value = job.id;
        option.textContent = job.title;
        filterSelect.appendChild(option);
    });
}

/**
 * Affiche tous les candidats dans leurs colonnes respectives
 */
function renderCandidates() {
    // Réinitialiser toutes les colonnes (sauf l'élément "Ajouter un candidat")
    document.querySelectorAll('.kanban-cards').forEach(column => {
        // Conserver uniquement l'élément "Ajouter un candidat"
        const addCandidateBtn = column.querySelector('.add-candidate');
        column.innerHTML = '';
        if (addCandidateBtn) {
            column.appendChild(addCandidateBtn);
        }
    });
    
    // Afficher chaque candidat dans sa colonne
    candidates.forEach(candidate => {
        const columnElement = document.querySelector(`.kanban-cards[data-column="${candidate.column}"]`);
        if (columnElement) {
            // Insérer le candidat avant le bouton "Ajouter un candidat"
            const addCandidateBtn = columnElement.querySelector('.add-candidate');
            columnElement.insertBefore(createCandidateCard(candidate), addCandidateBtn);
        }
    });
}

/**
 * Crée une carte de candidat à partir des données du candidat
 * @param {Object} candidate Les données du candidat
 * @returns {HTMLElement} Élément DOM de la carte
 */
function createCandidateCard(candidate) {
    const card = document.createElement('div');
    card.className = 'candidate-card';
    card.setAttribute('draggable', 'true');
    card.setAttribute('data-candidate-id', candidate.id);
    
    // Indicateur de correspondance
    const indicatorClass = candidate.matching === 'high' ? 'indicator-high' : 
                          candidate.matching === 'medium' ? 'indicator-medium' : 
                          'indicator-low';
    
    card.innerHTML = `
        <div class="candidate-card-indicator ${indicatorClass}"></div>
        <div class="candidate-name">${candidate.name}</div>
        <div class="candidate-details">
            <div class="candidate-detail">
                <i class="fas fa-envelope candidate-detail-icon"></i>
                ${candidate.email}
            </div>
            <div class="candidate-detail">
                <i class="fas fa-phone candidate-detail-icon"></i>
                ${candidate.phone}
            </div>
            <div class="candidate-detail">
                <i class="fas fa-briefcase candidate-detail-icon"></i>
                ${candidate.experience}
            </div>
        </div>
        <div class="candidate-actions">
            <div class="action-buttons">
                <button class="action-button view-profile-btn tooltip" data-candidate-id="${candidate.id}">
                    <i class="fas fa-user"></i>
                    <span class="tooltip-text">Voir le profil</span>
                </button>
                <button class="action-button send-message-btn tooltip" data-candidate-id="${candidate.id}">
                    <i class="fas fa-comment"></i>
                    <span class="tooltip-text">Envoyer un message</span>
                </button>
                <button class="action-button schedule-interview-btn tooltip" data-candidate-id="${candidate.id}">
                    <i class="fas fa-calendar"></i>
                    <span class="tooltip-text">Planifier un entretien</span>
                </button>
            </div>
            <div class="candidate-date">${formatDate(candidate.date)}</div>
        </div>
    `;
    
    return card;
}

/**
 * Met à jour les compteurs de candidats de chaque colonne
 */
function updateColumnCounts() {
    document.querySelectorAll('.kanban-column').forEach(column => {
        const columnName = column.getAttribute('data-column');
        const count = column.querySelectorAll('.candidate-card').length;
        
        const countElement = column.querySelector('.kanban-column-count');
        if (countElement) {
            countElement.textContent = count;
        }
    });
}

/**
 * Configuration des écouteurs d'événements pour l'interface
 */
function setupEventListeners() {
    // 1. Événements pour drag & drop
    setupDragAndDrop();
    
    // 2. Événements pour les modales
    setupModals();
    
    // 3. Événements pour filtrer et rechercher
    setupFiltersAndSearch();
    
    // 4. Événements pour les boutons d'action
    setupActionButtons();
}

/**
 * Configure les événements de drag & drop pour les cartes de candidats
 */
function setupDragAndDrop() {
    // Variables pour stocker les éléments en cours de drag & drop
    let draggedElement = null;
    
    // 1. Ajouter les écouteurs d'événements pour les cartes de candidats existantes
    document.querySelectorAll('.candidate-card').forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });
    
    // 2. Ajouter les écouteurs d'événements pour les zones de drop (colonnes)
    document.querySelectorAll('.kanban-cards').forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('dragenter', handleDragEnter);
        column.addEventListener('dragleave', handleDragLeave);
        column.addEventListener('drop', handleDrop);
    });
    
    // Fonction pour gérer le début du drag
    function handleDragStart(e) {
        draggedElement = this;
        this.classList.add('dragging');
        e.dataTransfer.setData('text/plain', this.getAttribute('data-candidate-id'));
        e.dataTransfer.effectAllowed = 'move';
    }
    
    // Fonction pour gérer la fin du drag
    function handleDragEnd() {
        this.classList.remove('dragging');
        document.querySelectorAll('.kanban-cards').forEach(column => {
            column.classList.remove('drag-over');
        });
    }
    
    // Fonction pour gérer le survol d'une zone de drop
    function handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        return false;
    }
    
    // Fonction pour gérer l'entrée dans une zone de drop
    function handleDragEnter(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    }
    
    // Fonction pour gérer la sortie d'une zone de drop
    function handleDragLeave() {
        this.classList.remove('drag-over');
    }
    
    // Fonction pour gérer le drop
    function handleDrop(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        
        const candidateId = e.dataTransfer.getData('text/plain');
        const card = document.querySelector(`[data-candidate-id="${candidateId}"]`);
        const targetColumn = this;
        const columnName = targetColumn.getAttribute('data-column');
        
        if (card && targetColumn) {
            // Ajouter la carte avant le bouton "Ajouter un candidat"
            const addCandidateBtn = targetColumn.querySelector('.add-candidate');
            targetColumn.insertBefore(card, addCandidateBtn);
            
            // Mettre à jour les données
            const candidateIndex = candidates.findIndex(c => c.id === candidateId);
            if (candidateIndex !== -1) {
                candidates[candidateIndex].column = columnName;
                
                // Afficher une notification
                showNotification('Candidat déplacé avec succès', 'success');
                
                // Mettre à jour les compteurs
                updateColumnCounts();
            }
        }
        
        return false;
    }
}

/**
 * Configure les événements pour les modales
 */
function setupModals() {
    // 1. Modale d'offre d'emploi
    const jobModal = document.getElementById('job-offer-modal');
    const addJobButtons = document.querySelectorAll('#add-job-offer-btn, #add-job-offer-bottom');
    const closeJobModal = document.getElementById('close-job-modal');
    const cancelJobBtn = document.getElementById('cancel-job-btn');
    const jobForm = document.getElementById('job-offer-form');
    
    // Ouvrir la modale d'offre d'emploi
    addJobButtons.forEach(button => {
        button.addEventListener('click', () => {
            document.getElementById('job-modal-title').textContent = 'Ajouter une offre d\'emploi';
            document.getElementById('job-id').value = '';
            jobForm.reset();
            jobModal.classList.add('show');
        });
    });
    
    // Fermer la modale d'offre d'emploi
    closeJobModal.addEventListener('click', () => jobModal.classList.remove('show'));
    cancelJobBtn.addEventListener('click', () => jobModal.classList.remove('show'));
    
    // Soumettre le formulaire d'offre d'emploi
    jobForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const jobId = document.getElementById('job-id').value || 'job' + (jobOffers.length + 1);
        const jobData = {
            id: jobId,
            title: document.getElementById('job-title').value,
            salary: document.getElementById('job-salary').value,
            location: document.getElementById('job-location').value,
            type: document.getElementById('job-type').value,
            deadline: document.getElementById('job-deadline').value,
            description: document.getElementById('job-description').value,
            skills: document.getElementById('job-skills').value
        };
        
        // Vérifier si c'est une création ou une mise à jour
        const existingJobIndex = jobOffers.findIndex(job => job.id === jobId);
        if (existingJobIndex !== -1) {
            // Mise à jour
            jobOffers[existingJobIndex] = jobData;
            showNotification('Offre d\'emploi mise à jour avec succès', 'success');
        } else {
            // Création
            jobOffers.push(jobData);
            // Ajouter l'offre d'emploi à l'interface
            addJobOfferToUI(jobData);
            showNotification('Nouvelle offre d\'emploi créée avec succès', 'success');
        }
        
        // Mettre à jour les filtres
        updateJobFilters();
        
        // Fermer la modale
        jobModal.classList.remove('show');
    });
    
    // 2. Modale de candidat
    const candidateModal = document.getElementById('candidate-modal');
    const closeCandidateModal = document.getElementById('close-candidate-modal');
    const cancelCandidateBtn = document.getElementById('cancel-candidate-btn');
    const candidateForm = document.getElementById('candidate-form');
    
    // Écouter les clics sur "Ajouter un candidat"
    document.addEventListener('click', (e) => {
        if (e.target.closest('.add-candidate')) {
            const addCandidateBtn = e.target.closest('.add-candidate');
            const column = addCandidateBtn.getAttribute('data-column');
            const jobId = addCandidateBtn.closest('.job-offer-container').getAttribute('data-job-id');
            
            // Réinitialiser et configurer le formulaire
            document.getElementById('candidate-modal-title').textContent = 'Ajouter un candidat';
            document.getElementById('candidate-id').value = '';
            document.getElementById('candidate-column').value = column;
            document.getElementById('candidate-job-id').value = jobId;
            candidateForm.reset();
            
            // Afficher la modale
            candidateModal.classList.add('show');
        }
    });
    
    // Fermer la modale de candidat
    closeCandidateModal.addEventListener('click', () => candidateModal.classList.remove('show'));
    cancelCandidateBtn.addEventListener('click', () => candidateModal.classList.remove('show'));
    
    // Soumettre le formulaire de candidat
    candidateForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const candidateId = document.getElementById('candidate-id').value || 'candidate' + (candidates.length + 1);
        const candidateData = {
            id: candidateId,
            jobId: document.getElementById('candidate-job-id').value,
            column: document.getElementById('candidate-column').value,
            name: document.getElementById('candidate-name').value,
            email: document.getElementById('candidate-email').value,
            phone: document.getElementById('candidate-phone').value,
            experience: document.getElementById('candidate-experience').value,
            matching: document.getElementById('candidate-matching').value,
            notes: document.getElementById('candidate-notes').value,
            date: getCurrentDate()
        };
        
        // Vérifier si c'est une création ou une mise à jour
        const existingCandidateIndex = candidates.findIndex(c => c.id === candidateId);
        if (existingCandidateIndex !== -1) {
            // Mise à jour
            candidates[existingCandidateIndex] = candidateData;
            showNotification('Candidat mis à jour avec succès', 'success');
        } else {
            // Création
            candidates.push(candidateData);
            showNotification('Nouveau candidat ajouté avec succès', 'success');
        }
        
        // Rafraîchir l'affichage
        renderCandidates();
        updateColumnCounts();
        setupDragAndDrop();
        
        // Fermer la modale
        candidateModal.classList.remove('show');
    });
    
    // 3. Modale de profil
    const profileModal = document.getElementById('profile-modal');
    const closeProfileModal = document.getElementById('close-profile-modal');
    const backToKanbanBtn = document.getElementById('back-to-kanban-btn');
    
    closeProfileModal.addEventListener('click', () => profileModal.classList.remove('show'));
    backToKanbanBtn.addEventListener('click', () => profileModal.classList.remove('show'));
    
    // 4. Modale d'entretien
    const interviewModal = document.getElementById('interview-modal');
    const closeInterviewModal = document.getElementById('close-interview-modal');
    const cancelInterviewBtn = document.getElementById('cancel-interview-btn');
    const interviewForm = document.getElementById('interview-form');
    
    closeInterviewModal.addEventListener('click', () => interviewModal.classList.remove('show'));
    cancelInterviewBtn.addEventListener('click', () => interviewModal.classList.remove('show'));
    
    // Soumettre le formulaire d'entretien
    interviewForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const candidateId = document.getElementById('interview-candidate-id').value;
        const interviewData = {
            id: 'interview' + (interviews.length + 1),
            candidateId: candidateId,
            candidateName: document.getElementById('interview-candidate-name').value,
            date: document.getElementById('interview-date').value,
            time: document.getElementById('interview-time').value,
            type: document.getElementById('interview-type').value,
            participants: document.getElementById('interview-participants').value,
            notes: document.getElementById('interview-notes').value
        };
        
        // Ajouter l'entretien
        interviews.push(interviewData);
        
        // Trouver le candidat et le déplacer vers la colonne d'entretiens
        const candidateIndex = candidates.findIndex(c => c.id === candidateId);
        if (candidateIndex !== -1 && candidates[candidateIndex].column !== 'entretiens') {
            candidates[candidateIndex].column = 'entretiens';
            
            // Rafraîchir l'affichage
            renderCandidates();
            updateColumnCounts();
            setupDragAndDrop();
        }
        
        showNotification('Entretien planifié avec succès', 'success');
        
        // Fermer la modale
        interviewModal.classList.remove('show');
    });
    
    // 5. Notification
    const notification = document.getElementById('notification');
    const closeNotification = document.getElementById('close-notification');
    
    closeNotification.addEventListener('click', () => notification.classList.remove('show'));
}

/**
 * Configure les événements pour les filtres et la recherche
 */
function setupFiltersAndSearch() {
    const searchInput = document.getElementById('search-candidates');
    const filterSelect = document.getElementById('filter-job-offers');
    
    // Rechercher des candidats
    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.toLowerCase();
        
        document.querySelectorAll('.candidate-card').forEach(card => {
            const candidateName = card.querySelector('.candidate-name').textContent.toLowerCase();
            const candidateEmail = card.querySelector('.candidate-detail').textContent.toLowerCase();
            
            if (candidateName.includes(searchTerm) || candidateEmail.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    });
    
    // Filtrer par offre d'emploi
    filterSelect.addEventListener('change', () => {
        const selectedJobId = filterSelect.value;
        
        document.querySelectorAll('.job-offer-container').forEach(jobContainer => {
            const jobId = jobContainer.getAttribute('data-job-id');
            
            if (selectedJobId === 'all' || selectedJobId === jobId) {
                jobContainer.style.display = '';
            } else {
                jobContainer.style.display = 'none';
            }
        });
    });
}

/**
 * Configure les événements pour les boutons d'action
 */
function setupActionButtons() {
    // Gérer les clics sur les boutons d'action des cartes
    document.addEventListener('click', (e) => {
        // 1. Voir le profil
        if (e.target.closest('.view-profile-btn')) {
            const button = e.target.closest('.view-profile-btn');
            const candidateId = button.getAttribute('data-candidate-id');
            const candidate = candidates.find(c => c.id === candidateId);
            
            if (candidate) {
                // Remplir la modale de profil avec les informations du candidat
                document.getElementById('profile-name').textContent = candidate.name;
                
                const profileContent = document.getElementById('profile-content');
                profileContent.innerHTML = `
                    <div class="profile-section">
                        <h3>Informations de contact</h3>
                        <p><i class="fas fa-envelope"></i> ${candidate.email}</p>
                        <p><i class="fas fa-phone"></i> ${candidate.phone}</p>
                    </div>
                    
                    <div class="profile-section">
                        <h3>Informations professionnelles</h3>
                        <p><i class="fas fa-briefcase"></i> ${candidate.experience}</p>
                        <p><i class="fas fa-calendar-alt"></i> Candidature reçue le ${formatDate(candidate.date)}</p>
                    </div>
                    
                    <div class="profile-section">
                        <h3>Notes</h3>
                        <p>${candidate.notes || 'Aucune note pour ce candidat.'}</p>
                    </div>
                    
                    ${interviews.some(i => i.candidateId === candidateId) ? `
                    <div class="profile-section">
                        <h3>Entretiens planifiés</h3>
                        <ul class="interview-list">
                            ${interviews.filter(i => i.candidateId === candidateId).map(interview => `
                                <li>
                                    <div class="interview-date">
                                        <i class="fas fa-calendar-day"></i> ${formatDate(interview.date)} à ${interview.time}
                                    </div>
                                    <div class="interview-type">
                                        <i class="fas fa-${interview.type === 'phone' ? 'phone' : interview.type === 'video' ? 'video' : 'building'}"></i>
                                        ${interview.type === 'phone' ? 'Entretien téléphonique' : interview.type === 'video' ? 'Visioconférence' : 'Entretien en présentiel'}
                                    </div>
                                    ${interview.participants ? `<div class="interview-participants">
                                        <i class="fas fa-users"></i> ${interview.participants}
                                    </div>` : ''}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    ` : ''}
                `;
                
                // Ajouter le bouton pour aller au profil complet
                const profileActions = document.querySelector('.profile-actions');
                profileActions.innerHTML = `
                    <button type="button" class="btn" id="back-to-kanban-btn">Retour</button>
                    <a href="candidate-page.html" class="btn btn-primary">Profil complet</a>
                `;
                
                // Réinstaller l'action sur le bouton retour
                document.getElementById('back-to-kanban-btn').addEventListener('click', () => {
                    document.getElementById('profile-modal').classList.remove('show');
                });
                
                // Afficher la modale
                document.getElementById('profile-modal').classList.add('show');
            }
        }
        
        // 2. Envoyer un message
        if (e.target.closest('.send-message-btn')) {
            const button = e.target.closest('.send-message-btn');
            const candidateId = button.getAttribute('data-candidate-id');
            const candidate = candidates.find(c => c.id === candidateId);
            
            if (candidate) {
                // Dans une application réelle, cela ouvrirait une messagerie
                showNotification(`Ouverture de la messagerie avec ${candidate.name}`, 'info');
            }
        }
        
        // 3. Planifier un entretien
        if (e.target.closest('.schedule-interview-btn')) {
            const button = e.target.closest('.schedule-interview-btn');
            const candidateId = button.getAttribute('data-candidate-id');
            const candidate = candidates.find(c => c.id === candidateId);
            
            if (candidate) {
                // Remplir le formulaire d'entretien
                document.getElementById('interview-candidate-id').value = candidateId;
                document.getElementById('interview-candidate-name').value = candidate.name;
                
                // Date par défaut (jour suivant)
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                document.getElementById('interview-date').value = formatDateForInput(tomorrow);
                
                // Heure par défaut (14h00)
                document.getElementById('interview-time').value = '14:00';
                
                // Afficher la modale
                document.getElementById('interview-modal').classList.add('show');
            }
        }
    });
}

/**
 * Ajoute une nouvelle offre d'emploi à l'interface
 * @param {Object} jobData Les données de l'offre d'emploi
 */
function addJobOfferToUI(jobData) {
    const kanbanContainer = document.getElementById('kanban-container');
    
    // Créer le conteneur de l'offre d'emploi
    const jobOfferContainer = document.createElement('div');
    jobOfferContainer.className = 'job-offer-container';
    jobOfferContainer.setAttribute('data-job-id', jobData.id);
    
    // Formatage de la date limite
    const deadlineDisplay = jobData.deadline ? formatDate(jobData.deadline) : 'Non défini';
    
    // Construire le contenu HTML
    jobOfferContainer.innerHTML = `
        <div class="job-offer-header">
            <div class="job-offer-title">
                <i class="fas fa-briefcase"></i>
                <h3>${jobData.title}</h3>
            </div>
            <div class="job-offer-info">
                ${jobData.salary ? `
                    <div class="job-offer-salary">
                        <i class="fas fa-euro-sign"></i> ${jobData.salary}
                    </div>
                ` : ''}
                ${jobData.location ? `
                    <div class="job-offer-location">
                        <i class="fas fa-map-marker-alt"></i> ${jobData.location}
                    </div>
                ` : ''}
                <div class="job-offer-deadline">
                    <i class="fas fa-calendar-alt"></i> ${deadlineDisplay}
                </div>
            </div>
        </div>
        
        <div class="job-kanban-container">
            <!-- Colonnes du Kanban -->
            <div class="kanban-column" data-column="candidatures">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-file-alt"></i> Candidatures
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="candidatures">
                    <div class="add-candidate" data-column="candidatures">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
            
            <div class="kanban-column" data-column="pre-selection">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-check"></i> Pré-sélection
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="pre-selection">
                    <div class="add-candidate" data-column="pre-selection">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
            
            <div class="kanban-column" data-column="entretiens">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-calendar-check"></i> Entretiens
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="entretiens">
                    <div class="add-candidate" data-column="entretiens">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
            
            <div class="kanban-column" data-column="tests">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-tasks"></i> Tests techniques
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="tests">
                    <div class="add-candidate" data-column="tests">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
            
            <div class="kanban-column" data-column="decision">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-gavel"></i> Décision finale
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="decision">
                    <div class="add-candidate" data-column="decision">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
            
            <div class="kanban-column" data-column="embauche">
                <div class="kanban-column-header">
                    <div class="kanban-column-title">
                        <i class="fas fa-handshake"></i> Embauche
                        <span class="kanban-column-count">0</span>
                    </div>
                </div>
                <div class="kanban-cards" data-column="embauche">
                    <div class="add-candidate" data-column="embauche">
                        <i class="fas fa-plus"></i> Ajouter un candidat
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Ajouter au DOM
    kanbanContainer.appendChild(jobOfferContainer);
    
    // Configurer les événements de drag & drop
    setupDragAndDrop();
}

/**
 * Affiche une notification à l'utilisateur
 * @param {string} message Le message à afficher
 * @param {string} type Le type de notification (success, info, warning, error)
 */
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notification-message');
    const notificationIcon = notification.querySelector('.notification-icon i');
    
    // Définir le message
    notificationMessage.textContent = message;
    
    // Définir l'icône et la classe en fonction du type
    notification.className = 'notification';
    switch (type) {
        case 'success':
            notification.classList.add('notification-success');
            notificationIcon.className = 'fas fa-check-circle';
            break;
        case 'warning':
            notification.classList.add('notification-warning');
            notificationIcon.className = 'fas fa-exclamation-triangle';
            break;
        case 'error':
            notification.classList.add('notification-error');
            notificationIcon.className = 'fas fa-times-circle';
            break;
        default: // info
            notification.classList.add('notification-info');
            notificationIcon.className = 'fas fa-info-circle';
            break;
    }
    
    // Afficher la notification
    notification.classList.add('show');
    
    // Masquer automatiquement après 5 secondes
    setTimeout(() => {
        notification.classList.remove('show');
    }, 5000);
}

/**
 * Formate une date au format JJ/MM/AAAA
 * @param {string} dateStr Chaîne de date (AAAA-MM-JJ ou JJ/MM/AAAA)
 * @returns {string} Date formatée
 */
function formatDate(dateStr) {
    // Si la date est déjà au format JJ/MM/AAAA, la retourner telle quelle
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(dateStr)) {
        return dateStr;
    }
    
    // Sinon, convertir de AAAA-MM-JJ à JJ/MM/AAAA
    try {
        const date = new Date(dateStr);
        return `${String(date.getDate()).padStart(2, '0')}/${String(date.getMonth() + 1).padStart(2, '0')}/${date.getFullYear()}`;
    } catch (e) {
        return dateStr;
    }
}

/**
 * Formate une date pour un champ input date (AAAA-MM-JJ)
 * @param {Date} date Objet Date
 * @returns {string} Date formatée pour input
 */
function formatDateForInput(date) {
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

/**
 * Retourne la date actuelle au format AAAA-MM-JJ
 * @returns {string} Date actuelle
 */
function getCurrentDate() {
    const now = new Date();
    return formatDateForInput(now);
}

// Ajouter des styles supplémentaires pour les modales et autres éléments d'interface
// Ces styles complètent ceux du fichier CSS principal
const styleElement = document.createElement('style');
styleElement.textContent = `
    /* Styles pour les modales */
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        overflow-y: auto;
        justify-content: center;
        align-items: center;
        padding: var(--spacing-lg);
    }
    
    .modal.show {
        display: flex;
    }
    
    .modal-content {
        background-color: var(--white);
        border-radius: var(--radius-lg);
        width: 100%;
        max-width: 600px;
        box-shadow: var(--shadow-lg);
        overflow: hidden;
        max-height: 90vh;
        display: flex;
        flex-direction: column;
    }
    
    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-lg);
        background-color: var(--primary-light);
        border-bottom: 1px solid var(--primary);
    }
    
    .modal-header h2 {
        margin: 0;
        color: var(--primary-dark);
        font-size: 1.25rem;
    }
    
    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        color: var(--gray-600);
        cursor: pointer;
        transition: var(--transition-fast);
    }
    
    .modal-close:hover {
        color: var(--primary);
    }
    
    .modal-body {
        padding: var(--spacing-lg);
        overflow-y: auto;
    }
    
    /* Styles de formulaire */
    .form-group {
        margin-bottom: var(--spacing-lg);
    }
    
    .form-row {
        display: flex;
        gap: var(--spacing-lg);
        margin-bottom: var(--spacing-lg);
    }
    
    .form-row .form-group {
        flex: 1;
        margin-bottom: 0;
    }
    
    label {
        display: block;
        margin-bottom: var(--spacing-xs);
        font-weight: 500;
        color: var(--gray-700);
    }
    
    input[type="text"],
    input[type="email"],
    input[type="tel"],
    input[type="date"],
    input[type="time"],
    textarea,
    select {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid var(--gray-300);
        border-radius: var(--radius-sm);
        font-size: 0.95rem;
        transition: var(--transition-fast);
    }
    
    input[type="text"]:focus,
    input[type="email"]:focus,
    input[type="tel"]:focus,
    input[type="date"]:focus,
    input[type="time"]:focus,
    textarea:focus,
    select:focus {
        border-color: var(--primary);
        outline: none;
        box-shadow: 0 0 0 2px var(--primary-light);
    }
    
    small {
        display: block;
        margin-top: var(--spacing-xs);
        color: var(--gray-500);
        font-size: 0.8rem;
    }
    
    .form-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-md);
        margin-top: var(--spacing-lg);
    }
    
    /* Styles pour le profil */
    .profile-section {
        margin-bottom: var(--spacing-lg);
    }
    
    .profile-section h3 {
        margin-bottom: var(--spacing-sm);
        color: var(--gray-700);
        font-size: 1rem;
        border-bottom: 1px solid var(--gray-200);
        padding-bottom: var(--spacing-xs);
    }
    
    .profile-section p {
        margin-bottom: var(--spacing-sm);
        color: var(--gray-800);
    }
    
    .profile-section i {
        width: 20px;
        color: var(--primary);
        margin-right: var(--spacing-sm);
    }
    
    .interview-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .interview-list li {
        background-color: var(--gray-100);
        border-radius: var(--radius-sm);
        padding: var(--spacing-md);
        margin-bottom: var(--spacing-sm);
    }
    
    .interview-list li div {
        margin-bottom: var(--spacing-xs);
    }
    
    .profile-actions {
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-md);
        margin-top: var(--spacing-lg);
    }
    
    /* Styles pour la page */
    .page-header {
        margin-bottom: var(--spacing-xl);
    }
    
    .page-header h1 {
        margin-bottom: var(--spacing-xs);
    }
    
    .page-header p {
        color: var(--gray-600);
        margin-bottom: var(--spacing-lg);
    }
    
    .actions {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--spacing-md);
    }
    
    .search-filter {
        display: flex;
        gap: var(--spacing-md);
        flex-grow: 1;
        max-width: 600px;
    }
    
    /* Styles responsifs */
    @media (max-width: 768px) {
        .form-row {
            flex-direction: column;
            gap: var(--spacing-md);
        }
        
        .actions {
            flex-direction: column;
            align-items: stretch;
        }
        
        .search-filter {
            flex-direction: column;
            max-width: none;
        }
        
        .modal-content {
            width: 95%;
        }
    }
`;

document.head.appendChild(styleElement);