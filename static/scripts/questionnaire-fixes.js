// ===== CORRECTIONS QUESTIONNAIRE CANDIDAT - ÉTAPE 3 =====
// Fichier de correction des problèmes d'interaction dans l'étape 3
// 🎯 Motivations | 🏭 Secteurs | 💰 Fourchette salariale
// Version: 1.0 - Testé et validé

console.log('🚀 Chargement des corrections questionnaire candidat...');

// ===== 1. SYSTÈME DE CLASSEMENT DES MOTIVATIONS =====
window.motivationSystem = {
    selectedMotivations: [],
    maxSelections: 3,
    
    init() {
        console.log('📝 Initialisation système motivations...');
        
        // Ajouter les événements de clic sur les cartes
        const motivationCards = document.querySelectorAll('.motivation-card');
        motivationCards.forEach(card => {
            // Supprimer les anciens événements pour éviter les doublons
            card.replaceWith(card.cloneNode(true));
        });
        
        // Re-sélectionner après clonage
        document.querySelectorAll('.motivation-card').forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleCardClick(card);
            });
            
            // Support clavier
            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleCardClick(card);
                }
            });
        });
        
        this.updateCounter();
        console.log('✅ Système motivations initialisé');
    },
    
    handleCardClick(card) {
        const motivation = card.dataset.motivation;
        
        if (card.classList.contains('selected')) {
            // Désélectionner
            this.removeMotivation(motivation);
            card.classList.remove('selected');
        } else {
            // Sélectionner si limite non atteinte
            if (this.selectedMotivations.length < this.maxSelections) {
                this.addMotivation(motivation);
                card.classList.add('selected');
                
                // Gérer le champ "Autre"
                if (motivation === 'autre') {
                    this.showAutreField();
                }
            } else {
                this.showLimitMessage();
            }
        }
        
        this.updateDisplay();
    },
    
    addMotivation(motivation) {
        if (!this.selectedMotivations.includes(motivation)) {
            this.selectedMotivations.push(motivation);
        }
    },
    
    removeMotivation(motivation) {
        const index = this.selectedMotivations.indexOf(motivation);
        if (index > -1) {
            this.selectedMotivations.splice(index, 1);
        }
        
        if (motivation === 'autre') {
            this.hideAutreField();
        }
    },
    
    updateDisplay() {
        this.updateCounter();
        this.updateRankingBadges();
        this.updateSummary();
        this.updateHiddenFields();
    },
    
    updateCounter() {
        const counter = document.getElementById('motivation-counter');
        if (counter) {
            counter.textContent = `${this.selectedMotivations.length} / ${this.maxSelections} sélectionnées`;
        }
    },
    
    updateRankingBadges() {
        document.querySelectorAll('.motivation-card').forEach(card => {
            const motivation = card.dataset.motivation;
            const rank = this.selectedMotivations.indexOf(motivation) + 1;
            const badge = card.querySelector('.ranking-badge');
            
            if (rank > 0) {
                badge.textContent = rank;
                badge.className = `ranking-badge rank-${rank}`;
            }
        });
    },
    
    updateSummary() {
        const summary = document.getElementById('motivation-summary');
        const summaryList = document.getElementById('summary-list');
        
        if (this.selectedMotivations.length > 0) {
            summary.classList.add('active');
            
            const motivationNames = {
                'evolution': 'Perspectives d\'évolution',
                'salaire': 'Augmentation salariale', 
                'flexibilite': 'Flexibilité',
                'autre': 'Autre'
            };
            
            let html = '';
            this.selectedMotivations.forEach((motivation, index) => {
                html += `
                    <div class="summary-item">
                        <div class="summary-rank">${index + 1}</div>
                        <span>${motivationNames[motivation] || motivation}</span>
                    </div>
                `;
            });
            
            summaryList.innerHTML = html;
        } else {
            summary.classList.remove('active');
        }
    },
    
    updateHiddenFields() {
        const hiddenMotivations = document.getElementById('hidden-motivations');
        const hiddenRanking = document.getElementById('hidden-motivations-ranking');
        
        if (hiddenMotivations) {
            hiddenMotivations.value = this.selectedMotivations.join(',');
        }
        if (hiddenRanking) {
            hiddenRanking.value = JSON.stringify(this.selectedMotivations);
        }
    },
    
    showAutreField() {
        const autreField = document.getElementById('autre-field');
        if (autreField) {
            autreField.classList.add('active');
        }
    },
    
    hideAutreField() {
        const autreField = document.getElementById('autre-field');
        if (autreField) {
            autreField.classList.remove('active');
            const textarea = document.getElementById('autre-motivation-text');
            if (textarea) textarea.value = '';
        }
    },
    
    showLimitMessage() {
        const existingMessage = document.querySelector('.limit-message');
        if (existingMessage) existingMessage.remove();
        
        const message = document.createElement('div');
        message.className = 'limit-message';
        message.style.cssText = `
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #f59e0b, #d97706); color: white;
            padding: 16px 24px; border-radius: 12px; font-weight: 600; z-index: 10000;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        `;
        message.innerHTML = '⚠️ Vous avez déjà sélectionné 3 motivations maximum';
        
        document.body.appendChild(message);
        setTimeout(() => message.remove(), 3000);
    }
};

// ===== 2. SYSTÈME DES SECTEURS D'ACTIVITÉ =====
window.sectorsSystem = {
    selectedSectors: [],
    excludedSectors: [],
    allSectors: [
        { id: 'tech', name: 'Technologies de l\'information', description: 'Développement, IA, cybersécurité', icon: 'laptop-code' },
        { id: 'finance', name: 'Finance et banque', description: 'Banque, assurance, fintech', icon: 'university' },
        { id: 'sante', name: 'Santé et médical', description: 'Médecine, pharmaceutique, biotechnologies', icon: 'heartbeat' },
        { id: 'education', name: 'Éducation et formation', description: 'Enseignement, formation professionnelle', icon: 'graduation-cap' },
        { id: 'commerce', name: 'Commerce et retail', description: 'Vente, e-commerce, distribution', icon: 'shopping-cart' },
        { id: 'industrie', name: 'Industrie et manufacture', description: 'Production, automobile, aéronautique', icon: 'industry' },
        { id: 'energie', name: 'Énergie et environnement', description: 'Énergies renouvelables, développement durable', icon: 'leaf' },
        { id: 'transport', name: 'Transport et logistique', description: 'Transport, supply chain, livraison', icon: 'truck' },
        { id: 'immobilier', name: 'Immobilier et construction', description: 'BTP, promotion immobilière', icon: 'building' },
        { id: 'media', name: 'Médias et communication', description: 'Journalisme, publicité, marketing', icon: 'broadcast-tower' },
        { id: 'luxe', name: 'Luxe et mode', description: 'Mode, cosmétiques, joaillerie', icon: 'gem' },
        { id: 'agriculture', name: 'Agriculture et agroalimentaire', description: 'Agriculture, food-tech, nutrition', icon: 'seedling' },
        { id: 'services', name: 'Services aux entreprises', description: 'Conseil, RH, services généraux', icon: 'briefcase' },
        { id: 'culture', name: 'Culture et divertissement', description: 'Arts, spectacle, gaming', icon: 'masks-theater' },
        { id: 'sport', name: 'Sport et loisirs', description: 'Sport professionnel, équipements sportifs', icon: 'running' }
    ],
    
    init() {
        console.log('🏭 Initialisation système secteurs...');
        
        this.renderSectorOptions('secteurs-options', false);
        this.renderSectorOptions('redhibitoires-options', true);
        this.setupSearchFunctionality();
        
        console.log('✅ Système secteurs initialisé');
    },
    
    renderSectorOptions(containerId, isExcluded = false) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        this.allSectors.forEach(sector => {
            const option = document.createElement('div');
            option.className = 'dropdown-option';
            option.dataset.sectorId = sector.id;
            option.innerHTML = `
                <div class="option-checkbox">
                    <i class="fas fa-check" style="display: none;"></i>
                </div>
                <div class="option-icon">
                    <i class="fas fa-${sector.icon}"></i>
                </div>
                <div class="option-content">
                    <div class="option-name">${sector.name}</div>
                    <div class="option-description">${sector.description}</div>
                </div>
            `;
            
            option.addEventListener('click', () => {
                this.toggleSector(sector.id, isExcluded);
            });
            
            container.appendChild(option);
        });
    },
    
    setupSearchFunctionality() {
        // Secteurs passionnants
        const secteursSearch = document.getElementById('secteurs-search');
        if (secteursSearch) {
            secteursSearch.addEventListener('input', (e) => {
                this.filterSectors(e.target.value, 'secteurs-options');
            });
            
            secteursSearch.addEventListener('focus', () => {
                document.getElementById('secteurs-options').style.display = 'block';
            });
        }
        
        // Secteurs rédhibitoires
        const redhibitoiresSearch = document.getElementById('redhibitoires-search');
        if (redhibitoiresSearch) {
            redhibitoiresSearch.addEventListener('input', (e) => {
                this.filterSectors(e.target.value, 'redhibitoires-options');
            });
            
            redhibitoiresSearch.addEventListener('focus', () => {
                document.getElementById('redhibitoires-options').style.display = 'block';
            });
        }
        
        // Fermer dropdowns en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.modern-dropdown-container') && 
                !e.target.closest('.redhibitoires-container')) {
                document.querySelectorAll('.dropdown-options').forEach(option => {
                    option.style.display = 'none';
                });
            }
        });
    },
    
    filterSectors(searchTerm, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.style.display = 'block';
        
        container.querySelectorAll('.dropdown-option').forEach(option => {
            const name = option.querySelector('.option-name').textContent.toLowerCase();
            const description = option.querySelector('.option-description').textContent.toLowerCase();
            const matches = name.includes(searchTerm.toLowerCase()) || 
                          description.includes(searchTerm.toLowerCase());
            
            option.style.display = matches ? 'flex' : 'none';
        });
    },
    
    toggleSector(sectorId, isExcluded = false) {
        if (isExcluded) {
            this.toggleExcludedSector(sectorId);
        } else {
            this.toggleSelectedSector(sectorId);
        }
        
        this.updateDisplay();
        this.checkConflicts();
    },
    
    toggleSelectedSector(sectorId) {
        const index = this.selectedSectors.indexOf(sectorId);
        if (index > -1) {
            this.selectedSectors.splice(index, 1);
        } else {
            this.selectedSectors.push(sectorId);
        }
    },
    
    toggleExcludedSector(sectorId) {
        const index = this.excludedSectors.indexOf(sectorId);
        if (index > -1) {
            this.excludedSectors.splice(index, 1);
        } else {
            this.excludedSectors.push(sectorId);
        }
    },
    
    updateDisplay() {
        this.updateCounters();
        this.updateSelectedOptions();
        this.updateTags();
        this.updateHiddenFields();
    },
    
    updateCounters() {
        const secteursCounter = document.getElementById('secteurs-counter');
        const redhibitoiresCounter = document.getElementById('redhibitoires-counter');
        
        if (secteursCounter) {
            secteursCounter.textContent = `${this.selectedSectors.length} sélectionnés`;
        }
        if (redhibitoiresCounter) {
            redhibitoiresCounter.textContent = `${this.excludedSectors.length} exclus`;
        }
    },
    
    updateSelectedOptions() {
        document.querySelectorAll('.dropdown-option').forEach(option => {
            const sectorId = option.dataset.sectorId;
            const isInSelected = this.selectedSectors.includes(sectorId);
            const isInExcluded = this.excludedSectors.includes(sectorId);
            const checkbox = option.querySelector('.option-checkbox i');
            
            if (isInSelected || isInExcluded) {
                option.classList.add('selected');
                checkbox.style.display = 'block';
            } else {
                option.classList.remove('selected');
                checkbox.style.display = 'none';
            }
        });
    },
    
    updateTags() {
        this.updateSectorTags('secteurs-tags', 'secteurs-selected', this.selectedSectors, false);
        this.updateSectorTags('redhibitoires-tags', 'redhibitoires-selected', this.excludedSectors, true);
    },
    
    updateSectorTags(tagsId, containerId, sectors, isExcluded) {
        const container = document.getElementById(containerId);
        const tagsContainer = document.getElementById(tagsId);
        
        if (!container || !tagsContainer) return;
        
        if (sectors.length > 0) {
            container.classList.add('active');
            
            tagsContainer.innerHTML = '';
            sectors.forEach(sectorId => {
                const sector = this.allSectors.find(s => s.id === sectorId);
                if (sector) {
                    const tag = document.createElement('div');
                    tag.className = 'sector-tag';
                    tag.innerHTML = `
                        ${sector.name}
                        <i class="fas fa-times remove-tag" 
                           onclick="sectorsSystem.toggleSector('${sectorId}', ${isExcluded})"></i>
                    `;
                    tagsContainer.appendChild(tag);
                }
            });
        } else {
            container.classList.remove('active');
        }
    },
    
    updateHiddenFields() {
        const hiddenSecteurs = document.getElementById('hidden-secteurs');
        const hiddenRedhibitoires = document.getElementById('hidden-secteurs-redhibitoires');
        
        if (hiddenSecteurs) {
            hiddenSecteurs.value = this.selectedSectors.join(',');
        }
        if (hiddenRedhibitoires) {
            hiddenRedhibitoires.value = this.excludedSectors.join(',');
        }
    },
    
    checkConflicts() {
        const conflicts = this.selectedSectors.filter(id => this.excludedSectors.includes(id));
        const conflictWarning = document.getElementById('conflict-warning');
        
        if (conflicts.length > 0 && conflictWarning) {
            conflictWarning.classList.add('active');
        } else if (conflictWarning) {
            conflictWarning.classList.remove('active');
        }
    }
};

// ===== 3. SYSTÈME FOURCHETTE SALARIALE =====
window.salarySystem = {
    min: 40,
    max: 45,
    
    init() {
        console.log('💰 Initialisation système salaire...');
        
        const minInput = document.getElementById('salary-min');
        const maxInput = document.getElementById('salary-max');
        const minSlider = document.getElementById('salary-slider-min');
        const maxSlider = document.getElementById('salary-slider-max');
        
        // Événements pour les inputs
        if (minInput) {
            minInput.addEventListener('input', () => this.updateFromInput('min'));
            minInput.addEventListener('focus', () => this.addFocusClass('min'));
            minInput.addEventListener('blur', () => this.removeFocusClass('min'));
        }
        
        if (maxInput) {
            maxInput.addEventListener('input', () => this.updateFromInput('max'));
            maxInput.addEventListener('focus', () => this.addFocusClass('max'));
            maxInput.addEventListener('blur', () => this.removeFocusClass('max'));
        }
        
        // Événements pour les sliders
        if (minSlider) {
            minSlider.addEventListener('input', () => this.updateFromSlider('min'));
        }
        
        if (maxSlider) {
            maxSlider.addEventListener('input', () => this.updateFromSlider('max'));
        }
        
        // Événements pour les suggestions
        document.querySelectorAll('.salary-suggestion').forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const min = parseInt(suggestion.dataset.min);
                const max = parseInt(suggestion.dataset.max);
                this.setSalaryRange(min, max);
            });
        });
        
        this.updateDisplay();
        console.log('✅ Système salaire initialisé');
    },
    
    updateFromInput(type) {
        const input = document.getElementById(`salary-${type}`);
        const value = parseInt(input.value) || (type === 'min' ? 20 : 200);
        
        if (type === 'min') {
            this.min = Math.max(20, Math.min(value, this.max - 1));
        } else {
            this.max = Math.max(this.min + 1, Math.min(value, 200));
        }
        
        this.updateDisplay();
        this.validateRange();
    },
    
    updateFromSlider(type) {
        const slider = document.getElementById(`salary-slider-${type}`);
        const value = parseInt(slider.value);
        
        if (type === 'min') {
            this.min = Math.min(value, this.max - 1);
        } else {
            this.max = Math.max(value, this.min + 1);
        }
        
        this.updateDisplay();
        this.validateRange();
    },
    
    setSalaryRange(min, max) {
        this.min = min;
        this.max = max;
        this.updateDisplay();
        this.validateRange();
    },
    
    updateDisplay() {
        const minInput = document.getElementById('salary-min');
        const maxInput = document.getElementById('salary-max');
        const minSlider = document.getElementById('salary-slider-min');
        const maxSlider = document.getElementById('salary-slider-max');
        const display = document.getElementById('salary-display');
        
        if (minInput) minInput.value = this.min;
        if (maxInput) maxInput.value = this.max;
        if (minSlider) minSlider.value = this.min;
        if (maxSlider) maxSlider.value = this.max;
        
        // 🎯 CORRECTION PRINCIPALE : Mise à jour de l'affichage principal
        if (display) {
            display.textContent = `Entre ${this.min}K et ${this.max}K €`;
        }
        
        this.updateHiddenFields();
    },
    
    validateRange() {
        const validation = document.getElementById('salary-validation');
        
        if (this.min >= this.max) {
            if (validation) validation.classList.add('active');
            this.addErrorClass();
        } else {
            if (validation) validation.classList.remove('active');
            this.removeErrorClass();
        }
    },
    
    addFocusClass(type) {
        const group = document.getElementById(`salary-${type}-group`);
        if (group) group.classList.add('focused');
    },
    
    removeFocusClass(type) {
        const group = document.getElementById(`salary-${type}-group`);
        if (group) group.classList.remove('focused');
    },
    
    addErrorClass() {
        document.querySelectorAll('.salary-input-group').forEach(group => {
            group.classList.add('error');
        });
    },
    
    removeErrorClass() {
        document.querySelectorAll('.salary-input-group').forEach(group => {
            group.classList.remove('error');
        });
    },
    
    updateHiddenFields() {
        const hiddenMin = document.getElementById('hidden-salary-min');
        const hiddenMax = document.getElementById('hidden-salary-max');
        const hiddenRange = document.getElementById('hidden-salary-range');
        
        if (hiddenMin) hiddenMin.value = this.min;
        if (hiddenMax) hiddenMax.value = this.max;
        if (hiddenRange) hiddenRange.value = `${this.min}-${this.max}`;
    }
};

// ===== 4. INITIALISATION AUTOMATIQUE =====
function initializeQuestionnaireFixes() {
    console.log('🎯 Initialisation des corrections questionnaire...');
    
    // Attendre que les éléments soient disponibles
    const checkAndInit = () => {
        const motivationCards = document.querySelectorAll('.motivation-card');
        const secteursOptions = document.getElementById('secteurs-options');
        const salaryInputs = document.querySelectorAll('#salary-min, #salary-max');
        
        if (motivationCards.length > 0) {
            window.motivationSystem.init();
        }
        
        if (secteursOptions) {
            window.sectorsSystem.init();
        }
        
        if (salaryInputs.length > 0) {
            window.salarySystem.init();
        }
        
        console.log('🚀 Corrections questionnaire appliquées avec succès !');
    };
    
    // Initialiser immédiatement et après chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(checkAndInit, 200);
        });
    } else {
        setTimeout(checkAndInit, 100);
    }
}

// Initialiser les corrections
initializeQuestionnaireFixes();

console.log('✅ Fichier de corrections questionnaire candidat chargé');
