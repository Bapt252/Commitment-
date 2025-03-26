// Script pour rendre les étapes du recrutement interactives
document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner toutes les étapes
    const stages = document.querySelectorAll('.stage');
    
    // Masquer toutes les cartes d'interlocuteurs par défaut
    const interviewerCards = document.querySelectorAll('.interviewer-card');
    interviewerCards.forEach(card => {
        card.style.display = 'none';
        card.classList.remove('card-visible');
    });
    
    // Fonction pour fermer toutes les cartes ouvertes
    function closeAllCards() {
        interviewerCards.forEach(card => {
            card.style.display = 'none';
            card.classList.remove('card-visible');
        });
    }
    
    // Variable pour suivre l'étape actuellement ouverte
    let currentOpenStage = null;
    
    // Ajouter des gestionnaires d'événements pour chaque étape
    stages.forEach(stage => {
        // Trouver la carte d'interlocuteur associée à cette étape (s'il y en a une)
        const card = stage.querySelector('.interviewer-card');
        
        if (card) {
            // Ajouter une classe pour le style de l'icône cliquable
            stage.querySelector('.stage-icon').classList.add('clickable');
            
            // Ajouter un gestionnaire d'événement pour le clic sur l'icône
            stage.querySelector('.stage-icon').addEventListener('click', function(e) {
                e.stopPropagation(); // Empêcher la propagation de l'événement
                
                // Vérifier si cette étape est déjà ouverte
                if (currentOpenStage === stage) {
                    // C'est la même étape, donc on ferme la carte
                    card.style.display = 'none';
                    card.classList.remove('card-visible');
                    currentOpenStage = null;
                } else {
                    // C'est une nouvelle étape, fermer toutes les cartes et ouvrir celle-ci
                    closeAllCards();
                    card.style.display = 'block';
                    card.classList.add('card-visible');
                    currentOpenStage = stage;
                    
                    // Animation d'apparition
                    setTimeout(() => {
                        card.style.opacity = 1;
                        card.style.transform = 'translateY(0)';
                    }, 10);
                }
            });
            
            // Ajouter un indice visuel (petit point ou badge) pour indiquer qu'il y a des informations
            const infoIndicator = document.createElement('span');
            infoIndicator.className = 'info-indicator';
            infoIndicator.setAttribute('title', 'Cliquez pour voir les détails');
            stage.querySelector('.stage-icon').appendChild(infoIndicator);
        }
    });
    
    // Fermer les cartes quand on clique ailleurs sur la page
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.stage-icon') && !e.target.closest('.interviewer-card')) {
            closeAllCards();
            currentOpenStage = null;
        }
    });
    
    // Pour les étapes actives, on peut ajouter un effet de pulsation pour attirer l'attention
    const activeStages = document.querySelectorAll('.stage.active .stage-icon');
    activeStages.forEach(icon => {
        icon.classList.add('pulse-animation');
    });
});