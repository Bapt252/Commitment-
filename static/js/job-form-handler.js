/**
 * Job Form Handler
 * Ce script gère l'enregistrement des offres d'emploi créées sur post-job.html
 * et leur affichage sur planning.html
 */

document.addEventListener('DOMContentLoaded', function() {
    // Vérifier sur quelle page nous sommes
    const isPostJobPage = window.location.href.includes('post-job.html');
    const isPlanningPage = window.location.href.includes('planning.html');
    
    if (isPostJobPage) {
        setupPostJobForm();
    } else if (isPlanningPage) {
        loadJobsFromStorage();
    }
});

/**
 * Configure le formulaire de création d'offre d'emploi
 */
function setupPostJobForm() {
    const form = document.getElementById('create-job-form');
    
    // Intercepter la soumission du formulaire
    if (form) {
        form.addEventListener('submit', function(e) {
            // Ne pas interférer avec le comportement par défaut du formulaire
            // mais sauvegarder les données
            
            // Récupérer les données du formulaire
            const jobTitle = document.getElementById('job-title')?.value || 'Poste non spécifié';
            const jobDescription = document.getElementById('job-description')?.value || '';
            
            // Récupérer la fourchette de salaire
            const salaryMin = document.getElementById('salary-min')?.value || '';
            const salaryMax = document.getElementById('salary-max')?.value || '';
            const salary = (salaryMin && salaryMax) ? `${salaryMin}-${salaryMax}K€` : '';
            
            // Environnement de travail
            const workEnvOptions = document.querySelectorAll('input[name="work-environment"]');
            let location = '';
            for (const option of workEnvOptions) {
                if (option.checked) {
                    switch (option.value) {
                        case 'openspace':
                            location = 'Open Space';
                            break;
                        case 'office':
                            location = 'Bureau fermé';
                            break;
                        case 'hybrid':
                            location = 'Hybride';
                            break;
                        case 'remote':
                            location = 'Télétravail';
                            break;
                    }
                    break;
                }
            }
            
            // Type de contrat
            const recruitmentContextOptions = document.querySelectorAll('input[name="recruitment-context"]');
            let type = '';
            for (const option of recruitmentContextOptions) {
                if (option.checked) {
                    switch (option.value) {
                        case 'creation':
                            type = 'cdi';
                            break;
                        case 'replacement':
                            type = 'cdd';
                            break;
                        case 'growth':
                            type = 'cdi';
                            break;
                        case 'confidential':
                            type = 'interim';
                            break;
                    }
                    break;
                }
            }
            
            // Date limite
            const now = new Date();
            const twoMonthsLater = new Date();
            twoMonthsLater.setMonth(now.getMonth() + 2);
            const deadline = formatDateForInput(twoMonthsLater);
            
            // Compétences requises (champ non présent dans le formulaire mais utile pour le kanban)
            const experienceOptions = document.querySelectorAll('input[name="experience-required"]');
            let skills = '';
            for (const option of experienceOptions) {
                if (option.checked) {
                    switch (option.value) {
                        case 'junior':
                            skills = 'Junior, Débutant';
                            break;
                        case '2-3years':
                            skills = '2-3 ans d\\'expérience';
                            break;
                        case '5-10years':
                            skills = '5-10 ans d\\'expérience, Senior';
                            break;
                        case '10plusyears':
                            skills = '10+ ans d\\'expérience, Expert';
                            break;
                    }
                    break;
                }
            }
            
            // Créer l'objet d'offre d'emploi
            const jobId = 'job' + Date.now(); // ID unique basé sur le timestamp
            const jobData = {
                id: jobId,
                title: jobTitle,
                salary: salary,
                location: location,
                type: type,
                deadline: deadline,
                description: jobDescription,
                skills: skills,
                createdAt: new Date().toISOString()
            };
            
            // Sauvegarder dans localStorage
            saveJobToStorage(jobData);
        });
    }
}

/**
 * Sauvegarde une offre d'emploi dans localStorage
 */
function saveJobToStorage(jobData) {
    // Récupérer les offres existantes
    let jobs = JSON.parse(localStorage.getItem('nextenJobs') || '[]');
    
    // Ajouter la nouvelle offre
    jobs.push(jobData);
    
    // Sauvegarder
    localStorage.setItem('nextenJobs', JSON.stringify(jobs));
}

/**
 * Charge les offres d'emploi depuis localStorage et les ajoute au tableau Kanban
 */
function loadJobsFromStorage() {
    // S'assurer que le script kanban-recruitment.js est chargé
    if (typeof window.jobOffers === 'undefined' || typeof window.addJobOfferToUI === 'undefined') {
        console.error('Le script kanban-recruitment.js doit être chargé avant job-form-handler.js');
        return;
    }
    
    // Récupérer les offres depuis localStorage
    const storedJobs = JSON.parse(localStorage.getItem('nextenJobs') || '[]');
    
    if (storedJobs.length > 0) {
        // Ajouter chaque offre au tableau des offres et à l'interface
        storedJobs.forEach(job => {
            // Vérifier si l'offre n'existe pas déjà
            if (!window.jobOffers.some(existingJob => existingJob.id === job.id)) {
                // Ajouter au tableau des offres
                window.jobOffers.push(job);
                
                // Ajouter à l'interface
                window.addJobOfferToUI(job);
            }
        });
        
        // Mettre à jour les filtres
        if (typeof window.updateJobFilters === 'function') {
            window.updateJobFilters();
        }
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
