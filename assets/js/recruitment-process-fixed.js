document.addEventListener('DOMContentLoaded', function() {
    // Ajouter des attributs de numéros d'étape aux éléments du processus
    // pour les badges violets dans les coins
    function updateProcessStepNumbers() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach((item, index) => {
            // Ajouter l'attribut data-step-number pour le numéro affiché dans le badge violet
            item.setAttribute('data-step-number', index + 1);
        });
    }
    
    // Initialiser les numéros
    updateProcessStepNumbers();
    
    // Mise à jour de la progression des étapes principales (onglets en haut)
    function updateProgress() {
        const steps = document.querySelectorAll('.progress-step');
        let activeIndex = 0;
        
        steps.forEach((step, index) => {
            if (step.classList.contains('active')) {
                activeIndex = index;
            }
        });
        
        // Met à jour la largeur de la barre de progression
        const progressLine = document.querySelector('.progress-steps');
        if (progressLine) {
            // Calcul du pourcentage de progression
            const progressPercent = (activeIndex / (steps.length - 1)) * 100;
            progressLine.style.setProperty('--progress-width', `${progressPercent}%`);
        }
    }
    
    // Initialisation de la progression
    updateProgress();
    
    // Navigation entre les étapes
    const nextButtons = document.querySelectorAll('.next-step');
    const prevButtons = document.querySelectorAll('.prev-step');
    
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const nextStep = this.getAttribute('data-step');
            goToStep(nextStep);
            updateProgress();
        });
    });
    
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const prevStep = this.getAttribute('data-step');
            goToStep(prevStep);
            updateProgress();
        });
    });
    
    function goToStep(stepNumber) {
        // Masque toutes les étapes
        document.querySelectorAll('.step-content').forEach(content => {
            content.classList.remove('active');
        });
        
        // Affiche l'étape demandée
        document.getElementById(`step-${stepNumber}`).classList.add('active');
        
        // Met à jour les indicateurs d'étape
        document.querySelectorAll('.progress-step').forEach(step => {
            step.classList.remove('active');
            if (parseInt(step.getAttribute('data-step')) < stepNumber) {
                step.classList.add('completed');
            } else if (parseInt(step.getAttribute('data-step')) == stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('completed');
            }
        });
        
        // Scroll vers le haut
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
});