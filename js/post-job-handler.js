// Script pour gérer la soumission du formulaire de post-job.html
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('create-job-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Récupérer les données du formulaire
            const jobId = 'job-' + Date.now(); // Identifiant unique basé sur le timestamp
            const jobData = {
                id: jobId, // Identifiant unique
                title: document.getElementById('job-title').value,
                description: document.getElementById('job-description').value,
                salary: getSalaryRange(),
                location: getLocation(),
                deadline: getDeadline(),
                recruitmentContext: getRecruitmentContext(),
                experienceRequired: getExperienceRequired(),
                created: new Date().toISOString(),
                process: getRecruitmentProcess()
            };
            
            console.log("Données du poste à sauvegarder:", jobData);
            console.log("ID du poste généré:", jobId);
            
            // Stocker l'ID du job pour la redirection
            sessionStorage.setItem('last_created_job_id', jobId);
            
            // Sauvegarder dans localStorage
            saveJobToLocalStorage(jobData);
            
            // Rediriger vers la page planning
            window.location.href = 'planning.html';
        });
    }
    
    // Fonction pour récupérer la fourchette de salaire
    function getSalaryRange() {
        const min = document.getElementById('salary-min').value || 0;
        const max = document.getElementById('salary-max').value || 0;
        
        if (min && max) {
            return `${min}-${max}K€`;
        } else if (min) {
            return `${min}K€+`;
        } else if (max) {
            return `Jusqu'à ${max}K€`;
        }
        return 'Non spécifié';
    }
    
    // Fonction pour récupérer la localisation (simulée)
    function getLocation() {
        return 'Paris, France'; // Par défaut, pourrait être récupéré d'un champ de formulaire
    }
    
    // Fonction pour récupérer la date limite (calculée à 30 jours par défaut)
    function getDeadline() {
        const deadline = new Date();
        deadline.setDate(deadline.getDate() + 30);
        return formatDate(deadline);
    }
    
    // Formater la date au format JJ/MM/AAAA
    function formatDate(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }
    
    // Récupérer le contexte de recrutement
    function getRecruitmentContext() {
        const contextRadios = document.querySelectorAll('input[name="recruitment-context"]');
        for (const radio of contextRadios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'creation'; // Par défaut
    }
    
    // Récupérer l'expérience requise
    function getExperienceRequired() {
        const experienceRadios = document.querySelectorAll('input[name="experience-required"]');
        for (const radio of experienceRadios) {
            if (radio.checked) {
                return radio.value;
            }
        }
        return 'junior'; // Par défaut
    }
    
    // Récupérer le processus de recrutement
    function getRecruitmentProcess() {
        const flowSteps = document.querySelectorAll('.flow-step');
        const process = [];
        
        flowSteps.forEach((step, index) => {
            const titleElement = step.querySelector('.flow-step-title span:first-child');
            const descriptionElement = step.querySelector('.flow-step-description');
            
            if (titleElement && descriptionElement) {
                process.push({
                    id: `step-${index + 1}`,
                    title: titleElement.textContent.trim(),
                    description: descriptionElement.textContent.trim(),
                    order: index + 1,
                    isActive: step.classList.contains('active'),
                    isCompleted: step.classList.contains('completed')
                });
            }
        });
        
        console.log("Processus de recrutement récupéré:", process);
        return process;
    }
    
    // Sauvegarder l'offre dans localStorage
    function saveJobToLocalStorage(jobData) {
        // Récupérer les offres existantes ou initialiser un tableau vide
        const savedJobs = JSON.parse(localStorage.getItem('commitment_jobs') || '[]');
        
        // Ajouter la nouvelle offre
        savedJobs.push(jobData);
        
        // Sauvegarder dans localStorage
        localStorage.setItem('commitment_jobs', JSON.stringify(savedJobs));
        
        console.log('Offre d\'emploi sauvegardée:', jobData);
    }
});
