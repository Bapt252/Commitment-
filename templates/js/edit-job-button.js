/**
 * Script pour rendre le bouton "Modifier" fonctionnel dans la page planning.html
 * Ce script permet d'ouvrir la modal d'édition d'offre d'emploi lors du clic sur le bouton "Modifier"
 * et de pré-remplir le formulaire avec les données de l'offre sélectionnée.
 */

// Fonction pour rendre le bouton "Modifier" fonctionnel
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner tous les boutons de modification
    const editButtons = document.querySelectorAll('.edit-job-btn');
    
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Récupérer l'ID de l'offre d'emploi à partir de l'attribut data-job-id
            const jobId = this.getAttribute('data-job-id');
            
            // Charger les données de l'offre d'emploi (simulation ou données réelles)
            const jobData = getJobData(jobId);
            
            // Remplir le formulaire avec les données
            fillJobForm(jobData);
            
            // Changer le titre de la modal
            const modalTitle = document.getElementById('job-modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'MODIFIER UNE OFFRE D\'EMPLOI';
            }
            
            // Afficher la modal
            openModal('job-offer-modal');
        });
    });
    
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
    
    // Fonction pour ouvrir une modal
    function openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }
});
