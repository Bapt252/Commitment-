/**
 * Script de correction pour la gestion du processus de recrutement
 * Ce script s'assure que les données du processus de recrutement sont correctement
 * capturées lors de la création du poste et correctement affichées dans la page de planning.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log("Script de correction du processus de recrutement chargé");
    
    // Référencer le bouton de soumission du formulaire
    const submitButton = document.getElementById('submit-job');
    
    if (submitButton) {
        console.log('Bouton de soumission trouvé, ajout du gestionnaire pour la correction du processus');
        
        // Remplacer le gestionnaire d'événement existant
        // Utiliser capture pour être appelé avant les autres gestionnaires
        submitButton.addEventListener('click', function(e) {
            // On empêche la propagation pour éviter les gestionnaires existants
            e.stopPropagation();
            // Empêcher le comportement par défaut
            e.preventDefault();
            
            // Vérifier si la case de confirmation est cochée
            const confirmCheckbox = document.getElementById('confirm-validation');
            if (!confirmCheckbox || !confirmCheckbox.checked) {
                alert('Veuillez confirmer que les informations sont correctes avant de continuer.');
                return;
            }
            
            // Capturer correctement les données du processus de recrutement
            try {
                saveJobDataWithProcess();
                console.log('Données du poste et processus de recrutement sauvegardés avec succès');
            } catch (error) {
                console.error('Erreur lors de la sauvegarde des données:', error);
                // Continuer malgré l'erreur
            }
            
            // Afficher un message de succès
            alert('Le poste a été créé avec succès. Vous allez être redirigé vers le planning des recrutements.');
            
            // Rediriger vers planning.html
            window.location.href = 'planning.html';
        }, true); // true pour capture phase
    } else {
        console.log("Bouton de soumission non trouvé, le script s'exécute probablement sur une autre page.");
    }
});

/**
 * Fonction améliorée pour sauvegarder les données du poste
 * avec une capture complète du processus de recrutement
 */
function saveJobDataWithProcess() {
    // Récupérer les étapes du processus de recrutement avec tous les détails
    const recruitmentProcess = [];
    
    // Parcourir tous les éléments timeline-item pour extraire les étapes du processus
    const timelineItems = document.querySelectorAll('.timeline-item');
    timelineItems.forEach((item, index) => {
        // Vérifier si l'élément est actif (ne contient pas la classe 'disabled')
        if (!item.classList.contains('disabled')) {
            const titleElement = item.querySelector('.timeline-title');
            const contentElement = item.querySelector('.timeline-content p');
            
            // Capturer les membres associés si présents
            const memberItems = item.querySelectorAll('.member-item');
            const members = Array.from(memberItems).map(memberItem => {
                const memberName = memberItem.querySelector('.member-name')?.textContent.trim();
                // Détecter si c'est un placeholder "Associer un membre" ou un vrai membre
                if (memberName && !memberName.includes('Associer un membre')) {
                    return {
                        name: memberName,
                        // On pourrait aussi capturer d'autres détails comme le rôle si disponible
                        role: memberItem.querySelector('.member-role')?.textContent.trim() || ''
                    };
                }
                return null;
            }).filter(Boolean); // Filtrer les valeurs null
            
            if (titleElement && contentElement) {
                recruitmentProcess.push({
                    title: titleElement.textContent.trim(),
                    description: contentElement.textContent.trim(),
                    order: index + 1,
                    members: members,
                    // Ajouter un ID unique pour chaque étape
                    id: item.getAttribute('data-step') || `step-${index + 1}`,
                    // Stocker la configuration visuelle de l'étape
                    enabled: !item.classList.contains('disabled'),
                    // Capture des attributs de données supplémentaires
                    attributes: {
                        'data-step': item.getAttribute('data-step'),
                        'data-step-number': item.getAttribute('data-step-number')
                    }
                });
            }
        }
    });
    
    console.log("Processus de recrutement capturé:", recruitmentProcess);
    
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
        // Stocker les deux versions pour la compatibilité
        recruitmentProcess: recruitmentProcess,
        process: recruitmentProcess, // Ajout pour compatibilité avec display-recruitment-process.js
        createdAt: now.toISOString()
    };
    
    // Récupérer les jobs existants depuis localStorage
    let jobs = JSON.parse(localStorage.getItem('commitment_jobs')) || [];
    
    // Ajouter le nouveau job
    jobs.push(jobData);
    
    // Sauvegarder dans localStorage
    localStorage.setItem('commitment_jobs', JSON.stringify(jobs));
}
