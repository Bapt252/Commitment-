/**
 * Script d'aide pour améliorer l'intégration des nouvelles offres d'emploi 
 * dans le système Kanban de recrutement
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script kanban-recruitment-helper.js chargé");
    
    // Vérifie si une offre vient d'être créée (via sessionStorage)
    const lastCreatedJobId = sessionStorage.getItem('last_created_job_id');
    
    if (lastCreatedJobId) {
        console.log("Dernière offre créée détectée:", lastCreatedJobId);
        
        // Attendre que les offres soient chargées dans le DOM
        setTimeout(() => {
            // On vérifie si l'offre est bien affichée
            const jobContainer = document.querySelector(`[data-job-id="${lastCreatedJobId}"]`);
            
            if (!jobContainer) {
                console.log("L'offre récemment créée n'est pas encore dans le DOM, tentative de l'ajouter manuellement");
                
                // Récupérer les données de l'offre
                const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
                const newJob = savedJobs.find(job => job.id === lastCreatedJobId);
                
                if (newJob && window.addJobOfferToUI) {
                    // Ajouter manuellement l'offre à l'interface
                    window.addJobOfferToUI(newJob);
                    console.log("Offre ajoutée manuellement à l'interface:", newJob);
                    
                    // Nettoyer sessionStorage
                    sessionStorage.removeItem('last_created_job_id');
                }
            } else {
                console.log("L'offre récemment créée est déjà présente dans le DOM");
                
                // Mettre en évidence l'offre nouvellement ajoutée
                jobContainer.style.transition = 'background-color 2s';
                jobContainer.style.backgroundColor = 'rgba(124, 58, 237, 0.1)';
                
                // Revenir à la couleur normale après un délai
                setTimeout(() => {
                    jobContainer.style.backgroundColor = '';
                }, 3000);
                
                // Nettoyer sessionStorage
                sessionStorage.removeItem('last_created_job_id');
            }
        }, 1500);
    }
    
    // Améliorer la fonction addJobOfferToUI pour gérer les timelines
    const originalAddJobOfferToUI = window.addJobOfferToUI;
    
    if (typeof originalAddJobOfferToUI === 'function') {
        window.addJobOfferToUI = function(jobData) {
            console.log("Ajout amélioré d'une offre à l'interface:", jobData);
            
            // Appeler la fonction originale
            originalAddJobOfferToUI(jobData);
            
            // Attendre que le DOM soit mis à jour
            setTimeout(() => {
                // Trouver le conteneur de l'offre
                const jobContainer = document.querySelector(`[data-job-id="${jobData.id}"]`);
                
                if (jobContainer) {
                    // Trouver ou créer la section de timeline
                    let timelineContainer = jobContainer.querySelector('.job-timeline-container');
                    
                    if (!timelineContainer) {
                        console.log("Création d'un conteneur de timeline pour:", jobData.id);
                        
                        // Créer la section de timeline
                        timelineContainer = document.createElement('div');
                        timelineContainer.className = 'job-timeline-container';
                        timelineContainer.innerHTML = `
                            <button class="toggle-timeline" data-target="${jobData.id}-timeline">
                                <i class="fas fa-stream"></i> Afficher la timeline du recrutement
                            </button>
                            <div id="${jobData.id}-timeline" class="job-timeline" style="display: none;">
                                <h4>Timeline du recrutement</h4>
                                <div class="timeline"></div>
                                <div class="timeline-actions">
                                    <button class="btn btn-sm btn-outline add-timeline-event" data-job-id="${jobData.id}">
                                        <i class="fas fa-plus"></i> Ajouter un événement
                                    </button>
                                </div>
                            </div>
                        `;
                        
                        // Ajouter au jobContainer
                        jobContainer.appendChild(timelineContainer);
                        
                        console.log("Conteneur de timeline créé pour:", jobData.id);
                    }
                }
            }, 500);
        };
    }
});
