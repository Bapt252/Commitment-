// Script de redirection directe pour post-job.html

document.addEventListener('DOMContentLoaded', function() {
    // Récupérer le bouton de soumission du formulaire
    const submitButton = document.getElementById('submit-job');
    
    if (submitButton) {
        console.log('Bouton de soumission trouvé, ajout du gestionnaire de clic');
        
        // Ajouter un gestionnaire d'événement de clic direct
        submitButton.addEventListener('click', function(e) {
            // Empêcher le comportement par défaut du bouton
            e.preventDefault();
            
            // Vérifier si la case de confirmation est cochée
            const confirmCheckbox = document.getElementById('confirm-validation');
            if (!confirmCheckbox || !confirmCheckbox.checked) {
                alert('Veuillez confirmer que les informations sont correctes avant de continuer.');
                return;
            }
            
            // Récupérer et sauvegarder les données du formulaire
            try {
                saveJobData();
                console.log('Données du poste sauvegardées avec succès');
            } catch (error) {
                console.error('Erreur lors de la sauvegarde des données:', error);
            }
            
            // Afficher un message de succès
            alert('Le poste a été créé avec succès. Vous allez être redirigé vers le planning des recrutements.');
            
            // Rediriger vers planning.html
            window.location.href = 'planning.html';
        });
    } else {
        console.error("Bouton 'Publier le poste' non trouvé dans le document!");
    }
    
    // Fonction pour sauvegarder les données du formulaire dans localStorage
    function saveJobData() {
        // Récupérer les étapes du processus de recrutement
        const recruitmentProcess = [];
        
        // Parcourir tous les éléments timeline-item pour extraire les étapes du processus
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach((item, index) => {
            // Vérifier si l'élément est actif (ne contient pas la classe 'disabled')
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
            location: 'Paris, France', // Valeur par défaut ou récupérée d'un champ si disponible
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
    }
});
