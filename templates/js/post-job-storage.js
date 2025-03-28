// Script pour la page post-job.html

document.addEventListener('DOMContentLoaded', function() {
    // Récupérer le formulaire
    const jobForm = document.getElementById('create-job-form');
    const addStepBtn = document.getElementById('add-step-btn');
    
    // Écouter l'événement de soumission du formulaire
    if (jobForm) {
        jobForm.addEventListener('submit', function(e) {
            // Ne pas empêcher la soumission par défaut car c'est géré par le code existant
            // Mais nous allons ajouter notre logique de sauvegarde
            
            // Récupérer les étapes du processus de recrutement
            const recruitmentProcess = [];
            
            // Parcourir tous les éléments timeline-item pour extraire les étapes du processus
            const timelineItems = document.querySelectorAll('.timeline-item');
            timelineItems.forEach((item, index) => {
                // Vérifier si l'élément est actif (contient la classe 'disabled')
                if (!item.classList.contains('disabled')) {
                    const titleElement = item.querySelector('.timeline-title');
                    const contentElement = item.querySelector('.timeline-content p');
                    
                    if (titleElement && contentElement) {
                        recruitmentProcess.push({
                            title: titleElement.textContent.trim(),
                            description: contentElement.textContent.trim(),
                            order: index + 1
                        });
                    }
                }
            });
            
            // Récupérer les valeurs du formulaire
            const jobTitle = document.getElementById('job-title').value;
            const jobDescription = document.getElementById('job-description').value;
            
            // Autres informations du formulaire
            const experienceRequired = document.getElementById('experience-required')?.value || '';
            const workEnvironment = document.querySelector('input[name="work-environment"]:checked')?.value || '';
            const remoteWork = document.getElementById('remote-partial')?.checked ? 'Partiel' : 
                               (document.getElementById('remote-full')?.checked ? 'Complet' : 'Non');
            
            // Récupérer la date et l'heure actuelles
            const now = new Date();
            
            // Générer une date d'expiration (par exemple, 30 jours à partir de maintenant)
            const expirationDate = new Date();
            expirationDate.setDate(expirationDate.getDate() + 30);
            
            // Créer l'objet de données du poste
            const jobData = {
                id: 'job-' + Date.now(), // Identifiant unique basé sur le timestamp
                title: jobTitle,
                description: jobDescription,
                experience: experienceRequired,
                workEnvironment: workEnvironment,
                remoteWork: remoteWork,
                date: now.toISOString(),
                expirationDate: expirationDate.toISOString(),
                location: document.getElementById('job-location')?.value || 'Non spécifié',
                salary: '40-50K€', // Valeur par défaut ou récupérée d'un champ si disponible
                recruitmentProcess: recruitmentProcess,
                createdAt: now.toISOString()
            };
            
            // Récupérer les jobs existants depuis localStorage
            let jobs = JSON.parse(localStorage.getItem('commitment_jobs')) || [];
            
            // Ajouter le nouveau job
            jobs.push(jobData);
            
            // Sauvegarder dans localStorage
            localStorage.setItem('commitment_jobs', JSON.stringify(jobs));
            
            // Afficher un message de confirmation (optionnel, peut être géré par le code existant)
            console.log('Poste enregistré avec succès dans localStorage');
            
            // Note: Le formulaire continuera sa soumission normale après notre traitement
        });
    } else {
        console.error('Formulaire de création de poste non trouvé');
    }
});
