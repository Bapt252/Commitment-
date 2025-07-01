/**
 * NEXTEN V3.0 - JavaScript Interactions CORRIGÉ
 * 🔧 Corrige la navigation bloquée + implémente 25+ secteurs
 */

class NextenQuestionnaire {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.contractRanking = [];
        this.selectedSecteurs = [];
        this.selectedRedhibitoires = [];
        this.selectedMotivations = [];
        
        // 🆕 Liste étendue des secteurs (25+ secteurs)
        this.secteursList = [
            { id: 'tech', name: 'Technologie / Informatique', icon: 'fas fa-laptop-code' },
            { id: 'finance', name: 'Finance / Banque / Assurance', icon: 'fas fa-chart-line' },
            { id: 'sante', name: 'Santé / Pharmaceutique', icon: 'fas fa-heartbeat' },
            { id: 'education', name: 'Éducation / Formation', icon: 'fas fa-graduation-cap' },
            { id: 'industrie', name: 'Industrie / Manufacturing', icon: 'fas fa-industry' },
            { id: 'commerce', name: 'Commerce / Retail', icon: 'fas fa-shopping-cart' },
            { id: 'automobile', name: 'Automobile', icon: 'fas fa-car' },
            { id: 'energie', name: 'Énergie / Utilities', icon: 'fas fa-bolt' },
            { id: 'medias', name: 'Médias / Communication', icon: 'fas fa-broadcast-tower' },
            { id: 'telecoms', name: 'Télécommunications', icon: 'fas fa-wifi' },
            { id: 'immobilier', name: 'Immobilier', icon: 'fas fa-building' },
            { id: 'tourisme', name: 'Tourisme / Hôtellerie', icon: 'fas fa-plane' },
            { id: 'agriculture', name: 'Agriculture / Agroalimentaire', icon: 'fas fa-seedling' },
            { id: 'btp', name: 'BTP / Construction', icon: 'fas fa-hard-hat' },
            { id: 'logistique', name: 'Logistique / Transport', icon: 'fas fa-truck' },
            { id: 'consulting', name: 'Consulting / Services professionnels', icon: 'fas fa-briefcase' },
            { id: 'ecommerce', name: 'E-commerce / Digital', icon: 'fas fa-shopping-bag' },
            { id: 'biotech', name: 'Biotechnologie', icon: 'fas fa-dna' },
            { id: 'aeronautique', name: 'Aéronautique / Spatial', icon: 'fas fa-rocket' },
            { id: 'mode', name: 'Mode / Luxe', icon: 'fas fa-gem' },
            { id: 'sports', name: 'Sports / Loisirs', icon: 'fas fa-futbol' },
            { id: 'juridique', name: 'Juridique', icon: 'fas fa-gavel' },
            { id: 'culture', name: 'Art / Culture', icon: 'fas fa-palette' },
            { id: 'environnement', name: 'Environnement / Développement durable', icon: 'fas fa-leaf' },
            { id: 'recherche', name: 'Recherche & Développement', icon: 'fas fa-microscope' },
            { id: 'securite', name: 'Sécurité', icon: 'fas fa-shield-alt' },
            { id: 'public', name: 'Administration publique', icon: 'fas fa-landmark' },
            { id: 'ong', name: 'ONG / Associations', icon: 'fas fa-hands-helping' }
        ];
        
        this.init();
    }

    init() {
        console.log('🚀 Initialisation NEXTEN V3.0 - Version Corrigée');
        this.initializeStepNavigation();
        this.initializeMotivationRanking();
        this.initializeSecteurSelectors();
        this.initializeSalaryControls();
        this.initializeModernOptions();
        this.updateStepIndicator();
        this.handleDemoMode();
        
        // 🔧 Force l'affichage de l'étape 3 si nécessaire
        this.ensureStep3Visibility();
    }

    // 🔧 CORRECTION CRITIQUE: Navigation entre étapes
    initializeStepNavigation() {
        console.log('🔄 Initialisation navigation étapes...');
        
        // Boutons Next - CORRECTION des sélecteurs
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
                    console.log(`⚡ Clic sur ${id} → Étape ${targetStep}`);
                    if (this.validateStep(targetStep - 1)) {
                        this.goToStep(targetStep);
                    }
                });
            } else {
                console.warn(`⚠️ Bouton ${id} non trouvé`);
            }
        });

        // Boutons Back - CORRECTION des sélecteurs
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
                    console.log(`⚡ Retour ${id} → Étape ${targetStep}`);
                    this.goToStep(targetStep);
                });
            }
        });

        // Navigation directe via indicateurs d'étapes
        document.querySelectorAll('.step').forEach((step, index) => {
            step.addEventListener('click', () => {
                this.goToStep(index + 1);
            });
        });
    }

    // 🔧 CORRECTION CRITIQUE: Navigation vers les étapes
    goToStep(stepNumber) {
        if (stepNumber < 1 || stepNumber > this.totalSteps) {
            console.warn(`⚠️ Étape ${stepNumber} invalide`);
            return;
        }
        
        console.log(`🎯 Navigation: ${this.currentStep} → ${stepNumber}`);
        
        // Masquer toutes les étapes
        for (let i = 1; i <= this.totalSteps; i++) {
            const step = document.getElementById(`form-step${i}`);
            if (step) {
                step.style.display = 'none';
                step.style.visibility = 'hidden';
                step.style.opacity = '0';
                step.classList.remove('active');
            }
        }
        
        // 🔧 CORRECTION: Afficher l'étape cible avec multiple sélecteurs
        const targetSelectors = [
            `#form-step${stepNumber}`,
            `.form-step:nth-child(${stepNumber})`,
            `[data-step="${stepNumber}"]`
        ];
        
        let targetStep = null;
        for (const selector of targetSelectors) {
            targetStep = document.querySelector(selector);
            if (targetStep) break;
        }
        
        if (targetStep) {
            targetStep.style.display = 'block';
            targetStep.style.visibility = 'visible';
            targetStep.style.opacity = '1';
            targetStep.classList.add('active');
            
            // Scroll vers l'étape
            setTimeout(() => {
                targetStep.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest' 
                });
            }, 100);
            
            console.log(`✅ Étape ${stepNumber} affichée`);
        } else {
            console.error(`❌ Impossible de trouver l'étape ${stepNumber}`);
            this.forceShowStep3(); // Fallback pour l'étape 3
        }
        
        this.currentStep = stepNumber;
        this.updateStepIndicator();
    }

    // 🔧 FORCE l'affichage de l'étape 3 si problème
    forceShowStep3() {
        const step3 = document.querySelector('.form-step.nexten-v3-modern');
        if (step3) {
            step3.style.display = 'block !important';
            step3.style.visibility = 'visible !important';
            step3.style.opacity = '1 !important';
            step3.classList.add('active');
            console.log('🔧 Force affichage étape 3 activé');
        }
    }

    // 🔧 S'assurer que l'étape 3 est visible
    ensureStep3Visibility() {
        setTimeout(() => {
            const step3 = document.getElementById('form-step3');
            if (step3) {
                // Supprimer tout style qui pourrait cacher l'étape
                step3.style.display = '';
                step3.style.visibility = '';
                step3.style.opacity = '';
                
                // Ajouter des styles de forçage si nécessaire
                if (step3.offsetHeight === 0) {
                    step3.style.minHeight = '200px';
                    console.log('🔧 Hauteur minimale appliquée à l\'étape 3');
                }
            }
        }, 1000);
    }

    validateStep(step) {
        switch(step) {
            case 1:
                const name = document.getElementById('full-name')?.value;
                const job = document.getElementById('job-title')?.value;
                
                if (!name || !job) {
                    this.showNotification('Veuillez remplir tous les champs obligatoires', 'warning');
                    return false;
                }
                return true;
                
            case 2:
                const transport = document.querySelector('input[name="transport-method"]:checked');
                const office = document.querySelector('input[name="office-preference"]:checked');
                
                if (!transport || !office) {
                    this.showNotification('Veuillez sélectionner vos préférences', 'warning');
                    return false;
                }
                return true;
                
            default:
                return true;
        }
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

        // Mise à jour de la barre de progression
        const progress = ((this.currentStep - 1) / (this.totalSteps - 1)) * 100;
        const progressBar = document.getElementById('stepper-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }

    // 🆕 NOUVEAU: Système de ranking des motivations
    initializeMotivationRanking() {
        console.log('🎯 Initialisation système de ranking motivations...');
        
        const motivationCards = document.querySelectorAll('.motivation-card');
        const counter = document.getElementById('motivation-counter');
        const summary = document.getElementById('motivation-summary');
        const summaryList = document.getElementById('summary-list');
        const autreField = document.getElementById('autre-field');
        
        motivationCards.forEach(card => {
            card.addEventListener('click', () => {
                const motivation = card.dataset.motivation;
                
                if (card.classList.contains('selected')) {
                    this.removeMotivation(motivation);
                } else if (this.selectedMotivations.length < 3) {
                    this.addMotivation(motivation);
                } else {
                    this.showNotification('Vous ne pouvez sélectionner que 3 motivations maximum', 'warning');
                    card.classList.add('max-reached');
                    setTimeout(() => card.classList.remove('max-reached'), 600);
                }
                
                this.updateMotivationDisplay();
            });
        });
    }

    addMotivation(motivation) {
        if (!this.selectedMotivations.includes(motivation)) {
            this.selectedMotivations.push(motivation);
            
            const card = document.querySelector(`[data-motivation="${motivation}"]`);
            if (card) {
                card.classList.add('selected');
                const badge = card.querySelector('.ranking-badge');
                if (badge) {
                    badge.textContent = this.selectedMotivations.length;
                    badge.className = `ranking-badge rank-${this.selectedMotivations.length}`;
                }
            }
            
            // Afficher le champ "autre" si sélectionné
            if (motivation === 'autre') {
                const autreField = document.getElementById('autre-field');
                if (autreField) {
                    autreField.classList.add('active');
                }
            }
        }
    }

    removeMotivation(motivation) {
        const index = this.selectedMotivations.indexOf(motivation);
        if (index > -1) {
            this.selectedMotivations.splice(index, 1);
            
            const card = document.querySelector(`[data-motivation="${motivation}"]`);
            if (card) {
                card.classList.remove('selected');
            }
            
            // Masquer le champ "autre" si désélectionné
            if (motivation === 'autre') {
                const autreField = document.getElementById('autre-field');
                if (autreField) {
                    autreField.classList.remove('active');
                }
            }
            
            // Réorganiser les badges
            this.selectedMotivations.forEach((mot, idx) => {
                const motCard = document.querySelector(`[data-motivation="${mot}"]`);
                if (motCard) {
                    const badge = motCard.querySelector('.ranking-badge');
                    if (badge) {
                        badge.textContent = idx + 1;
                        badge.className = `ranking-badge rank-${idx + 1}`;
                    }
                }
            });
        }
    }

    updateMotivationDisplay() {
        // Mettre à jour le compteur
        const counter = document.getElementById('motivation-counter');
        if (counter) {
            counter.textContent = `${this.selectedMotivations.length} / 3 sélectionnées`;
        }

        // Mettre à jour le résumé
        const summary = document.getElementById('motivation-summary');
        const summaryList = document.getElementById('summary-list');
        
        if (this.selectedMotivations.length > 0 && summaryList) {
            summary?.classList.add('active');
            
            const motivationNames = {
                'evolution': 'Perspectives d\'évolution',
                'salaire': 'Augmentation salariale', 
                'flexibilite': 'Flexibilité',
                'autre': 'Autre motivation'
            };
            
            summaryList.innerHTML = this.selectedMotivations.map((mot, idx) => `
                <div class="summary-item">
                    <div class="summary-rank">${idx + 1}</div>
                    <span>${motivationNames[mot] || mot}</span>
                </div>
            `).join('');
        } else {
            summary?.classList.remove('active');
        }
        
        // Mettre à jour les champs cachés
        document.getElementById('hidden-motivations').value = this.selectedMotivations.join(',');
        document.getElementById('hidden-motivations-ranking').value = this.selectedMotivations.map((m, i) => `${m}:${i+1}`).join(',');
    }

    // 🆕 NOUVEAU: Système de secteurs avec dropdown moderne
    initializeSecteurSelectors() {
        console.log('🏭 Initialisation sélecteurs de secteurs...');
        
        this.createSecteurDropdown('secteurs', 'secteurs-options', 'secteurs-search', 'secteurs-counter', 'secteurs-tags');
        this.createSecteurDropdown('redhibitoires', 'redhibitoires-options', 'redhibitoires-search', 'redhibitoires-counter', 'redhibitoires-tags');
    }

    createSecteurDropdown(type, optionsId, searchId, counterId, tagsId) {
        const optionsContainer = document.getElementById(optionsId);
        const searchInput = document.getElementById(searchId);
        const counter = document.getElementById(counterId);
        const tagsContainer = document.getElementById(tagsId);
        
        if (!optionsContainer) {
            console.warn(`Container ${optionsId} non trouvé`);
            return;
        }

        // Créer les options
        optionsContainer.innerHTML = this.secteursList.map(secteur => `
            <div class="dropdown-option" data-value="${secteur.id}">
                <div class="option-checkbox">
                    <i class="fas fa-check" style="display: none;"></i>
                </div>
                <div class="option-icon">
                    <i class="${secteur.icon}"></i>
                </div>
                <div class="option-content">
                    <div class="option-name">${secteur.name}</div>
                    <div class="option-description">Secteur ${secteur.name.toLowerCase()}</div>
                </div>
            </div>
        `).join('');

        // Event listeners
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterSecteurs(e.target.value, optionsContainer);
            });
        }

        optionsContainer.addEventListener('click', (e) => {
            const option = e.target.closest('.dropdown-option');
            if (option) {
                this.toggleSecteur(option, type);
                this.updateSecteurDisplay(type, counterId, tagsId);
            }
        });
    }

    filterSecteurs(query, container) {
        const options = container.querySelectorAll('.dropdown-option');
        const searchTerm = query.toLowerCase();
        
        options.forEach(option => {
            const name = option.querySelector('.option-name').textContent.toLowerCase();
            const isVisible = name.includes(searchTerm);
            option.style.display = isVisible ? 'flex' : 'none';
        });
    }

    toggleSecteur(option, type) {
        const value = option.dataset.value;
        const secteur = this.secteursList.find(s => s.id === value);
        
        if (option.classList.contains('selected')) {
            // Désélectionner
            option.classList.remove('selected');
            option.querySelector('.option-checkbox i').style.display = 'none';
            
            if (type === 'secteurs') {
                this.selectedSecteurs = this.selectedSecteurs.filter(s => s.id !== value);
            } else {
                this.selectedRedhibitoires = this.selectedRedhibitoires.filter(s => s.id !== value);
            }
        } else {
            // Sélectionner
            option.classList.add('selected');
            option.querySelector('.option-checkbox i').style.display = 'block';
            
            if (type === 'secteurs') {
                this.selectedSecteurs.push(secteur);
            } else {
                this.selectedRedhibitoires.push(secteur);
            }
        }
        
        this.checkSecteurConflicts();
    }

    updateSecteurDisplay(type, counterId, tagsId) {
        const counter = document.getElementById(counterId);
        const tagsContainer = document.getElementById(tagsId);
        const selectedContainer = document.getElementById(`${type}-selected`);
        
        const selectedList = type === 'secteurs' ? this.selectedSecteurs : this.selectedRedhibitoires;
        
        // Mettre à jour le compteur
        if (counter) {
            const countText = type === 'secteurs' ? 'sélectionnés' : 'exclus';
            counter.textContent = `${selectedList.length} ${countText}`;
        }

        // Mettre à jour les tags
        if (tagsContainer) {
            tagsContainer.innerHTML = selectedList.map(secteur => `
                <div class="sector-tag">
                    <i class="${secteur.icon}"></i>
                    <span>${secteur.name}</span>
                    <i class="fas fa-times remove-tag" data-value="${secteur.id}" data-type="${type}"></i>
                </div>
            `).join('');
            
            // Event listeners pour suppression
            tagsContainer.querySelectorAll('.remove-tag').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const secteurId = e.target.dataset.value;
                    const option = document.querySelector(`[data-value="${secteurId}"]`);
                    if (option) {
                        this.toggleSecteur(option, type);
                        this.updateSecteurDisplay(type, counterId, tagsId);
                    }
                });
            });
        }

        // Afficher/masquer le conteneur de sélection
        if (selectedContainer) {
            selectedContainer.classList.toggle('active', selectedList.length > 0);
        }
        
        // Mettre à jour les champs cachés
        document.getElementById(`hidden-${type}`).value = selectedList.map(s => s.name).join(',');
    }

    checkSecteurConflicts() {
        const conflictIds = this.selectedSecteurs
            .filter(s => this.selectedRedhibitoires.some(r => r.id === s.id))
            .map(s => s.id);
        
        const warning = document.getElementById('conflict-warning');
        if (warning) {
            warning.classList.toggle('active', conflictIds.length > 0);
        }
    }

    // 🆕 Contrôles de fourchette salariale
    initializeSalaryControls() {
        console.log('💰 Initialisation contrôles salariaux...');
        
        const minInput = document.getElementById('salary-min');
        const maxInput = document.getElementById('salary-max');
        const minSlider = document.getElementById('salary-slider-min');
        const maxSlider = document.getElementById('salary-slider-max');
        const display = document.getElementById('salary-display');
        const validation = document.getElementById('salary-validation');

        if (!minInput || !maxInput) return;

        const updateSalary = () => {
            let minVal = parseInt(minInput.value) || 20;
            let maxVal = parseInt(maxInput.value) || 200;

            // Validation
            if (minVal >= maxVal) {
                validation?.classList.add('active');
                minInput.parentElement.classList.add('error');
                maxInput.parentElement.classList.add('error');
                return;
            } else {
                validation?.classList.remove('active');
                minInput.parentElement.classList.remove('error');
                maxInput.parentElement.classList.remove('error');
            }

            // Synchronisation des sliders
            if (minSlider) minSlider.value = minVal;
            if (maxSlider) maxSlider.value = maxVal;

            // Mise à jour de l'affichage
            if (display) {
                display.textContent = `Entre ${minVal}K et ${maxVal}K €`;
            }

            // Champs cachés
            document.getElementById('hidden-salary-min').value = minVal;
            document.getElementById('hidden-salary-max').value = maxVal;
            document.getElementById('hidden-salary-range').value = `${minVal}-${maxVal}`;
        };

        // Event listeners
        [minInput, maxInput].forEach(input => {
            input.addEventListener('input', updateSalary);
            input.addEventListener('focus', () => input.parentElement.classList.add('focused'));
            input.addEventListener('blur', () => input.parentElement.classList.remove('focused'));
        });

        [minSlider, maxSlider].forEach(slider => {
            if (slider) {
                slider.addEventListener('input', () => {
                    if (slider === minSlider) minInput.value = slider.value;
                    if (slider === maxSlider) maxInput.value = slider.value;
                    updateSalary();
                });
            }
        });

        // Suggestions rapides
        document.querySelectorAll('.salary-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const min = suggestion.dataset.min;
                const max = suggestion.dataset.max;
                
                minInput.value = min;
                maxInput.value = max;
                updateSalary();
                
                suggestion.classList.add('applied');
                setTimeout(() => suggestion.classList.remove('applied'), 600);
            });
        });

        updateSalary();
    }

    // 🆕 Options modernes (étape 4)
    initializeModernOptions() {
        console.log('⚙️ Initialisation options modernes...');
        
        // Options radio/checkbox modernes
        document.querySelectorAll('.modern-option').forEach(option => {
            option.addEventListener('click', () => {
                const group = option.dataset.optionGroup;
                const value = option.dataset.value;
                
                if (group) {
                    // Radio behavior: une seule sélection par groupe
                    document.querySelectorAll(`[data-option-group="${group}"]`).forEach(opt => {
                        opt.classList.remove('selected');
                    });
                    option.classList.add('selected');
                    
                    document.getElementById(`hidden-${group}`).value = value;
                }
            });
        });

        // Cards interactives
        document.querySelectorAll('.interactive-card').forEach(card => {
            card.addEventListener('click', () => {
                const group = card.dataset.cardGroup;
                const value = card.dataset.value;
                
                if (group) {
                    document.querySelectorAll(`[data-card-group="${group}"]`).forEach(c => {
                        c.classList.remove('selected');
                    });
                    card.classList.add('selected');
                    
                    document.getElementById(`hidden-${group}`).value = value;
                }
            });
        });
    }

    // Mode démo
    handleDemoMode() {
        const urlParams = new URLSearchParams(window.location.search);
        
        if (urlParams.has('cv_data') && urlParams.get('cv_data') === 'available') {
            console.log('🎭 Mode démo activé');
            this.populateDemoData();
        }
    }

    populateDemoData() {
        setTimeout(() => {
            const fullName = document.getElementById('full-name');
            const jobTitle = document.getElementById('job-title');
            const address = document.getElementById('address');
            
            if (fullName && !fullName.value) fullName.value = 'Jean Dupont';
            if (jobTitle && !jobTitle.value) jobTitle.value = 'Développeur Full Stack';
            if (address && !address.value) address.value = '1 Place Vendôme, 75001 Paris';
            
            this.showNotification('Données de démonstration chargées', 'success');
        }, 500);
    }

    // Notifications
    showNotification(message, type = 'info') {
        // Supprimer les anciennes notifications
        document.querySelectorAll('.nexten-v3-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `nexten-v3-notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
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

// 🚀 Initialisation globale
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Démarrage NEXTEN V3.0 - Version Corrigée');
    
    // Attendre que tous les scripts soient chargés
    setTimeout(() => {
        window.nextenQuestionnaire = new NextenQuestionnaire();
        console.log('✅ NEXTEN V3.0 initialisé avec succès');
    }, 500);
});

// Export pour utilisation externe
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NextenQuestionnaire;
}