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

    // Ajouter des écouteurs d'événement pour les actions de suppression et d'ajout d'étapes
    setupProcessStepListeners();
});

/**
 * Configurer les écouteurs d'événements pour suivre les modifications des étapes du processus
 */
function setupProcessStepListeners() {
    // Écouter les clics sur les boutons de suppression des étapes
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // Si c'est un bouton de suppression d'étape (icône ou son parent)
        if (target.classList.contains('danger') || 
            (target.parentElement && target.parentElement.classList.contains('danger'))) {
            
            console.log('Bouton de suppression d\'étape cliqué');
            
            // Trouver l'élément timeline-item parent
            const timelineItem = target.closest('.timeline-item');
            if (timelineItem) {
                // Marquer l'élément comme supprimé avec un attribut personnalisé
                timelineItem.setAttribute('data-deleted', 'true');
                console.log('Étape marquée comme supprimée:', timelineItem);
            }
        }
        
        // Si c'est le bouton "Ajouter une étape"
        if (target.id === 'add-step-btn' || 
            (target.parentElement && target.parentElement.id === 'add-step-btn')) {
            console.log('Bouton "Ajouter une étape" cliqué');
            // Les nouvelles étapes seront traitées lors de la sauvegarde
        }
    });
    
    // Écouter les clics sur le bouton de sauvegarde d'une nouvelle étape
    document.addEventListener('click', function(event) {
        if (event.target.id === 'save-step-btn') {
            console.log('Nouvelle étape ajoutée');
            // La nouvelle étape sera ajoutée au DOM par le code existant
            // et sera capturée lors de la sauvegarde
        }
    });

    // Écouteur pour les changements d'activation/désactivation des étapes
    document.addEventListener('click', function(event) {
        const target = event.target;
        
        // Si c'est un bouton d'activation d'étape (icône ou son parent)
        if (target.classList.contains('success') || 
            (target.parentElement && target.parentElement.classList.contains('success'))) {
            
            console.log('Bouton d\'activation d\'étape cliqué');
            
            // Trouver l'élément timeline-item parent
            const timelineItem = target.closest('.timeline-item');
            if (timelineItem) {
                // Toggle l'état d'activation
                const isDisabled = timelineItem.classList.contains('disabled');
                
                if (isDisabled) {
                    timelineItem.classList.remove('disabled');
                    timelineItem.removeAttribute('data-disabled');
                    console.log('Étape activée:', timelineItem);
                } else {
                    timelineItem.classList.add('disabled');
                    timelineItem.setAttribute('data-disabled', 'true');
                    console.log('Étape désactivée:', timelineItem);
                }
            }
        }
    });
}

/**
 * Fonction améliorée pour sauvegarder les données du poste
 * avec une capture complète du processus de recrutement
 */
function saveJobDataWithProcess() {
    // Récupérer les étapes du processus de recrutement avec tous les détails
    const recruitmentProcess = [];
    
    // Parcourir tous les éléments timeline-item pour extraire les étapes du processus
    const timelineItems = document.querySelectorAll('.timeline-item');
    let stepIndex = 1;
    
    timelineItems.forEach((item) => {
        // Vérifier si l'élément est supprimé ou désactivé
        const isDeleted = item.getAttribute('data-deleted') === 'true';
        const isDisabled = item.classList.contains('disabled') || item.getAttribute('data-disabled') === 'true';
        
        // Ne pas inclure les étapes supprimées
        if (isDeleted) {
            console.log('Étape ignorée car supprimée:', item);
            return;
        }
        
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
                order: stepIndex++,
                members: members,
                // Ajouter un ID unique pour chaque étape
                id: item.getAttribute('data-step') || `step-${stepIndex}`,
                // Stocker la configuration visuelle de l'étape
                enabled: !isDisabled,
                // Capture des attributs de données supplémentaires
                attributes: {
                    'data-step': item.getAttribute('data-step'),
                    'data-step-number': item.getAttribute('data-step-number')
                }
            });
        }
    });
    
    console.log("Processus de recrutement capturé avec gestion des suppressions/désactivations:", recruitmentProcess);
    
    // Récupérer les valeurs du formulaire
    const jobTitle = document.getElementById('job-title').value || "Nouveau poste";
    const jobDescription = document.getElementById('job-description').value || "Description non spécifiée";
    
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
    
    // Composer la chaîne de salaire
    let salary = '40-50K€'; // Valeur par défaut
    const salaryMin = document.getElementById('salary-min')?.value;
    const salaryMax = document.getElementById('salary-max')?.value;
    const salaryFrequency = document.getElementById('salary-frequency')?.value;
    
    if (salaryMin && salaryMax) {
        const frequencyLabel = {
            'annual': 'annuel',
            'monthly': 'mensuel',
            'daily': 'jour',
            'hourly': 'heure'
        }[salaryFrequency] || 'annuel';
        
        salary = `${salaryMin}-${salaryMax}€/${frequencyLabel}`;
    }
    
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
        salary: salary,
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
