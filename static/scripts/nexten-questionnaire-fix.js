/**
 * 🔧 CORRECTION URGENTE : Questionnaire Candidat - Affichage Étapes 2, 3, 4
 * Script de correction pour résoudre le problème d'affichage des étapes
 */

class QuestionnaireStepsFix {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.isInitialized = false;
        
        console.log('🔧 Initialisation de la correction des étapes...');
        this.init();
    }

    init() {
        // Éviter la double initialisation
        if (this.isInitialized) {
            console.log('⚠️ Correction déjà initialisée');
            return;
        }

        // Attendre que le DOM soit prêt
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupSteps());
        } else {
            setTimeout(() => this.setupSteps(), 100);
        }
    }

    setupSteps() {
        try {
            console.log('🔧 Configuration des étapes...');
            
            // Vérifier que les étapes existent
            const stepsExist = this.validateStepsExist();
            if (!stepsExist) {
                console.error('❌ Les étapes du questionnaire sont introuvables');
                return;
            }

            // Nettoyer les anciens event listeners
            this.cleanupOldListeners();
            
            // Configurer l'affichage initial
            this.setupInitialDisplay();
            
            // Ajouter les event listeners de navigation
            this.setupNavigation();
            
            // Marquer comme initialisé
            this.isInitialized = true;
            
            console.log('✅ Correction des étapes appliquée avec succès');
            
        } catch (error) {
            console.error('❌ Erreur lors de la configuration:', error);
        }
    }

    validateStepsExist() {
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`form-step${i}`);
            if (!step) {
                console.error(`❌ Étape ${i} introuvable`);
                return false;
            }
        }
        return true;
    }

    cleanupOldListeners() {
        // Désactiver les anciens scripts problématiques
        if (window.nextenQuestionnaire) {
            console.log('🧹 Nettoyage ancienne instance');
            window.nextenQuestionnaire = null;
        }
        
        // Supprimer les event listeners existants sur les boutons
        document.querySelectorAll('.btn-next, .btn-back').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
        });
    }

    setupInitialDisplay() {
        // Masquer toutes les étapes d'abord
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`form-step${i}`);
            if (step) {
                step.style.display = 'none';
                step.classList.remove('active');
            }
        }
        
        // Afficher seulement l'étape 1
        const step1 = document.getElementById('form-step1');
        if (step1) {
            step1.style.display = 'block';
            step1.classList.add('active');
        }
        
        this.updateStepIndicator();
        console.log('📋 Affichage initial configuré - Étape 1 visible');
    }

    setupNavigation() {
        // Configuration des boutons Next
        const nextButtons = [
            { id: 'next-step1', targetStep: 2 },
            { id: 'next-step2', targetStep: 3 },
            { id: 'next-step3', targetStep: 4 }
        ];
        
        nextButtons.forEach(({ id, targetStep }) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`▶️ Navigation: Étape ${targetStep}`);
                    
                    if (this.validateCurrentStep()) {
                        this.goToStep(targetStep);
                    }
                });
                console.log(`✅ Bouton ${id} configuré`);
            }
        });

        // Configuration des boutons Back
        const backButtons = [
            { id: 'back-step1', targetStep: 1 },
            { id: 'back-step2', targetStep: 2 },
            { id: 'back-step3', targetStep: 3 }
        ];
        
        backButtons.forEach(({ id, targetStep }) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`◀️ Retour: Étape ${targetStep}`);
                    this.goToStep(targetStep);
                });
                console.log(`✅ Bouton retour ${id} configuré`);
            }
        });
    }

    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.totalSteps) {
            console.warn(`⚠️ Numéro d'étape invalide: ${stepNumber}`);
            return false;
        }

        console.log(`🎯 Navigation: ${this.currentStep} → ${stepNumber}`);
        
        try {
            // Masquer toutes les étapes
            for (let i = 1; i <= this.totalSteps; i++) {
                const step = document.getElementById(`form-step${i}`);
                if (step) {
                    step.style.display = 'none';
                    step.classList.remove('active');
                }
            }
            
            // Afficher l'étape cible
            const targetStep = document.getElementById(`form-step${stepNumber}`);
            if (targetStep) {
                targetStep.style.display = 'block';
                targetStep.classList.add('active');
                
                // Scroll vers l'étape
                setTimeout(() => {
                    targetStep.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }, 100);
                
                this.currentStep = stepNumber;
                this.updateStepIndicator();
                
                console.log(`✅ Étape ${stepNumber} affichée avec succès`);
                this.showNotification(`Étape ${stepNumber} affichée`, 'success');
                
                return true;
            } else {
                console.error(`❌ Étape ${stepNumber} introuvable dans le DOM`);
                return false;
            }
        } catch (error) {
            console.error('❌ Erreur lors de la navigation:', error);
            return false;
        }
    }

    updateStepIndicator() {
        // Mettre à jour les indicateurs visuels dans le stepper
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNum < this.currentStep) {
                step.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
            }
        });

        // Mettre à jour la barre de progression
        const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
        const progressBar = document.getElementById('stepper-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        console.log(`📊 Indicateur mis à jour - Étape ${this.currentStep} (${progress}%)`);
    }

    validateCurrentStep() {
        // Validation simple pour permettre la navigation
        const step = this.currentStep;
        
        try {
            switch(step) {
                case 1:
                    const name = document.getElementById('full-name')?.value;
                    const jobTitle = document.getElementById('job-title')?.value;
                    
                    if (!name || name.trim() === '') {
                        this.showNotification('Veuillez renseigner votre nom et prénom', 'warning');
                        return false;
                    }
                    if (!jobTitle || jobTitle.trim() === '') {
                        this.showNotification('Veuillez renseigner l\'intitulé de poste souhaité', 'warning');
                        return false;
                    }
                    return true;
                    
                case 2:
                    const transport = document.querySelector('input[name="transport-method"]:checked');
                    const office = document.querySelector('input[name="office-preference"]:checked');
                    
                    if (!transport) {
                        this.showNotification('Veuillez sélectionner au moins un mode de transport', 'warning');
                        return false;
                    }
                    if (!office) {
                        this.showNotification('Veuillez sélectionner votre préférence d\'environnement de travail', 'warning');
                        return false;
                    }
                    return true;
                    
                case 3:
                    // Validation plus souple pour l'étape 3
                    return true;
                    
                default:
                    return true;
            }
        } catch (error) {
            console.error('❌ Erreur lors de la validation:', error);
            return true; // Permettre la navigation en cas d'erreur de validation
        }
    }

    showNotification(message, type = 'info') {
        // Supprimer les anciennes notifications
        document.querySelectorAll('.questionnaire-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = 'questionnaire-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: 500;
            font-size: 14px;
            max-width: 350px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
        `;
        
        const icon = this.getNotificationIcon(type);
        notification.innerHTML = `<i class="fas fa-${icon}" style="margin-right: 8px;"></i>${message}`;
        
        document.body.appendChild(notification);
        
        // Animation d'entrée
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Suppression automatique
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'linear-gradient(135deg, #10b981, #059669)',
            'warning': 'linear-gradient(135deg, #f59e0b, #d97706)', 
            'error': 'linear-gradient(135deg, #ef4444, #dc2626)',
            'info': 'linear-gradient(135deg, #3b82f6, #2563eb)'
        };
        return colors[type] || colors.info;
    }

    getNotificationIcon(type) {
        const icons = {
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'times-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Test de navigation directe (fonctions globales pour débogage)
window.testNavigation = {
    goToStep2: () => {
        console.log('🧪 Test navigation vers étape 2');
        if (window.questionnaireStepsFix) {
            window.questionnaireStepsFix.goToStep(2);
        }
    },
    goToStep3: () => {
        console.log('🧪 Test navigation vers étape 3');
        if (window.questionnaireStepsFix) {
            window.questionnaireStepsFix.goToStep(3);
        }
    },
    goToStep4: () => {
        console.log('🧪 Test navigation vers étape 4');
        if (window.questionnaireStepsFix) {
            window.questionnaireStepsFix.goToStep(4);
        }
    }
};

// Initialisation SÉCURISÉE
(function() {
    console.log('🔧 Démarrage de la correction du questionnaire...');
    
    // Éviter les conflits avec les autres scripts
    const initFix = () => {
        try {
            if (!window.questionnaireStepsFix) {
                window.questionnaireStepsFix = new QuestionnaireStepsFix();
                console.log('✅ Correction du questionnaire initialisée');
            }
        } catch (error) {
            console.error('❌ Erreur lors de l\'initialisation de la correction:', error);
        }
    };

    // Plusieurs tentatives d'initialisation pour assurer la robustesse
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initFix);
    } else {
        setTimeout(initFix, 100);
    }
    
    // Backup d'initialisation après chargement complet
    window.addEventListener('load', () => {
        setTimeout(() => {
            if (!window.questionnaireStepsFix) {
                console.log('🔄 Initialisation de secours...');
                initFix();
            }
        }, 500);
    });
})();
