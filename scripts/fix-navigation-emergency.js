// fix-navigation-emergency.js
// Correctif d'urgence pour la navigation défaillante

console.log('🚨 Correctif d\'urgence navigation - Résolution boucle infinie');

// Fonction pour réparer la navigation
function fixNavigationEmergency() {
    try {
        console.log('🔧 Réparation navigation en cours...');
        
        // Supprimer tous les event listeners problématiques
        const steps = document.querySelectorAll('.step');
        steps.forEach(step => {
            const newStep = step.cloneNode(true);
            step.parentNode.replaceChild(newStep, step);
        });
        
        // Ajouter une navigation simple et fonctionnelle
        document.querySelectorAll('.step').forEach(step => {
            step.addEventListener('click', function() {
                const targetStep = this.dataset.step;
                showStep(targetStep);
            });
        });
        
        // Réparer les boutons de navigation
        document.querySelectorAll('.next-step, .prev-step').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });
        
        // Ajouter les event listeners corrects
        document.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', function() {
                const targetStep = this.dataset.step;
                showStep(targetStep);
            });
        });
        
        document.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', function() {
                const targetStep = this.dataset.step;
                showStep(targetStep);
            });
        });
        
        console.log('✅ Navigation réparée');
        
    } catch (error) {
        console.error('❌ Erreur réparation navigation:', error);
    }
}

// Fonction pour afficher une étape
function showStep(stepNumber) {
    try {
        console.log(`🔄 Affichage étape ${stepNumber}`);
        
        // Masquer toutes les sections
        document.querySelectorAll('.form-section').forEach(section => {
            section.classList.remove('active');
            section.style.display = 'none';
        });
        
        // Afficher la section cible
        const targetSection = document.querySelector(`section[data-step="${stepNumber}"]`);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.style.display = 'block';
            console.log(`✅ Étape ${stepNumber} affichée`);
        } else {
            console.error(`❌ Section étape ${stepNumber} non trouvée`);
        }
        
        // Mettre à jour la navigation visuelle
        updateStepNavigation(stepNumber);
        
    } catch (error) {
        console.error('❌ Erreur affichage étape:', error);
    }
}

// Fonction pour mettre à jour la navigation visuelle
function updateStepNavigation(currentStep) {
    const steps = document.querySelectorAll('.step');
    
    steps.forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        
        if (stepNum < currentStep) {
            step.classList.add('completed');
        } else if (stepNum == currentStep) {
            step.classList.add('active');
        }
    });
    
    // Mettre à jour la barre de progression
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        const progress = ((currentStep - 1) / 3) * 100;
        progressFill.style.width = progress + '%';
    }
}

// Fonction pour afficher directement l'étape 3
function forceShowStep3() {
    console.log('🎯 Forçage affichage étape 3...');
    showStep(3);
    
    // Attendre un peu puis activer la section job parsing
    setTimeout(() => {
        const recruitmentYes = document.getElementById('recruitment-yes');
        if (recruitmentYes) {
            recruitmentYes.checked = true;
            recruitmentYes.dispatchEvent(new Event('change'));
            
            const jobParsingSection = document.getElementById('job-parsing-section');
            if (jobParsingSection) {
                jobParsingSection.classList.add('active');
                jobParsingSection.style.display = 'block';
                console.log('✅ Section job parsing activée');
            }
        }
    }, 500);
}

// Export pour utilisation externe
window.fixNavigationEmergency = {
    fix: fixNavigationEmergency,
    showStep: showStep,
    forceStep3: forceShowStep3
};

// Auto-exécution
console.log('🚀 Lancement correctif navigation...');
setTimeout(() => {
    fixNavigationEmergency();
    // Afficher automatiquement l'étape 3
    setTimeout(forceShowStep3, 1000);
}, 1000);

console.log('🔧 Correctif navigation chargé - auto-activation dans 2 secondes');