// Script pour afficher les postes stockés dans localStorage sur la page planning.html

document.addEventListener('DOMContentLoaded', function() {
    // Récupérer le conteneur où afficher les offres d'emploi
    const kanbanContainer = document.getElementById('kanban-container');
    
    if (!kanbanContainer) {
        console.error('Conteneur kanban non trouvé');
        return;
    }
    
    // Récupérer les jobs depuis localStorage
    const jobs = JSON.parse(localStorage.getItem('commitmentJobs')) || [];
    
    // Si aucun job n'est trouvé, ne rien faire
    if (jobs.length === 0) {
        console.log('Aucun poste trouvé dans localStorage');
        return;
    }
    
    // Fonction pour formatter la date
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('fr-FR', {
            day: 'numeric',
            month: 'numeric',
            year: 'numeric'
        });
    }
    
    // Parcourir les jobs et créer les éléments d'interface
    jobs.forEach(job => {
        // Créer un nouvel élément de conteneur pour l'offre d'emploi
        const jobOfferContainer = document.createElement('div');
        jobOfferContainer.className = 'job-offer-container';
        jobOfferContainer.dataset.jobId = job.id;
        
        // Créer l'en-tête de l'offre d'emploi
        const jobOfferHeader = document.createElement('div');
        jobOfferHeader.className = 'job-offer-header';
        
        // Titre de l'offre d'emploi
        const jobOfferTitle = document.createElement('div');
        jobOfferTitle.className = 'job-offer-title';
        jobOfferTitle.innerHTML = `
            <i class="fas fa-briefcase"></i>
            <h3>${job.title}</h3>
        `;
        
        // Informations de l'offre d'emploi
        const jobOfferInfo = document.createElement('div');
        jobOfferInfo.className = 'job-offer-info';
        jobOfferInfo.innerHTML = `
            <div class="job-offer-salary">
                <i class="fas fa-euro-sign"></i> ${job.salary || '40-50K€'}
            </div>
            <div class="job-offer-location">
                <i class="fas fa-map-marker-alt"></i> ${job.location || 'Non spécifié'}
            </div>
            <div class="job-offer-deadline">
                <i class="fas fa-calendar-alt"></i> ${formatDate(job.expirationDate)}
            </div>
            <div class="job-actions">
                <button class="btn btn-sm btn-outline view-job-stats" data-job-id="${job.id}">
                    <i class="fas fa-chart-bar"></i> Statistiques
                </button>
                <button class="btn btn-sm btn-outline edit-job-btn" data-job-id="${job.id}">
                    <i class="fas fa-edit"></i> Modifier
                </button>
            </div>
        `;
        
        // Assembler l'en-tête
        jobOfferHeader.appendChild(jobOfferTitle);
        jobOfferHeader.appendChild(jobOfferInfo);
        
        // Créer le conteneur du kanban
        const jobKanbanContainer = document.createElement('div');
        jobKanbanContainer.className = 'job-kanban-container';
        
        // Créer les colonnes du kanban
        const columns = ['candidatures', 'pre-selection', 'entretiens', 'tests', 'decision', 'embauche'];
        const columnIcons = {
            'candidatures': 'fas fa-file-alt',
            'pre-selection': 'fas fa-check',
            'entretiens': 'fas fa-calendar-check',
            'tests': 'fas fa-tasks',
            'decision': 'fas fa-gavel',
            'embauche': 'fas fa-handshake'
        };
        const columnTitles = {
            'candidatures': 'Candidatures',
            'pre-selection': 'Pré-sélection',
            'entretiens': 'Entretiens',
            'tests': 'Tests techniques',
            'decision': 'Décision finale',
            'embauche': 'Embauche'
        };
        
        // Créer les colonnes
        columns.forEach(column => {
            const kanbanColumn = document.createElement('div');
            kanbanColumn.className = 'kanban-column';
            kanbanColumn.dataset.column = column;
            
            const kanbanColumnHeader = document.createElement('div');
            kanbanColumnHeader.className = 'kanban-column-header';
            
            const kanbanColumnTitle = document.createElement('div');
            kanbanColumnTitle.className = 'kanban-column-title';
            kanbanColumnTitle.innerHTML = `
                <i class="${columnIcons[column]}"></i> ${columnTitles[column]}
                <span class="kanban-column-count">0</span>
            `;
            
            kanbanColumnHeader.appendChild(kanbanColumnTitle);
            
            const kanbanCards = document.createElement('div');
            kanbanCards.className = 'kanban-cards';
            kanbanCards.dataset.column = column;
            
            // Ajouter le bouton pour ajouter un candidat
            const addCandidateButton = document.createElement('div');
            addCandidateButton.className = 'add-candidate';
            addCandidateButton.dataset.column = column;
            addCandidateButton.innerHTML = '<i class="fas fa-plus"></i> Ajouter un candidat';
            
            kanbanCards.appendChild(addCandidateButton);
            
            kanbanColumn.appendChild(kanbanColumnHeader);
            kanbanColumn.appendChild(kanbanCards);
            
            jobKanbanContainer.appendChild(kanbanColumn);
        });
        
        // Créer la section du processus de recrutement
        const jobTimelineContainer = document.createElement('div');
        jobTimelineContainer.className = 'job-timeline-container';
        
        const toggleTimelineButton = document.createElement('button');
        toggleTimelineButton.className = 'toggle-timeline';
        toggleTimelineButton.dataset.target = `${job.id}-timeline`;
        toggleTimelineButton.innerHTML = '<i class="fas fa-stream"></i> Afficher le processus de recrutement';
        
        const jobTimeline = document.createElement('div');
        jobTimeline.id = `${job.id}-timeline`;
        jobTimeline.className = 'job-timeline';
        jobTimeline.style.display = 'none';
        
        // Titre du processus de recrutement
        const timelineTitle = document.createElement('h4');
        timelineTitle.textContent = 'Processus de recrutement';
        
        // Conteneur pour les étapes du processus
        const timeline = document.createElement('div');
        timeline.className = 'timeline';
        
        // Ajouter les étapes du processus de recrutement s'il y en a
        if (job.recruitmentProcess && job.recruitmentProcess.length > 0) {
            job.recruitmentProcess.forEach((step, index) => {
                const timelineItem = document.createElement('div');
                timelineItem.className = 'timeline-item';
                
                const timelineDate = document.createElement('div');
                timelineDate.className = 'timeline-date';
                timelineDate.textContent = `Étape ${index + 1}`;
                
                const timelineContent = document.createElement('div');
                timelineContent.className = 'timeline-content';
                
                const timelineIcon = document.createElement('div');
                timelineIcon.className = 'timeline-icon';
                timelineIcon.innerHTML = '<i class="fas fa-tasks"></i>';
                
                const timelineText = document.createElement('div');
                timelineText.className = 'timeline-text';
                
                const timelineItemTitle = document.createElement('span');
                timelineItemTitle.className = 'timeline-title';
                timelineItemTitle.textContent = step.title;
                
                const timelineItemDescription = document.createElement('p');
                timelineItemDescription.textContent = step.description;
                
                timelineText.appendChild(timelineItemTitle);
                timelineText.appendChild(timelineItemDescription);
                
                timelineContent.appendChild(timelineIcon);
                timelineContent.appendChild(timelineText);
                
                timelineItem.appendChild(timelineDate);
                timelineItem.appendChild(timelineContent);
                
                timeline.appendChild(timelineItem);
            });
        } else {
            // Message si aucun processus de recrutement n'est défini
            const noProcessItem = document.createElement('div');
            noProcessItem.className = 'timeline-item';
            noProcessItem.innerHTML = `
                <div class="timeline-content">
                    <div class="timeline-text">
                        <span class="timeline-title">Aucun processus de recrutement défini</span>
                        <p>Modifiez l'offre pour ajouter des étapes au processus de recrutement.</p>
                    </div>
                </div>
            `;
            timeline.appendChild(noProcessItem);
        }
        
        // Ajouter un bouton pour ajouter un événement
        const timelineActions = document.createElement('div');
        timelineActions.className = 'timeline-actions';
        timelineActions.innerHTML = `
            <button class="btn btn-sm btn-outline add-timeline-event" data-job-id="${job.id}">
                <i class="fas fa-plus"></i> Ajouter un événement
            </button>
        `;
        
        // Assembler la timeline
        jobTimeline.appendChild(timelineTitle);
        jobTimeline.appendChild(timeline);
        jobTimeline.appendChild(timelineActions);
        
        jobTimelineContainer.appendChild(toggleTimelineButton);
        jobTimelineContainer.appendChild(jobTimeline);
        
        // Assembler le tout
        jobOfferContainer.appendChild(jobOfferHeader);
        jobOfferContainer.appendChild(jobKanbanContainer);
        jobOfferContainer.appendChild(jobTimelineContainer);
        
        // Ajouter au conteneur principal
        kanbanContainer.prepend(jobOfferContainer);
    });
    
    // Ajouter les écouteurs d'événements pour les boutons de la timeline
    document.querySelectorAll('.toggle-timeline').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const target = document.getElementById(targetId);
            if (target) {
                const isHidden = target.style.display === 'none';
                target.style.display = isHidden ? 'block' : 'none';
                this.innerHTML = isHidden ? 
                    '<i class="fas fa-stream"></i> Masquer le processus de recrutement' : 
                    '<i class="fas fa-stream"></i> Afficher le processus de recrutement';
            }
        });
    });
    
    // Mettre à jour les compteurs pour chaque colonne
    document.querySelectorAll('.kanban-column').forEach(column => {
        const cards = column.querySelectorAll('.candidate-card');
        const countElement = column.querySelector('.kanban-column-count');
        if (countElement) {
            countElement.textContent = cards.length;
        }
    });
    
    console.log('Postes chargés avec succès depuis localStorage');
});
