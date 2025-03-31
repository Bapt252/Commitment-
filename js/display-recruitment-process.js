/**
 * Script pour afficher le processus de recrutement personnalisé sur la page planning.html
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script display-recruitment-process.js chargé");
    
    // Récupérer les offres d'emploi depuis localStorage
    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    
    console.log("Vérification des processus de recrutement:", savedJobs);
    
    // Si des offres existent
    if (savedJobs.length > 0) {
        // Pour chaque offre, vérifier si elle a un processus de recrutement
        savedJobs.forEach(job => {
            console.log("Traitement de l'offre:", job.id, job.title);
            
            // Utiliser recruitmentProcess ou process (priorité à process pour rétrocompatibilité)
            const jobProcess = job.process || job.recruitmentProcess;
            console.log("Processus attaché:", jobProcess);
            
            if (jobProcess && jobProcess.length > 0) {
                console.log("Processus de recrutement trouvé pour:", job.id);
                
                // Attendre un peu que le DOM soit complètement chargé avec les offres
                setTimeout(() => {
                    // On essaie de trouver le conteneur de timeline pour cette offre
                    // Différentes façons possibles d'identifier la timeline
                    const jobContainer = document.querySelector(`[data-job-id="${job.id}"]`);
                    console.log("Conteneur d'offre trouvé:", jobContainer);
                    
                    if (jobContainer) {
                        // Trouver le bouton toggle timeline
                        const timelineToggleBtn = jobContainer.querySelector('.toggle-timeline');
                        console.log("Bouton toggle timeline trouvé:", timelineToggleBtn);
                        
                        if (timelineToggleBtn) {
                            const targetId = timelineToggleBtn.getAttribute('data-target');
                            console.log("ID cible de la timeline:", targetId);
                            
                            // Créer ou récupérer la timeline
                            let timelineContainer = document.getElementById(targetId);
                            
                            if (!timelineContainer) {
                                console.log("Timeline non trouvée, on simule un clic sur le bouton pour la créer");
                                // Simuler un clic pour créer la timeline
                                timelineToggleBtn.click();
                                // Récupérer à nouveau le conteneur
                                timelineContainer = document.getElementById(targetId);
                                
                                if (timelineContainer) {
                                    console.log("Timeline créée avec succès");
                                    // Appliquer le processus
                                    applyProcessToTimeline(jobProcess, timelineContainer);
                                    // Refermer la timeline
                                    setTimeout(() => timelineToggleBtn.click(), 100);
                                } else {
                                    console.error("Impossible de créer la timeline");
                                }
                            } else {
                                console.log("Timeline trouvée directement");
                                applyProcessToTimeline(jobProcess, timelineContainer);
                            }
                        } else {
                            console.error("Bouton toggle timeline non trouvé");
                            
                            // Tentative alternative: créer la timeline manuellement
                            const timelineContainer = document.createElement('div');
                            timelineContainer.id = `${job.id}-timeline`;
                            timelineContainer.className = 'job-timeline';
                            timelineContainer.innerHTML = `
                                <h4>Timeline du recrutement</h4>
                                <div class="timeline"></div>
                                <div class="timeline-actions">
                                    <button class="btn btn-sm btn-outline add-timeline-event" data-job-id="${job.id}">
                                        <i class="fas fa-plus"></i> Ajouter un événement
                                    </button>
                                </div>
                            `;
                            
                            // Trouver un endroit où ajouter cette timeline
                            const timelineContainerParent = jobContainer.querySelector('.job-timeline-container');
                            if (timelineContainerParent) {
                                timelineContainerParent.appendChild(timelineContainer);
                                console.log("Timeline créée manuellement");
                                applyProcessToTimeline(jobProcess, timelineContainer);
                            }
                        }
                    } else {
                        console.error("Conteneur d'offre non trouvé pour l'ID:", job.id);
                        
                        // Attendre la création des offres d'emploi dans le DOM
                        const observer = new MutationObserver((mutations, obs) => {
                            const jobContainer = document.querySelector(`[data-job-id="${job.id}"]`);
                            if (jobContainer) {
                                console.log("Conteneur d'offre trouvé après attente:", job.id);
                                
                                // Trouver le bouton toggle timeline
                                const timelineToggleBtn = jobContainer.querySelector('.toggle-timeline');
                                if (timelineToggleBtn) {
                                    const targetId = timelineToggleBtn.getAttribute('data-target');
                                    
                                    // Pour être sûr, on attend encore un peu
                                    setTimeout(() => {
                                        // Simuler un clic pour créer la timeline
                                        timelineToggleBtn.click();
                                        
                                        // Récupérer le conteneur
                                        const timelineContainer = document.getElementById(targetId);
                                        
                                        if (timelineContainer) {
                                            // Appliquer le processus
                                            applyProcessToTimeline(jobProcess, timelineContainer);
                                            // Refermer la timeline après un moment
                                            setTimeout(() => timelineToggleBtn.click(), 200);
                                        }
                                    }, 300);
                                }
                                
                                // Arrêter l'observation
                                obs.disconnect();
                            }
                        });
                        
                        // Observer le DOM pour détecter quand les offres d'emploi sont ajoutées
                        observer.observe(document.body, { childList: true, subtree: true });
                    }
                }, 1000); // Attendre 1 seconde
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
                    
                    // Vérifier si nous avons un processus à appliquer pour cette timeline
                    const jobId = targetId.replace('-timeline', '');
                    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
                    const job = savedJobs.find(j => j.id === jobId);
                    
                    if (job) {
                        const jobProcess = job.process || job.recruitmentProcess;
                        if (jobProcess && jobProcess.length > 0) {
                            console.log("Application du processus lors du toggle:", jobProcess);
                            applyProcessToTimeline(jobProcess, timelineContainer);
                        }
                    }
                } else {
                    timelineContainer.style.display = 'none';
                    button.innerHTML = '<i class="fas fa-stream"></i> Afficher la timeline du recrutement';
                }
            }
        }
    });
    
    // Logique pour initialiser les colonnes Kanban en fonction du processus de recrutement
    initializeKanbanColumns();
});

/**
 * Initialise les colonnes du Kanban en fonction du processus de recrutement
 */
function initializeKanbanColumns() {
    console.log("Initialisation des colonnes Kanban basées sur le processus de recrutement");
    
    // Récupérer les offres d'emploi depuis localStorage
    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    
    // Pour chaque offre
    savedJobs.forEach(job => {
        // Utiliser recruitmentProcess ou process (priorité à process pour rétrocompatibilité)
        const jobProcess = job.process || job.recruitmentProcess;
        
        if (jobProcess && jobProcess.length > 0) {
            setTimeout(() => {
                // Trouver le conteneur Kanban pour cette offre
                const jobContainer = document.querySelector(`[data-job-id="${job.id}"]`);
                if (jobContainer) {
                    const kanbanContainer = jobContainer.querySelector('.job-kanban-container');
                    if (kanbanContainer) {
                        // Adapter les colonnes du Kanban aux étapes du processus si nécessaire
                        // Cette partie est optionnelle et peut être implémentée selon les besoins
                        console.log(`Colonnes Kanban trouvées pour l'offre ${job.id}, adaptation possible`);
                    }
                }
            }, 1500); // Attendre que le DOM soit chargé
        }
    });
}

/**
 * Applique les étapes du processus de recrutement à la timeline
 * @param {Array} process Les étapes du processus de recrutement
 * @param {HTMLElement} timelineContainer Le conteneur HTML de la timeline
 */
function applyProcessToTimeline(process, timelineContainer) {
    // S'assurer que le conteneur existe et a la structure attendue
    if (!timelineContainer) {
        console.error("Container de timeline non trouvé");
        return;
    }
    
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
        } else if (step.title.toLowerCase().includes('contact') || step.title.toLowerCase().includes('call') || step.title.toLowerCase().includes('qualification')) {
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
        
        // Construire l'élément HTML de base
        let timelineItemHTML = `
            <div class="timeline-date">${formattedDate}</div>
            <div class="timeline-content">
                <div class="timeline-icon"><i class="fas ${icon}"></i></div>
                <div class="timeline-text">
                    <span class="timeline-title">${step.title}</span>
                    <p>${step.description || ''}</p>
                </div>
            </div>
        `;
        
        // Ajouter les membres associés si présents
        if (step.members && step.members.length > 0) {
            let membersHTML = '<div class="timeline-members">';
            step.members.forEach(member => {
                membersHTML += `
                    <div class="timeline-member">
                        <div class="member-avatar">${getInitials(member.name)}</div>
                        <div class="member-info">
                            <div class="member-name">${member.name}</div>
                            ${member.role ? `<div class="member-role">${member.role}</div>` : ''}
                        </div>
                    </div>
                `;
            });
            membersHTML += '</div>';
            
            // Insérer les membres dans l'élément HTML
            timelineItemHTML = timelineItemHTML.replace('</div></div>', `</div>${membersHTML}</div>`);
        }
        
        // Définir le HTML de l'élément timeline
        timelineItem.innerHTML = timelineItemHTML;
        
        // Ajouter l'élément à la timeline
        timelineElement.appendChild(timelineItem);
    });
    
    console.log("Timeline mise à jour avec le processus de recrutement");
}

/**
 * Récupère les initiales d'un nom
 * @param {string} name Le nom complet
 * @return {string} Les initiales (2 caractères max)
 */
function getInitials(name) {
    if (!name) return '';
    
    const parts = name.split(' ');
    let initials = '';
    
    for (let i = 0; i < Math.min(parts.length, 2); i++) {
        if (parts[i][0]) {
            initials += parts[i][0].toUpperCase();
        }
    }
    
    return initials;
}
