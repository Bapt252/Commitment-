// Script pour afficher les opportunités sélectionnées
document.addEventListener('DOMContentLoaded', function() {
    console.log('Script de chargement des opportunités sélectionnées');
    
    // Charger les opportunités sélectionnées
    loadSelectedOpportunities();
    
    // Initialiser les filtres et les boutons
    initFilters();
});

// Fonction pour charger et afficher les opportunités
function loadSelectedOpportunities() {
    // Trouver le conteneur des opportunités
    const opportunitiesContainer = document.getElementById('selected-opportunities') || 
                                  document.querySelector('.opportunities-container');
    
    if (!opportunitiesContainer) {
        console.error('Conteneur des opportunités non trouvé');
        return;
    }
    
    // Récupérer les opportunités depuis localStorage
    const selectedJobs = JSON.parse(localStorage.getItem('selectedOpportunities') || '[]');
    console.log('Opportunités chargées:', selectedJobs);
    
    // S'il n'y a pas d'opportunités, afficher un message
    if (selectedJobs.length === 0) {
        opportunitiesContainer.innerHTML = `
            <div class="empty-state" style="text-align: center; padding: 30px; background-color: #f8f8f8; border-radius: 8px; margin: 20px 0;">
                <i class="fas fa-search" style="font-size: 48px; color: #7C3AED; margin-bottom: 15px;"></i>
                <h3 style="margin-bottom: 10px; color: #333;">Aucune opportunité sélectionnée</h3>
                <p style="margin-bottom: 20px; color: #666;">Vous n'avez pas encore sélectionné d'opportunités. Découvrez notre sélection de postes adaptés à votre profil.</p>
                <a href="candidate-matching-improved.html" style="display: inline-block; background-color: #7C3AED; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                    <i class="fas fa-search"></i> Découvrir des opportunités
                </a>
            </div>
        `;
        return;
    }
    
    // Générer le HTML pour chaque opportunité
    let opportunitiesHTML = '';
    
    selectedJobs.forEach((job, index) => {
        // Créer le HTML pour l'opportunité
        const matchValue = parseInt(job.matchPercentage) || 85;
        
        opportunitiesHTML += `
            <div class="opportunity-card" data-status="in-progress" data-job-id="${job.id}">
                <div class="opportunity-header">
                    <div class="opportunity-company">
                        <div class="logo-placeholder">
                            <i class="fas fa-building"></i>
                        </div>
                        <div class="company-details">
                            <h3 class="company-name">${job.company}</h3>
                            <h4 class="job-title">${job.title}</h4>
                            <p class="job-info"><i class="fas fa-money-bill-wave"></i> ${job.salary}</p>
                            <a href="candidate-resources.html?email=demo.utilisateur%40nexten.fr&password=s" class="resource-button">
                                Accéder aux ressources
                            </a>
                        </div>
                    </div>
                    <div class="opportunity-match">
                        <span class="match-percentage">${job.matchPercentage}</span>
                        <span class="match-label">Match</span>
                    </div>
                </div>
                
                <div class="opportunity-status">
                    <div class="status-info">
                        <span class="status-label"><i class="fas fa-info-circle"></i> Statut: <strong>En traitement</strong></span>
                        <span class="travel-time"><i class="fas fa-map-marker-alt"></i> Temps de trajet: <a href="#" class="map-link">${job.location} <span class="text-nowrap">(voir sur Maps)</span></a></span>
                    </div>
                    
                    <div class="progress-bar-container">
                        <div class="progress-bar" style="width: 20%;"></div>
                    </div>
                </div>
                
                <div class="recruitment-stages">
                    <div class="stages-line"></div>
                    <div class="stages-progress" style="width: 20%;"></div>
                    
                    <div class="stages-wrapper">
                        <div class="stage completed">
                            <div class="stage-icon">
                                <i class="fas fa-check"></i>
                            </div>
                            <div class="stage-label">En cours de validation</div>
                        </div>
                        
                        <div class="stage active">
                            <div class="stage-icon">
                                <i class="fas fa-circle"></i>
                            </div>
                            <div class="stage-label">Call prise de contact</div>
                            <div class="interviewer-card">
                                <div class="interviewer-name">Recruteur</div>
                                <div class="interviewer-title">Responsable Recrutement</div>
                                <div class="interview-date">
                                    <i class="fas fa-calendar-alt"></i> Prochainement
                                </div>
                            </div>
                        </div>
                        
                        <div class="stage">
                            <div class="stage-icon">
                                <i class="far fa-circle"></i>
                            </div>
                            <div class="stage-label">Entretien visio</div>
                        </div>
                        
                        <div class="stage">
                            <div class="stage-icon">
                                <i class="far fa-circle"></i>
                            </div>
                            <div class="stage-label">Entretien Présentiel</div>
                        </div>
                        
                        <div class="stage">
                            <div class="stage-icon">
                                <i class="far fa-circle"></i>
                            </div>
                            <div class="stage-label">Acceptation</div>
                        </div>
                    </div>
                </div>
                
                <div class="opportunity-actions">
                    <div class="primary-actions">
                        <button class="btn btn-primary"><i class="fas fa-comment-dots"></i> Poser une question</button>
                        <button class="btn btn-outline-danger remove-job" data-job-id="${job.id}"><i class="fas fa-times-circle"></i> Retirer cette opportunité</button>
                        <button class="btn btn-outline"><i class="fas fa-calendar-alt"></i> Définir un rappel</button>
                    </div>
                    <div class="secondary-actions">
                        <button class="btn btn-outline btn-icon-text"><i class="fas fa-envelope"></i> Messagerie</button>
                        <div class="notes-container">
                            <span>Note personnelle: </span>
                            <div class="note-input-container">
                                <input type="text" class="form-control" placeholder="Ajouter un rappel...">
                                <button class="btn-save" aria-label="Sauvegarder la note"><i class="fas fa-bell"></i></button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    // Insérer le HTML dans le conteneur
    opportunitiesContainer.innerHTML = opportunitiesHTML;
    
    // Initialiser les boutons de suppression
    initRemoveButtons();
}

// Fonction pour initialiser les boutons de suppression
function initRemoveButtons() {
    const removeButtons = document.querySelectorAll('.remove-job');
    
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const jobId = this.getAttribute('data-job-id');
            if (jobId) {
                removeJob(jobId);
            }
        });
    });
    
    console.log('Boutons de suppression initialisés');
}

// Fonction pour supprimer une opportunité
function removeJob(jobId) {
    // Récupérer les opportunités depuis localStorage
    let selectedJobs = JSON.parse(localStorage.getItem('selectedOpportunities') || '[]');
    
    // Filtrer pour retirer l'opportunité spécifiée
    selectedJobs = selectedJobs.filter(job => job.id !== jobId);
    
    // Sauvegarder les opportunités mises à jour
    localStorage.setItem('selectedOpportunities', JSON.stringify(selectedJobs));
    
    // Recharger l'affichage
    loadSelectedOpportunities();
    
    console.log('Opportunité supprimée:', jobId);
}

// Fonction pour initialiser les filtres
function initFilters() {
    const filterBadges = document.querySelectorAll('.filter-badge');
    
    filterBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            // Désactiver tous les filtres
            filterBadges.forEach(b => b.classList.remove('active'));
            
            // Activer le filtre cliqué
            this.classList.add('active');
            
            // Appliquer le filtre
            const filter = this.getAttribute('data-filter');
            filterOpportunities(filter);
        });
    });
    
    console.log('Filtres initialisés');
}

// Fonction pour filtrer les opportunités
function filterOpportunities(filter) {
    const opportunities = document.querySelectorAll('.opportunity-card');
    
    opportunities.forEach(opportunity => {
        const status = opportunity.getAttribute('data-status');
        
        if (filter === 'all' || status === filter) {
            opportunity.style.display = 'block';
        } else {
            opportunity.style.display = 'none';
        }
    });
}