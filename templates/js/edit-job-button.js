/**
 * Script pour rendre le bouton "Modifier" fonctionnel dans la page planning.html
 * Ce script permet d'ouvrir la modal d'édition d'offre d'emploi lors du clic sur le bouton "Modifier"
 * et de pré-remplir le formulaire avec les données de l'offre sélectionnée.
 */

// Fonction pour rendre le bouton "Modifier" fonctionnel
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script edit-job-button.js chargé");
    
    // S'assurer que les styles de modal sont corrects
    setupModalStyles();
    
    // Sélectionner tous les boutons de modification
    const editButtons = document.querySelectorAll('.edit-job-btn');
    console.log(`Nombre de boutons Modifier trouvés: ${editButtons.length}`);
    
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Bouton Modifier cliqué");
            
            // Récupérer l'ID de l'offre d'emploi à partir de l'attribut data-job-id
            const jobId = this.getAttribute('data-job-id');
            console.log(`ID de l'offre: ${jobId}`);
            
            // Charger les données de l'offre d'emploi (simulation ou données réelles)
            const jobData = getJobData(jobId);
            console.log("Données de l'offre récupérées", jobData);
            
            // Remplir le formulaire avec les données
            fillJobForm(jobData);
            
            // Changer le titre de la modal
            const modalTitle = document.getElementById('job-modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'MODIFIER UNE OFFRE D\'EMPLOI';
            }
            
            // Afficher la modal
            forceOpenModal('job-offer-modal');
        });
    });
});

// Fonction pour s'assurer que les styles des modals sont corrects
function setupModalStyles() {
    const allModals = document.querySelectorAll('.modal');
    
    allModals.forEach(modal => {
        // S'assurer que la modal a le bon style pour être visible
        if (window.getComputedStyle(modal).position === 'static') {
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
            modal.style.display = 'none';
            modal.style.zIndex = '1000';
            modal.style.overflow = 'auto';
            
            // S'assurer que le contenu de la modal est bien positionné
            const modalContent = modal.querySelector('.modal-content');
            if (modalContent) {
                modalContent.style.position = 'relative';
                modalContent.style.margin = '10% auto';
                modalContent.style.width = '80%';
                modalContent.style.maxWidth = '600px';
                modalContent.style.backgroundColor = '#fff';
                modalContent.style.padding = '20px';
                modalContent.style.borderRadius = '5px';
                modalContent.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.3)';
            }
        }
    });
    
    // Ajouter des gestionnaires pour fermer les modals
    const closeButtons = document.querySelectorAll('.modal-close, [id^="cancel-"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Fermer la modal si on clique en dehors du contenu
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Fonction pour forcer l'ouverture d'une modal
function forceOpenModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        console.log(`Ouverture de la modal ${modalId}`);
        modal.style.display = 'block';
        modal.style.position = 'fixed';
        modal.style.top = '0';
        modal.style.left = '0';
        modal.style.width = '100%';
        modal.style.height = '100%';
        modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modal.style.zIndex = '1000';
        modal.style.overflow = 'auto';
        
        // S'assurer que le contenu est bien positionné
        const modalContent = modal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.style.position = 'relative';
            modalContent.style.margin = '10% auto';
            modalContent.style.width = '80%';
            modalContent.style.maxWidth = '600px';
            modalContent.style.backgroundColor = '#fff';
        }
    } else {
        console.error(`Modal avec ID ${modalId} non trouvée`);
    }
}

// Fonction pour simuler la récupération des données d'une offre d'emploi
// Dans une application réelle, cette fonction récupérerait les données depuis le serveur ou localStorage
function getJobData(jobId) {
    // Essayer d'abord de récupérer les données depuis localStorage
    const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
    const savedJob = savedJobs.find(job => job.id === jobId);
    
    if (savedJob) {
        return savedJob;
    }
    
    // Données par défaut si aucune offre n'est trouvée
    // Dans une vraie application, vous récupéreriez ces données depuis une API ou une base de données
    const jobsData = {
        'job1': {
            id: 'job1',
            title: 'Développeur Full-Stack',
            salary: '45-55K€',
            location: 'Paris, France',
            type: 'cdi',
            deadline: '2025-04-30',
            description: 'Nous recherchons un développeur Full-Stack expérimenté pour rejoindre notre équipe dynamique...',
            skills: 'JavaScript, React, Node.js, MongoDB, Express'
        }
        // Vous pouvez ajouter d'autres offres d'emploi ici
    };
    
    return jobsData[jobId] || {};
}

// Fonction pour remplir le formulaire avec les données de l'offre d'emploi
function fillJobForm(jobData) {
    // Vérifier que tous les éléments du formulaire existent
    const formElements = [
        'job-id', 'job-title', 'job-salary', 'job-location', 
        'job-type', 'job-deadline', 'job-description', 'job-skills'
    ];
    
    let allElementsExist = true;
    formElements.forEach(id => {
        const element = document.getElementById(id);
        if (!element) {
            console.error(`Élément avec ID ${id} non trouvé dans le formulaire`);
            allElementsExist = false;
        }
    });
    
    if (!allElementsExist) {
        console.error("Impossible de remplir le formulaire car certains éléments sont manquants");
        return;
    }
    
    // Remplir les champs du formulaire
    document.getElementById('job-id').value = jobData.id || '';
    document.getElementById('job-title').value = jobData.title || '';
    document.getElementById('job-salary').value = jobData.salary || '';
    document.getElementById('job-location').value = jobData.location || '';
    document.getElementById('job-type').value = jobData.type || 'cdi';
    document.getElementById('job-deadline').value = jobData.deadline || '';
    document.getElementById('job-description').value = jobData.description || '';
    document.getElementById('job-skills').value = jobData.skills || '';
}
