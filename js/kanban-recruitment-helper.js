/**
 * Script d'aide pour synchroniser le processus de recrutement avec les colonnes Kanban
 * Ce script permet de s'assurer que les colonnes Kanban correspondent aux étapes du processus de recrutement
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Script d'aide pour la synchronisation Kanban-Processus chargé");
    
    // Délai court pour s'assurer que les offres sont chargées
    setTimeout(initializeKanbanColumns, 1000);
    
    // Ajouter des écouteurs d'événements pour observer les changements
    observeJobChanges();
    
    // Ajouter un écouteur pour la mise à jour du localStorage
    listenForStorageChanges();
});

/**
 * Initialise les colonnes Kanban en fonction du processus de recrutement défini
 */
function initializeKanbanColumns() {
    console.log("Initialisation des colonnes Kanban...");
    
    // Vérifier s'il y a des postes définis
    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    
    if (!savedJobs.length) {
        console.log("Aucun poste trouvé dans localStorage");
        return;
    }
    
    // Pour chaque poste
    savedJobs.forEach(job => {
        // Récupérer le processus de recrutement (priorité à process pour compatibilité)
        const jobProcess = job.process || job.recruitmentProcess;
        
        // Si le processus existe
        if (jobProcess && jobProcess.length > 0) {
            console.log(`Processus trouvé pour le job ${job.id} : ${jobProcess.length} étapes`);
            
            // Trouver le conteneur d'offre d'emploi correspondant
            const jobContainer = document.querySelector(`[data-job-id="${job.id}"]`);
            
            // Si le conteneur est trouvé
            if (jobContainer) {
                console.log(`Conteneur trouvé pour le job ${job.id}`);
                
                // Trouver le conteneur Kanban dans le conteneur d'offre
                const kanbanContainer = jobContainer.querySelector('.job-kanban-container');
                
                // Si le conteneur Kanban est trouvé
                if (kanbanContainer) {
                    console.log(`Conteneur Kanban trouvé pour le job ${job.id}`);
                    
                    // Force la mise à jour des colonnes pour correspondre au processus actuel
                    adaptKanbanColumns(kanbanContainer, jobProcess);
                    
                } else {
                    console.log(`Conteneur Kanban non trouvé pour le job ${job.id}`);
                }
            } else {
                console.log(`Conteneur d'offre non trouvé pour le job ${job.id}`);
            }
        } else {
            console.log(`Aucun processus défini pour le job ${job.id}`);
        }
    });
}

/**
 * Détermine si les colonnes Kanban doivent être adaptées au processus de recrutement
 * @param {HTMLElement} kanbanContainer Le conteneur Kanban
 * @param {Array} jobProcess Le processus de recrutement
 * @return {boolean} True si les colonnes doivent être adaptées, false sinon
 */
function shouldAdaptKanbanColumns(kanbanContainer, jobProcess) {
    // Vérifier si l'option est activée en configuration
    const enableAutoAdapt = true; // À rendre configurable si nécessaire
    
    if (!enableAutoAdapt) {
        return false;
    }
    
    // Vérifier si les colonnes correspondent déjà au processus
    const columns = kanbanContainer.querySelectorAll('.kanban-column');
    
    // Si le nombre de colonnes est différent du nombre d'étapes + 1 (pour les candidatures)
    // On considère que les colonnes doivent être adaptées
    if (columns.length !== jobProcess.length + 1) {
        return true;
    }
    
    // Vérifie si les noms des colonnes correspondent aux étapes du processus
    // (ceci est une vérification simplifiée, vous pourriez vouloir l'améliorer)
    let columnsMatch = true;
    
    // Vérifier chaque colonne à partir de la 2ème (la 1ère est toujours "Candidatures")
    columns.forEach((column, index) => {
        if (index === 0) {
            // La première colonne doit être "Candidatures"
            const title = column.querySelector('.kanban-column-title');
            if (title && !title.textContent.includes('Candidatures')) {
                columnsMatch = false;
            }
        } else if (index <= jobProcess.length) {
            // Les colonnes suivantes doivent correspondre aux étapes du processus
            const step = jobProcess[index - 1];
            const title = column.querySelector('.kanban-column-title');
            
            if (title && !title.textContent.includes(step.title)) {
                columnsMatch = false;
            }
        }
    });
    
    return !columnsMatch;
}

/**
 * Adapte les colonnes Kanban au processus de recrutement
 * @param {HTMLElement} kanbanContainer Le conteneur Kanban
 * @param {Array} jobProcess Le processus de recrutement
 */
function adaptKanbanColumns(kanbanContainer, jobProcess) {
    console.log("Adaptation des colonnes Kanban au processus de recrutement...");
    
    // Cette fonction est liée à l'implémentation spécifique du Kanban
    // et pourrait nécessiter des adaptations en fonction de votre code
    
    // Exemple simple: créer de nouvelles colonnes
    
    // 1. Vider le conteneur Kanban (sauf les candidats existants)
    const existingCards = {};
    const columns = kanbanContainer.querySelectorAll('.kanban-column');
    
    columns.forEach(column => {
        const columnId = column.getAttribute('data-column');
        const cards = column.querySelectorAll('.candidate-card');
        
        // Stocker les cartes existantes pour les restaurer plus tard
        existingCards[columnId] = Array.from(cards);
    });
    
    // Vider le conteneur
    kanbanContainer.innerHTML = '';
    
    // 2. Créer la colonne "Candidatures"
    const candidaturesColumn = createKanbanColumn('candidatures', 'Candidatures', 'fa-file-alt');
    kanbanContainer.appendChild(candidaturesColumn);
    
    // 3. Créer les colonnes pour chaque étape du processus
    jobProcess.forEach((step, index) => {
        // Créer un identifiant unique pour la colonne
        const columnId = `step-${index + 1}`;
        
        // Déterminer l'icône en fonction du titre de l'étape
        let icon = '';
        if (step.title.toLowerCase().includes('validation')) {
            icon = 'fa-clipboard-check';
        } else if (step.title.toLowerCase().includes('call') || step.title.toLowerCase().includes('qualification')) {
            icon = 'fa-phone';
        } else if (step.title.toLowerCase().includes('entretien') || step.title.toLowerCase().includes('visio')) {
            icon = 'fa-video';
        } else if (step.title.toLowerCase().includes('présentiel')) {
            icon = 'fa-building';
        } else if (step.title.toLowerCase().includes('test')) {
            icon = 'fa-tasks';
        } else if (step.title.toLowerCase().includes('décision')) {
            icon = 'fa-gavel';
        } else if (step.title.toLowerCase().includes('embauche')) {
            icon = 'fa-handshake';
        } else {
            // Icône par défaut
            icon = 'fa-check';
        }
        
        // Créer la colonne
        const column = createKanbanColumn(columnId, step.title, icon);
        kanbanContainer.appendChild(column);
    });
    
    // 4. Restaurer les cartes existantes dans les nouvelles colonnes
    Object.keys(existingCards).forEach(columnId => {
        const column = kanbanContainer.querySelector(`[data-column="${columnId}"]`);
        
        if (column) {
            const cardsContainer = column.querySelector('.kanban-cards');
            
            existingCards[columnId].forEach(card => {
                // Insérer avant l'élément "Ajouter un candidat"
                cardsContainer.appendChild(card.cloneNode(true));
            });
        }
    });
    
    console.log("Colonnes Kanban adaptées au processus de recrutement");
}

/**
 * Crée une colonne Kanban
 * @param {string} columnId L'identifiant de la colonne
 * @param {string} title Le titre de la colonne
 * @param {string} icon L'icône de la colonne
 * @return {HTMLElement} La colonne créée
 */
function createKanbanColumn(columnId, title, icon) {
    const column = document.createElement('div');
    column.className = 'kanban-column';
    column.setAttribute('data-column', columnId);
    
    column.innerHTML = `
        <div class="kanban-column-header">
            <div class="kanban-column-title">
                <i class="fas ${icon}"></i> ${title}
                <span class="kanban-column-count">0</span>
            </div>
        </div>
        <div class="kanban-cards" data-column="${columnId}">
            <div class="add-candidate" data-column="${columnId}">
                <i class="fas fa-plus"></i> Ajouter un candidat
            </div>
        </div>
    `;
    
    return column;
}

/**
 * Observe les changements dans les postes pour réinitialiser les colonnes Kanban si nécessaire
 */
function observeJobChanges() {
    // Vérifier toutes les 3 secondes (plus fréquent pour une meilleure réactivité)
    setInterval(() => {
        // Revérifier si les colonnes Kanban doivent être adaptées
        initializeKanbanColumns();
    }, 3000);
}

/**
 * Écoute les changements dans le localStorage pour détecter les modifications du processus
 */
function listenForStorageChanges() {
    // Ajouter un écouteur d'événements pour les changements de localStorage
    window.addEventListener('storage', function(e) {
        // Vérifier si l'élément modifié est 'commitment_jobs'
        if (e.key === 'commitment_jobs') {
            console.log('Détection de changement dans localStorage pour commitment_jobs');
            // Forcer la réinitialisation des colonnes Kanban
            setTimeout(initializeKanbanColumns, 500);
        }
    });
}
