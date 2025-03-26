/**
 * Script pour afficher le processus de recrutement personnalisé sur la page planning.html
 */
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les offres d'emploi depuis localStorage
    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    
    // Si des offres existent
    if (savedJobs.length > 0) {
        console.log("Processus de recrutement trouvés:", savedJobs);
        
        // Pour chaque offre, vérifier si elle a un processus de recrutement
        savedJobs.forEach(job => {
            if (job.process && job.process.length > 0) {
                // Sélectionner le conteneur de timeline correspondant à cette offre
                const timelineContainer = document.getElementById(`${job.id}-timeline`);
                if (timelineContainer) {
                    applyProcessToTimeline(job.process, timelineContainer);
                } else {
                    // Si le conteneur n'existe pas encore, créer un MutationObserver pour le détecter
                    // quand il sera créé par la fonction addJobOfferToUI
                    const observer = new MutationObserver(mutations => {
                        mutations.forEach(mutation => {
                            if (mutation.type === 'childList') {
                                const newTimelineContainer = document.getElementById(`${job.id}-timeline`);
                                if (newTimelineContainer) {
                                    applyProcessToTimeline(job.process, newTimelineContainer);
                                    observer.disconnect(); // Arrêter l'observation une fois le conteneur trouvé
                                }
                            }
                        });
                    });
                    
                    // Observer les changements dans le DOM pour détecter quand le conteneur est créé
                    observer.observe(document.body, { childList: true, subtree: true });
                    
                    // Créer la timeline maintenant si possible
                    setTimeout(() => {
                        const timelineBtn = document.querySelector(`button.toggle-timeline[data-target="${job.id}-timeline"]`);
                        if (timelineBtn) {
                            // Cliquer pour créer la timeline si elle n'existe pas
                            timelineBtn.click();
                            // Attendre que la timeline soit créée
                            setTimeout(() => {
                                const timelineContainer = document.getElementById(`${job.id}-timeline`);
                                if (timelineContainer) {
                                    applyProcessToTimeline(job.process, timelineContainer);
                                    // Recliquer pour masquer la timeline
                                    timelineBtn.click();
                                }
                            }, 100);
                        }
                    }, 500);
                }
            }
        });
    }
    
    // Écouteur d'événements pour les boutons toggle-timeline
    document.addEventListener('click', function(e) {
        if (e.target.closest('.toggle-timeline')) {
            const button = e.target.closest('.toggle-timeline');
            const targetId = button.getAttribute('data-target');
            const timelineContainer = document.getElementById(targetId);
            
            if (timelineContainer) {
                // Toggle de l'affichage
                if (timelineContainer.style.display === 'none') {
                    timelineContainer.style.display = 'block';
                    button.innerHTML = '<i class="fas fa-stream"></i> Masquer la timeline du recrutement';
                } else {
                    timelineContainer.style.display = 'none';
                    button.innerHTML = '<i class="fas fa-stream"></i> Afficher la timeline du recrutement';
                }
            }
        }
    });
});

/**
 * Applique les étapes du processus de recrutement à la timeline
 * @param {Array} process Les étapes du processus de recrutement
 * @param {HTMLElement} timelineContainer Le conteneur HTML de la timeline
 */
function applyProcessToTimeline(process, timelineContainer) {
    // S'assurer que le conteneur existe et a la structure attendue
    if (!timelineContainer) return;
    
    console.log("Application du processus à la timeline:", process);
    
    // Trouver l'élément timeline dans le conteneur
    const timelineElement = timelineContainer.querySelector('.timeline');
    if (!timelineElement) {
        console.error("Élément timeline non trouvé dans le conteneur:", timelineContainer);
        return;
    }
    
    // Vider la timeline existante
    timelineElement.innerHTML = '';
    
    // Ajouter chaque étape du processus à la timeline
    process.forEach((step, index) => {
        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';
        
        // Déterminer l'icône en fonction du titre ou de l'ordre
        let icon = '';
        if (step.title.toLowerCase().includes('validation')) {
            icon = 'fa-clipboard-check';
        } else if (step.title.toLowerCase().includes('contact') || step.title.toLowerCase().includes('call')) {
            icon = 'fa-phone';
        } else if (step.title.toLowerCase().includes('entretien') || step.title.toLowerCase().includes('visio')) {
            icon = 'fa-video';
        } else if (step.title.toLowerCase().includes('présentiel')) {
            icon = 'fa-building';
        } else if (step.title.toLowerCase().includes('acceptation') || step.title.toLowerCase().includes('décision')) {
            icon = 'fa-handshake';
        } else {
            // Icônes par défaut selon l'ordre
            const defaultIcons = ['fa-clipboard-check', 'fa-phone', 'fa-video', 'fa-building', 'fa-handshake'];
            icon = defaultIcons[index % defaultIcons.length];
        }
        
        // Date (simulée pour l'exemple)
        const today = new Date();
        const stepDate = new Date(today);
        stepDate.setDate(today.getDate() + (index * 7)); // Une étape par semaine
        
        const day = String(stepDate.getDate()).padStart(2, '0');
        const month = String(stepDate.getMonth() + 1).padStart(2, '0');
        const year = stepDate.getFullYear();
        const formattedDate = `${day}/${month}/${year}`;
        
        // Construire l'élément HTML
        timelineItem.innerHTML = `
            <div class="timeline-date">${formattedDate}</div>
            <div class="timeline-content">
                <div class="timeline-icon"><i class="fas ${icon}"></i></div>
                <div class="timeline-text">
                    <span class="timeline-title">${step.title}</span>
                    <p>${step.description}</p>
                </div>
            </div>
        `;
        
        // Ajouter l'élément à la timeline
        timelineElement.appendChild(timelineItem);
    });
    
    console.log("Timeline mise à jour avec le processus de recrutement");
}
