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
            
            // S'assurer que tous les icônes perdent la classe "card-open"
            document.querySelectorAll('.stage-icon').forEach(icon => {
                icon.classList.remove('card-open');
            });
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
            const stageIcon = stage.querySelector('.stage-icon');
            stageIcon.classList.add('clickable');
            
            // Ajouter un gestionnaire d'événement pour le clic sur l'icône
            stageIcon.addEventListener('click', function(e) {
                e.stopPropagation(); // Empêcher la propagation de l'événement
                
                // Vérifier si cette étape est déjà ouverte
                if (currentOpenStage === stage) {
                    // C'est la même étape, donc on ferme la carte
                    card.style.display = 'none';
                    card.classList.remove('card-visible');
                    stageIcon.classList.remove('card-open');
                    currentOpenStage = null;
                } else {
                    // C'est une nouvelle étape, fermer toutes les cartes et ouvrir celle-ci
                    closeAllCards();
                    card.style.display = 'block';
                    card.classList.add('card-visible');
                    stageIcon.classList.add('card-open');
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
            stageIcon.appendChild(infoIndicator);
            
            // Permettre également de fermer en cliquant sur la carte elle-même
            card.addEventListener('click', function(e) {
                e.stopPropagation(); // Empêcher la propagation pour ne pas fermer toutes les cartes
                
                // Fermer la carte quand on clique dessus
                card.style.display = 'none';
                card.classList.remove('card-visible');
                stageIcon.classList.remove('card-open');
                currentOpenStage = null;
            });
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
        
        // Ajouter une classe spéciale pour améliorer la visibilité du curseur pointer
        icon.classList.add('active-icon-hover');
    });
    
    // Ajouter un style pour la carte ouverte
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        .stage-icon.clickable {
            cursor: pointer;
        }
        .stage-icon.active-icon-hover:hover {
            transform: scale(1.25);
            box-shadow: 0 0 0 6px rgba(76, 175, 80, 0.3);
        }
        .stage-icon.card-open {
            transform: scale(1.25);
            box-shadow: 0 0 0 6px rgba(76, 175, 80, 0.3);
        }
        .interviewer-card {
            opacity: 0;
            transform: translateY(10px);
            transition: opacity 0.3s ease, transform 0.3s ease;
            cursor: pointer; /* Indique que la carte est cliquable */
        }
        .interviewer-card:hover {
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        .interviewer-card.card-visible {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(styleElement);
});