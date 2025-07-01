/**
 * NEXTEN V3.0 - JavaScript Interactions Corrigé
 * Corrige les problèmes d'affichage et améliore les secteurs d'activité
 */

class NextenQuestionnaire {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.contractRanking = [];
        this.selectedSecteurs = [];
        this.selectedRedhibitoires = [];
        
        // Liste étendue des secteurs (25+ secteurs)
        this.secteursList = [
            'Technologie / Informatique',
            'Finance / Banque / Assurance', 
            'Santé / Pharmaceutique',
            'Éducation / Formation',
            'Industrie / Manufacturing',
            'Commerce / Retail',
            'Automobile',
            'Énergie / Utilities',
            'Médias / Communication',
            'Télécommunications',
            'Immobilier',
            'Tourisme / Hôtellerie',
            'Agriculture / Agroalimentaire',
            'BTP / Construction',
            'Logistique / Transport',
            'Consulting / Services professionnels',
            'E-commerce / Digital',
            'Biotechnologie',
            'Aéronautique / Spatial',
            'Mode / Luxe',
            'Sports / Loisirs',
            'Juridique',
            'Art / Culture',
            'Environnement / Développement durable',
            'Recherche & Développement',
            'Sécurité',
            'Administration publique',
            'ONG / Associations'
        ];
        
        this.init();
    }

    init() {
        this.initializeStepNavigation();
        this.initializeContractRanking();
        this.initializeSecteurSelector();
        this.initializeRedhibitoireSelector();
        this.initializeSalarySlider();
        this.updateStepIndicator();
        this.handleDemoMode();
    }

    // Navigation entre étapes - CORRIGÉ
    initializeStepNavigation() {
        // Boutons Next
        document.querySelectorAll('[class*="next-step"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const stepNum = parseInt(btn.className.match(/next-step(\d+)/)?.[1]);
                if (stepNum) {
                    this.validateAndNextStep(stepNum);
                }
            });
        });

        // Boutons Back  
        document.querySelectorAll('[class*="back-step"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const stepNum = parseInt(btn.className.match(/back-step(\d+)/)?.[1]);
                if (stepNum) {
                    this.goToStep(stepNum);
                }
            });
        });

        // Navigation directe via indicateurs d'étapes
        document.querySelectorAll('.step').forEach((step, index) => {
            step.addEventListener('click', () => {
                this.goToStep(index + 1);
            });
        });
    }

    validateAndNextStep(currentStep) {
        if (this.validateStep(currentStep)) {
            this.goToStep(currentStep + 1);
        }
    }

    validateStep(step) {
        switch(step) {
            case 1:
                const name = document.getElementById('full-name')?.value;
                const job = document.getElementById('job-title')?.value;
                const address = document.getElementById('address')?.value;
                
                if (!name || !job || !address) {
                    this.showError('Veuillez remplir tous les champs obligatoires');
                    return false;
                }
                return true;
                
            case 2:
                const transport = document.querySelector('input[name="transport-method"]:checked');
                const office = document.querySelector('input[name="office-preference"]:checked');
                
                if (!transport || !office) {
                    this.showError('Veuillez sélectionner vos préférences de transport et de bureau');
                    return false;
                }
                return true;
                
            case 3:
                // Validation optionnelle pour les secteurs
                return true;
                
            default:
                return true;
        }
    }

    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.totalSteps) return;
        
        console.log(`🎯 Navigation de l'étape ${this.currentStep} vers ${stepNumber}`);
        
        // Masquer toutes les étapes
        document.querySelectorAll('.form-step').forEach(step => {
            step.style.display = 'none';
            step.classList.remove('active');
        });
        
        // Afficher l'étape cible - CORRECTION CRITIQUE
        const targetStep = document.querySelector(`.form-step${stepNumber}`);
        if (targetStep) {
            targetStep.style.display = 'block';
            targetStep.style.visibility = 'visible';
            targetStep.style.opacity = '1';
            targetStep.classList.add('active');
            
            // Scroll vers l'étape
            targetStep.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        this.currentStep = stepNumber;
        this.updateStepIndicator();
        
        console.log(`✅ Navigation terminée: étape ${stepNumber}`);
    }

    updateStepIndicator() {
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNum < this.currentStep) {
                step.classList.add('completed');
            } else if (stepNum === this.currentStep) {
                step.classList.add('active');
            }
        });
    }

    // Système de secteurs amélioré - NOUVELLE FONCTIONNALITÉ
    initializeSecteurSelector() {
        this.createSecteurDropdown('secteurs', 'Secteurs d\'activité qui vous intéressent');
    }

    initializeRedhibitoireSelector() {
        this.createSecteurDropdown('redhibitoires', 'Secteurs d\'activité rédhibitoires');
    }

    createSecteurDropdown(type, label) {
        const container = document.getElementById(`${type}-container`);
        if (!container) {
            console.warn(`Container ${type}-container non trouvé`);
            return;
        }

        container.innerHTML = `
            <div class="secteur-selector nexten-v3">
                <label class="secteur-label">${label}</label>
                <div class="secteur-dropdown">
                    <div class="secteur-search-container">
                        <input type="text" 
                               id="${type}-search" 
                               class="secteur-search" 
                               placeholder="Rechercher ou sélectionner..."
                               autocomplete="off">
                        <div class="secteur-arrow">▼</div>
                    </div>
                    <div class="secteur-options" id="${type}-options" style="display: none;">
                        ${this.secteursList.map(secteur => `
                            <div class="secteur-option" data-value="${secteur}">
                                <input type="checkbox" id="${type}-${secteur.replace(/\s+/g, '-').toLowerCase()}" 
                                       value="${secteur}">
                                <label for="${type}-${secteur.replace(/\s+/g, '-').toLowerCase()}">${secteur}</label>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="secteur-selected" id="${type}-selected"></div>
                <input type="hidden" name="${type}" id="hidden-${type}">
            </div>
        `;

        this.bindSecteurEvents(type);
    }

    bindSecteurEvents(type) {
        const searchInput = document.getElementById(`${type}-search`);
        const optionsContainer = document.getElementById(`${type}-options`);
        const selectedContainer = document.getElementById(`${type}-selected`);
        const hiddenInput = document.getElementById(`hidden-${type}`);

        // Afficher/masquer les options
        searchInput.addEventListener('click', () => {
            optionsContainer.style.display = optionsContainer.style.display === 'none' ? 'block' : 'none';
        });

        // Fermer lors du clic à l'extérieur
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.secteur-dropdown')) {
                optionsContainer.style.display = 'none';
            }
        });

        // Recherche en temps réel
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const options = optionsContainer.querySelectorAll('.secteur-option');
            
            options.forEach(option => {
                const text = option.textContent.toLowerCase();
                option.style.display = text.includes(query) ? 'block' : 'none';
            });
        });

        // Sélection des secteurs
        optionsContainer.addEventListener('change', (e) => {
            if (e.target.type === 'checkbox') {
                this.updateSelectedSecteurs(type);
            }
        });
    }

    updateSelectedSecteurs(type) {
        const selectedContainer = document.getElementById(`${type}-selected`);
        const hiddenInput = document.getElementById(`hidden-${type}`);
        const checkboxes = document.querySelectorAll(`#${type}-options input[type="checkbox"]:checked`);
        
        const selected = Array.from(checkboxes).map(cb => cb.value);
        
        // Mettre à jour l'affichage des tags
        selectedContainer.innerHTML = selected.map(secteur => `
            <div class="secteur-tag nexten-v3">
                <span>${secteur}</span>
                <button type="button" class="secteur-tag-remove" data-value="${secteur}">×</button>
            </div>
        `).join('');

        // Mettre à jour le champ caché
        hiddenInput.value = selected.join(',');

        // Gérer la suppression des tags
        selectedContainer.querySelectorAll('.secteur-tag-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const value = e.target.dataset.value;
                const checkbox = document.querySelector(`#${type}-options input[value="${value}"]`);
                if (checkbox) {
                    checkbox.checked = false;
                    this.updateSelectedSecteurs(type);
                }
            });
        });

        // Mettre à jour les arrays de classe
        if (type === 'secteurs') {
            this.selectedSecteurs = selected;
        } else if (type === 'redhibitoires') {
            this.selectedRedhibitoires = selected;
        }
    }

    // Slider de salaire amélioré
    initializeSalarySlider() {
        const minSlider = document.getElementById('salary-slider-min');
        const maxSlider = document.getElementById('salary-slider-max');
        const minInput = document.getElementById('salary-min');
        const maxInput = document.getElementById('salary-max');

        if (!minSlider || !maxSlider) return;

        const updateSalary = () => {
            let minVal = parseInt(minSlider.value);
            let maxVal = parseInt(maxSlider.value);

            // Empêcher les croisements
            if (minVal >= maxVal) {
                minVal = maxVal - 5000;
                minSlider.value = minVal;
            }

            if (minInput) minInput.value = minVal;
            if (maxInput) maxInput.value = maxVal;

            // Mise à jour visuelle
            this.updateSliderVisual(minSlider, maxSlider);
        };

        minSlider.addEventListener('input', updateSalary);
        maxSlider.addEventListener('input', updateSalary);
        
        // Synchronisation avec les inputs texte
        if (minInput) {
            minInput.addEventListener('input', () => {
                minSlider.value = minInput.value;
                updateSalary();
            });
        }
        
        if (maxInput) {
            maxInput.addEventListener('input', () => {
                maxSlider.value = maxInput.value;
                updateSalary();
            });
        }

        updateSalary();
    }

    updateSliderVisual(minSlider, maxSlider) {
        const minPercent = (minSlider.value - minSlider.min) / (minSlider.max - minSlider.min) * 100;
        const maxPercent = (maxSlider.value - minSlider.min) / (minSlider.max - minSlider.min) * 100;
        
        const track = document.querySelector('.salary-slider-track');
        if (track) {
            track.style.left = minPercent + '%';
            track.style.width = (maxPercent - minPercent) + '%';
        }
    }

    // Ranking des contrats
    initializeContractRanking() {
        const addButtons = document.querySelectorAll('.add-contract-button');
        
        addButtons.forEach(button => {
            button.addEventListener('click', () => {
                const contractType = button.dataset.contract || 
                    button.closest('.contract-option')?.dataset.contract ||
                    button.previousElementSibling?.textContent?.trim();
                
                if (contractType) {
                    this.addToRanking(contractType);
                }
            });
        });
    }

    addToRanking(contractType) {
        if (this.contractRanking.includes(contractType)) {
            this.showError('Ce type de contrat est déjà sélectionné');
            return;
        }

        this.contractRanking.push(contractType);
        this.updateRankingDisplay();
        this.updateContractHiddenFields();
    }

    updateRankingDisplay() {
        const container = document.getElementById('contract-ranking-display') || 
                         document.querySelector('.contract-ranking');
        
        if (!container) return;

        container.innerHTML = this.contractRanking.map((contract, index) => `
            <div class="ranking-item nexten-v3" data-index="${index}">
                <span class="ranking-number">${index + 1}</span>
                <span class="ranking-contract">${contract}</span>
                <button type="button" class="ranking-remove" data-contract="${contract}">×</button>
            </div>
        `).join('');

        // Ajout des event listeners pour la suppression
        container.querySelectorAll('.ranking-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const contract = e.target.dataset.contract;
                this.removeFromRanking(contract);
            });
        });
    }

    removeFromRanking(contractType) {
        this.contractRanking = this.contractRanking.filter(c => c !== contractType);
        this.updateRankingDisplay();
        this.updateContractHiddenFields();
    }

    updateContractHiddenFields() {
        const rankingField = document.getElementById('contract-ranking-order');
        if (rankingField) {
            rankingField.value = this.contractRanking.join(',');
        }
    }

    // Gestion du mode démo
    handleDemoMode() {
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('cv_data') && urlParams.get('cv_data') === 'available') {
            this.populateDemoData();
        }
    }

    populateDemoData() {
        // Remplissage automatique pour la démo
        setTimeout(() => {
            const fullName = document.getElementById('full-name');
            const jobTitle = document.getElementById('job-title');
            const address = document.getElementById('address');
            
            if (fullName && !fullName.value) fullName.value = 'Jean Dupont';
            if (jobTitle && !jobTitle.value) jobTitle.value = 'Développeur Full Stack';
            if (address && !address.value) address.value = 'Paris, France';
        }, 500);
    }

    // Utilitaires
    showError(message) {
        // Créer ou mettre à jour le message d'erreur
        let errorDiv = document.getElementById('nexten-error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'nexten-error-message';
            errorDiv.className = 'nexten-error nexten-v3';
            document.body.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        
        // Masquer après 5 secondes
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        let successDiv = document.getElementById('nexten-success-message');
        
        if (!successDiv) {
            successDiv = document.createElement('div');
            successDiv.id = 'nexten-success-message';
            successDiv.className = 'nexten-success nexten-v3';
            document.body.appendChild(successDiv);
        }
        
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 3000);
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initialisation NEXTEN V3.0 Questionnaire');
    window.nextenQuestionnaire = new NextenQuestionnaire();
});

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenQuestionnaire;
}