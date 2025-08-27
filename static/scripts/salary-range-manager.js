/**
 * 🚀 NEXTEN V3.0 - Gestionnaire de Fourchette Salariale
 * Système moderne avec validation, suggestions et intégration backend
 */
class SalaryRangeManager {
    constructor() {
        this.minInput = null;
        this.maxInput = null;
        this.displayElement = null;
        this.previewElement = null;
        this.validationElement = null;
        this.hiddenMinField = null;
        this.hiddenMaxField = null;
        this.hiddenRangeField = null;
        
        this.debounceTimer = null;
        this.isValidating = false;
        
        this.init();
    }

    init() {
        console.log('💰 Initialisation SalaryRangeManager NEXTEN V3.0');
        this.setupElements();
        this.setupEventListeners();
        this.loadSavedData();
        this.updateDisplay();
    }

    setupElements() {
        this.minInput = document.getElementById('salary-min');
        this.maxInput = document.getElementById('salary-max');
        this.displayElement = document.getElementById('salary-range-display');
        this.previewElement = document.getElementById('preview-range');
        this.validationElement = document.getElementById('salary-validation');
        this.hiddenMinField = document.getElementById('hidden-salary-min');
        this.hiddenMaxField = document.getElementById('hidden-salary-max');
        this.hiddenRangeField = document.getElementById('hidden-salary-range');

        if (!this.minInput || !this.maxInput) {
            console.warn('⚠️ Éléments de fourchette salariale non trouvés');
            return false;
        }

        console.log('✅ Éléments de fourchette salariale initialisés');
        return true;
    }

    setupEventListeners() {
        if (!this.minInput || !this.maxInput) return;

        // Écoute des changements de valeur avec debounce
        this.minInput.addEventListener('input', (e) => this.handleInputChange(e, 'min'));
        this.maxInput.addEventListener('input', (e) => this.handleInputChange(e, 'max'));

        // Validation en temps réel
        this.minInput.addEventListener('blur', () => this.validateRange());
        this.maxInput.addEventListener('blur', () => this.validateRange());

        // Gestion du clavier (Enter pour validation)
        this.minInput.addEventListener('keydown', (e) => this.handleKeyboard(e));
        this.maxInput.addEventListener('keydown', (e) => this.handleKeyboard(e));

        // Options rapides
        document.querySelectorAll('.quick-option').forEach(button => {
            button.addEventListener('click', (e) => this.handleQuickOption(e));
        });

        console.log('✅ Event listeners fourchette salariale configurés');
    }

    handleInputChange(event, type) {
        clearTimeout(this.debounceTimer);
        
        const input = event.target;
        const value = parseInt(input.value) || 0;

        // Validation immédiate des limites
        if (value < 20) {
            input.value = 20;
        } else if (value > 300) {
            input.value = 300;
        }

        // Mise à jour avec debounce
        this.debounceTimer = setTimeout(() => {
            this.validateRange();
            this.updateDisplay();
            this.saveData();
        }, 300);
    }

    handleKeyboard(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            this.validateRange();
        }
        
        // Permettre seulement les chiffres et touches de navigation
        const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 
                           'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
        
        if (!allowedKeys.includes(event.key) && 
            (event.key < '0' || event.key > '9') && 
            !(event.key >= '0' && event.key <= '9')) {
            event.preventDefault();
        }
    }

    handleQuickOption(event) {
        const button = event.currentTarget;
        const min = parseInt(button.dataset.min);
        const max = parseInt(button.dataset.max);

        if (!min || !max) return;

        // Animation du bouton
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = '';
        }, 150);

        // Mise à jour des valeurs
        this.minInput.value = min;
        this.maxInput.value = max;

        // Effet visuel sur les inputs
        this.animateInput(this.minInput);
        this.animateInput(this.maxInput);

        // Validation et mise à jour
        this.validateRange();
        this.updateDisplay();
        this.saveData();

        console.log(`💡 Option rapide sélectionnée: ${min}K-${max}K €`);
    }

    animateInput(input) {
        input.style.transform = 'scale(1.05)';
        input.style.borderColor = '#10b981';
        
        setTimeout(() => {
            input.style.transform = '';
            input.style.borderColor = '';
        }, 300);
    }

    validateRange() {
        if (this.isValidating) return;
        this.isValidating = true;

        const min = parseInt(this.minInput.value) || 0;
        const max = parseInt(this.maxInput.value) || 0;
        let isValid = true;
        let errorMessage = '';

        // Validation de base
        if (min < 20) {
            isValid = false;
            errorMessage = 'Le salaire minimum ne peut pas être inférieur à 20K €';
            this.markInputError(this.minInput);
        } else if (max > 300) {
            isValid = false;
            errorMessage = 'Le salaire maximum ne peut pas dépasser 300K €';
            this.markInputError(this.maxInput);
        } else if (min >= max) {
            isValid = false;
            errorMessage = 'Le salaire maximum doit être supérieur au minimum';
            this.markInputError(this.maxInput);
        } else {
            // Validation réussie
            this.markInputValid(this.minInput);
            this.markInputValid(this.maxInput);
        }

        // Affichage du message d'erreur
        if (isValid) {
            this.hideValidationError();
        } else {
            this.showValidationError(errorMessage);
        }

        this.isValidating = false;
        return isValid;
    }

    markInputError(input) {
        input.classList.remove('valid');
        input.classList.add('error');
    }

    markInputValid(input) {
        input.classList.remove('error');
        input.classList.add('valid');
    }

    showValidationError(message) {
        if (!this.validationElement) return;

        const messageSpan = document.getElementById('validation-message');
        if (messageSpan) {
            messageSpan.textContent = message;
        }

        this.validationElement.style.display = 'flex';
        this.validationElement.classList.add('show');
    }

    hideValidationError() {
        if (!this.validationElement) return;

        this.validationElement.style.display = 'none';
        this.validationElement.classList.remove('show');
    }

    updateDisplay() {
        const min = parseInt(this.minInput.value) || 25;
        const max = parseInt(this.maxInput.value) || 120;

        const displayText = `Entre ${min}K € et ${max}K €`;
        
        // Mise à jour de l'affichage principal
        if (this.displayElement) {
            this.displayElement.textContent = displayText;
        }

        // Mise à jour de la prévisualisation
        if (this.previewElement) {
            this.previewElement.textContent = displayText;
        }

        // Mise à jour des champs cachés pour le backend
        this.updateHiddenFields(min, max);

        console.log(`📊 Affichage mis à jour: ${displayText}`);
    }

    updateHiddenFields(min, max) {
        if (this.hiddenMinField) {
            this.hiddenMinField.value = min * 1000; // Conversion en euros
        }
        
        if (this.hiddenMaxField) {
            this.hiddenMaxField.value = max * 1000; // Conversion en euros
        }
        
        if (this.hiddenRangeField) {
            this.hiddenRangeField.value = `${min * 1000}-${max * 1000}`;
        }
    }

    saveData() {
        try {
            const data = {
                min: parseInt(this.minInput.value) || 25,
                max: parseInt(this.maxInput.value) || 120,
                lastSaved: new Date().toISOString(),
                version: '3.0'
            };

            localStorage.setItem('nexten_salary_range_v3', JSON.stringify(data));
            console.log('💾 Fourchette salariale sauvegardée:', data);
        } catch (error) {
            console.error('❌ Erreur sauvegarde fourchette salariale:', error);
        }
    }

    loadSavedData() {
        try {
            const saved = localStorage.getItem('nexten_salary_range_v3');
            if (saved) {
                const data = JSON.parse(saved);
                
                if (this.minInput && data.min) {
                    this.minInput.value = data.min;
                }
                
                if (this.maxInput && data.max) {
                    this.maxInput.value = data.max;
                }

                console.log('📂 Fourchette salariale restaurée:', data);
            }
        } catch (error) {
            console.error('❌ Erreur restauration fourchette salariale:', error);
        }
    }

    // Méthodes publiques pour intégration
    getSalaryRange() {
        return {
            min: parseInt(this.minInput?.value) || 25,
            max: parseInt(this.maxInput?.value) || 120,
            minInEuros: (parseInt(this.minInput?.value) || 25) * 1000,
            maxInEuros: (parseInt(this.maxInput?.value) || 120) * 1000,
            display: `Entre ${parseInt(this.minInput?.value) || 25}K € et ${parseInt(this.maxInput?.value) || 120}K €`
        };
    }

    setSalaryRange(min, max) {
        if (this.minInput) this.minInput.value = min;
        if (this.maxInput) this.maxInput.value = max;
        
        this.validateRange();
        this.updateDisplay();
        this.saveData();
    }

    isValid() {
        return this.validateRange();
    }

    reset() {
        if (this.minInput) this.minInput.value = 25;
        if (this.maxInput) this.maxInput.value = 120;
        
        this.hideValidationError();
        this.updateDisplay();
        this.saveData();
        
        console.log('🔄 Fourchette salariale réinitialisée');
    }
}

// Initialisation automatique quand le DOM est prêt
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        window.salaryRangeManager = new SalaryRangeManager();
        
        // Exposer pour debugging
        console.log('✅ SalaryRangeManager NEXTEN V3.0 initialisé');
        console.log('🛠️ Commandes debug disponibles:');
        console.log('   - salaryRangeManager.getSalaryRange() - Voir la fourchette');
        console.log('   - salaryRangeManager.setSalaryRange(35, 50) - Définir fourchette');
        console.log('   - salaryRangeManager.isValid() - Valider');
        console.log('   - salaryRangeManager.reset() - Réinitialiser');
    }, 500);
});