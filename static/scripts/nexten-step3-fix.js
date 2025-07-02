/**
 * 🔧 CORRECTION COMPLÈTE ÉTAPE 3 : Motivations, Secteurs, Salaire
 * Script de correction pour résoudre tous les problèmes de l'étape 3
 */

class NextenStep3Fix {
    constructor() {
        this.selectedMotivations = [];
        this.selectedSecteurs = [];
        this.selectedRedhibitoires = [];
        this.salaryMin = 40;
        this.salaryMax = 45;
        this.maxMotivations = 3;
        
        // Base de données des secteurs
        this.secteursList = [
            { id: 'tech', name: 'Technologie / Informatique', icon: 'fas fa-laptop-code', description: 'Développement, IA, cybersécurité' },
            { id: 'finance', name: 'Finance / Banque / Assurance', icon: 'fas fa-chart-line', description: 'Services financiers, investissement' },
            { id: 'sante', name: 'Santé / Pharmaceutique', icon: 'fas fa-heartbeat', description: 'Médical, recherche pharmaceutique' },
            { id: 'education', name: 'Éducation / Formation', icon: 'fas fa-graduation-cap', description: 'Enseignement, formation professionnelle' },
            { id: 'industrie', name: 'Industrie / Manufacturing', icon: 'fas fa-industry', description: 'Production, ingénierie industrielle' },
            { id: 'commerce', name: 'Commerce / Retail', icon: 'fas fa-shopping-cart', description: 'Vente au détail, distribution' },
            { id: 'automobile', name: 'Automobile', icon: 'fas fa-car', description: 'Construction automobile, équipements' },
            { id: 'energie', name: 'Énergie / Utilities', icon: 'fas fa-bolt', description: 'Énergies renouvelables, utilities' },
            { id: 'medias', name: 'Médias / Communication', icon: 'fas fa-broadcast-tower', description: 'Presse, audiovisuel, marketing' },
            { id: 'telecoms', name: 'Télécommunications', icon: 'fas fa-wifi', description: 'Réseaux, télécommunications' },
            { id: 'immobilier', name: 'Immobilier', icon: 'fas fa-building', description: 'Promotion, gestion immobilière' },
            { id: 'tourisme', name: 'Tourisme / Hôtellerie', icon: 'fas fa-plane', description: 'Voyage, hôtellerie, restauration' },
            { id: 'agriculture', name: 'Agriculture / Agroalimentaire', icon: 'fas fa-seedling', description: 'Agriculture, industrie alimentaire' },
            { id: 'btp', name: 'BTP / Construction', icon: 'fas fa-hard-hat', description: 'Bâtiment, travaux publics' },
            { id: 'logistique', name: 'Logistique / Transport', icon: 'fas fa-truck', description: 'Supply chain, transport' },
            { id: 'consulting', name: 'Consulting / Services professionnels', icon: 'fas fa-briefcase', description: 'Conseil, services aux entreprises' },
            { id: 'ecommerce', name: 'E-commerce / Digital', icon: 'fas fa-shopping-bag', description: 'Commerce en ligne, digital' },
            { id: 'biotech', name: 'Biotechnologie', icon: 'fas fa-dna', description: 'Recherche biotechnologique' },
            { id: 'aeronautique', name: 'Aéronautique / Spatial', icon: 'fas fa-rocket', description: 'Industrie aéronautique et spatiale' },
            { id: 'mode', name: 'Mode / Luxe', icon: 'fas fa-gem', description: 'Industrie de la mode, luxe' },
            { id: 'sports', name: 'Sports / Loisirs', icon: 'fas fa-futbol', description: 'Sport, loisirs, divertissement' },
            { id: 'juridique', name: 'Juridique', icon: 'fas fa-gavel', description: 'Droit, services juridiques' },
            { id: 'culture', name: 'Art / Culture', icon: 'fas fa-palette', description: 'Arts, culture, créativité' },
            { id: 'environnement', name: 'Environnement / Développement durable', icon: 'fas fa-leaf', description: 'Écologie, développement durable' },
            { id: 'recherche', name: 'Recherche & Développement', icon: 'fas fa-microscope', description: 'R&D, innovation' },
            { id: 'securite', name: 'Sécurité', icon: 'fas fa-shield-alt', description: 'Sécurité, surveillance' },
            { id: 'public', name: 'Administration publique', icon: 'fas fa-landmark', description: 'Service public, administration' },
            { id: 'ong', name: 'ONG / Associations', icon: 'fas fa-hands-helping', description: 'Secteur associatif, humanitaire' }
        ];
        
        this.init();
    }

    init() {
        console.log('🔧 Initialisation correction étape 3...');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupStep3());
        } else {
            this.setupStep3();
        }
    }

    setupStep3() {
        try {
            console.log('⚙️ Configuration étape 3...');
            
            this.initializeMotivationSystem();
            this.initializeSecteurSystem();
            this.initializeSalarySystem();
            this.setupFormValidation();
            
            console.log('✅ Étape 3 configurée avec succès');
        } catch (error) {
            console.error('❌ Erreur configuration étape 3:', error);
        }
    }

    // === SYSTÈME DE MOTIVATIONS ===
    initializeMotivationSystem() {
        console.log('🎯 Initialisation système de motivations...');
        
        const motivationCards = document.querySelectorAll('.motivation-card');
        const counter = document.getElementById('motivation-counter');
        const summary = document.getElementById('motivation-summary');
        const autreField = document.getElementById('autre-field');
        
        if (!motivationCards.length) {
            console.warn('⚠️ Cartes de motivation non trouvées');
            return;
        }

        // Event listeners pour les cartes de motivation
        motivationCards.forEach(card => {
            card.addEventListener('click', (e) => this.handleMotivationClick(card, e));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleMotivationClick(card, e);
                }
            });
        });

        this.updateMotivationDisplay();
        console.log('✅ Système de motivations initialisé');
    }

    handleMotivationClick(card, event) {
        event.preventDefault();
        event.stopPropagation();
        
        const motivation = card.dataset.motivation;
        const isSelected = this.selectedMotivations.includes(motivation);
        
        if (isSelected) {
            // Désélectionner
            this.selectedMotivations = this.selectedMotivations.filter(m => m !== motivation);
            card.classList.remove('selected');
            
            // Cacher le champ "autre" si c'est l'option "autre"
            if (motivation === 'autre') {
                const autreField = document.getElementById('autre-field');
                if (autreField) {
                    autreField.classList.remove('active');
                }
            }
        } else {
            // Vérifier la limite
            if (this.selectedMotivations.length >= this.maxMotivations) {
                this.showNotification(`Vous ne pouvez sélectionner que ${this.maxMotivations} motivations maximum`, 'warning');
                return;
            }
            
            // Sélectionner
            this.selectedMotivations.push(motivation);
            card.classList.add('selected');
            
            // Afficher le champ "autre" si c'est l'option "autre"
            if (motivation === 'autre') {
                const autreField = document.getElementById('autre-field');
                if (autreField) {
                    autreField.classList.add('active');
                }
            }
        }
        
        this.updateMotivationDisplay();
        console.log('🎯 Motivations sélectionnées:', this.selectedMotivations);
    }

    updateMotivationDisplay() {
        // Mettre à jour le compteur
        const counter = document.getElementById('motivation-counter');
        if (counter) {
            counter.textContent = `${this.selectedMotivations.length} / ${this.maxMotivations} sélectionnées`;
        }

        // Mettre à jour les badges de rang
        const cards = document.querySelectorAll('.motivation-card');
        cards.forEach(card => {
            const motivation = card.dataset.motivation;
            const badge = card.querySelector('.ranking-badge');
            const index = this.selectedMotivations.indexOf(motivation);
            
            if (index !== -1 && badge) {
                badge.textContent = index + 1;
                badge.className = `ranking-badge rank-${index + 1}`;
            }
        });

        // Mettre à jour le résumé
        this.updateMotivationSummary();
        
        // Désactiver les cartes non sélectionnées si limite atteinte
        if (this.selectedMotivations.length >= this.maxMotivations) {
            cards.forEach(card => {
                if (!this.selectedMotivations.includes(card.dataset.motivation)) {
                    card.classList.add('disabled');
                }
            });
        } else {
            cards.forEach(card => card.classList.remove('disabled'));
        }

        // Mettre à jour les champs cachés
        this.updateMotivationHiddenFields();
    }

    updateMotivationSummary() {
        const summary = document.getElementById('motivation-summary');
        const summaryList = document.getElementById('summary-list');
        
        if (!summary || !summaryList) return;

        if (this.selectedMotivations.length > 0) {
            summary.classList.add('active');
            
            const items = this.selectedMotivations.map((motivation, index) => {
                const card = document.querySelector(`[data-motivation="${motivation}"]`);
                const title = card ? card.querySelector('.card-title').textContent : motivation;
                
                return `
                    <div class="summary-item">
                        <div class="summary-rank">${index + 1}</div>
                        <div>${title}</div>
                    </div>
                `;
            }).join('');
            
            summaryList.innerHTML = items;
        } else {
            summary.classList.remove('active');
        }
    }

    updateMotivationHiddenFields() {
        const hiddenMotivations = document.getElementById('hidden-motivations');
        const hiddenRanking = document.getElementById('hidden-motivations-ranking');
        
        if (hiddenMotivations) {
            hiddenMotivations.value = this.selectedMotivations.join(',');
        }
        if (hiddenRanking) {
            hiddenRanking.value = this.selectedMotivations.map((m, i) => `${m}:${i + 1}`).join(',');
        }
    }

    // === SYSTÈME DE SECTEURS ===
    initializeSecteurSystem() {
        console.log('🏭 Initialisation système de secteurs...');
        
        this.populateSecteurOptions('secteurs');
        this.populateSecteurOptions('redhibitoires');
        this.setupSecteurSearch();
        
        console.log('✅ Système de secteurs initialisé');
    }

    populateSecteurOptions(type) {
        const optionsContainer = document.getElementById(`${type}-options`);
        if (!optionsContainer) return;

        const optionsHtml = this.secteursList.map(secteur => `
            <div class="dropdown-option" data-secteur="${secteur.id}" data-type="${type}">
                <div class="option-checkbox">
                    <i class="fas fa-check"></i>
                </div>
                <div class="option-icon">
                    <i class="${secteur.icon}"></i>
                </div>
                <div class="option-content">
                    <div class="option-name">${secteur.name}</div>
                    <div class="option-description">${secteur.description}</div>
                </div>
            </div>
        `).join('');

        optionsContainer.innerHTML = optionsHtml;

        // Ajouter les event listeners
        optionsContainer.querySelectorAll('.dropdown-option').forEach(option => {
            option.addEventListener('click', (e) => this.handleSecteurClick(option, type, e));
        });
    }

    setupSecteurSearch() {
        // Recherche pour secteurs passionnants
        const secteursSearch = document.getElementById('secteurs-search');
        if (secteursSearch) {
            secteursSearch.addEventListener('input', (e) => this.filterSecteurs('secteurs', e.target.value));
        }

        // Recherche pour secteurs rédhibitoires
        const redhibitoiresSearch = document.getElementById('redhibitoires-search');
        if (redhibitoiresSearch) {
            redhibitoiresSearch.addEventListener('input', (e) => this.filterSecteurs('redhibitoires', e.target.value));
        }
    }

    handleSecteurClick(option, type, event) {
        event.preventDefault();
        event.stopPropagation();
        
        const secteurId = option.dataset.secteur;
        const isSelected = option.classList.contains('selected');
        
        if (type === 'secteurs') {
            if (isSelected) {
                this.selectedSecteurs = this.selectedSecteurs.filter(s => s !== secteurId);
                option.classList.remove('selected');
            } else {
                this.selectedSecteurs.push(secteurId);
                option.classList.add('selected');
            }
        } else if (type === 'redhibitoires') {
            if (isSelected) {
                this.selectedRedhibitoires = this.selectedRedhibitoires.filter(s => s !== secteurId);
                option.classList.remove('selected');
            } else {
                this.selectedRedhibitoires.push(secteurId);
                option.classList.add('selected');
            }
        }
        
        this.updateSecteurDisplay(type);
        this.checkSecteurConflicts();
        
        console.log(`🏭 ${type} sélectionnés:`, type === 'secteurs' ? this.selectedSecteurs : this.selectedRedhibitoires);
    }

    filterSecteurs(type, searchTerm) {
        const options = document.querySelectorAll(`#${type}-options .dropdown-option`);
        const term = searchTerm.toLowerCase();
        
        options.forEach(option => {
            const name = option.querySelector('.option-name').textContent.toLowerCase();
            const description = option.querySelector('.option-description').textContent.toLowerCase();
            
            if (name.includes(term) || description.includes(term)) {
                option.style.display = 'flex';
            } else {
                option.style.display = 'none';
            }
        });
    }

    updateSecteurDisplay(type) {
        const selectedArray = type === 'secteurs' ? this.selectedSecteurs : this.selectedRedhibitoires;
        const counter = document.getElementById(`${type}-counter`);
        const selectedContainer = document.getElementById(`${type}-selected`);
        const tagsContainer = document.getElementById(`${type}-tags`);
        
        // Mettre à jour le compteur
        if (counter) {
            const label = type === 'secteurs' ? 'sélectionnés' : 'exclus';
            counter.textContent = `${selectedArray.length} ${label}`;
        }

        // Mettre à jour les tags
        if (tagsContainer && selectedContainer) {
            if (selectedArray.length > 0) {
                selectedContainer.classList.add('active');
                
                const tagsHtml = selectedArray.map(secteurId => {
                    const secteur = this.secteursList.find(s => s.id === secteurId);
                    if (!secteur) return '';
                    
                    return `
                        <div class="sector-tag">
                            <i class="${secteur.icon}"></i>
                            <span>${secteur.name}</span>
                            <i class="fas fa-times remove-tag" onclick="window.nextenStep3Fix.removeSecteur('${secteurId}', '${type}')"></i>
                        </div>
                    `;
                }).join('');
                
                tagsContainer.innerHTML = tagsHtml;
            } else {
                selectedContainer.classList.remove('active');
            }
        }

        // Mettre à jour les champs cachés
        this.updateSecteurHiddenFields();
    }

    removeSecteur(secteurId, type) {
        if (type === 'secteurs') {
            this.selectedSecteurs = this.selectedSecteurs.filter(s => s !== secteurId);
        } else {
            this.selectedRedhibitoires = this.selectedRedhibitoires.filter(s => s !== secteurId);
        }
        
        // Mettre à jour l'option dans la liste
        const option = document.querySelector(`#${type}-options [data-secteur="${secteurId}"]`);
        if (option) {
            option.classList.remove('selected');
        }
        
        this.updateSecteurDisplay(type);
        this.checkSecteurConflicts();
    }

    checkSecteurConflicts() {
        const conflictWarning = document.getElementById('conflict-warning');
        if (!conflictWarning) return;

        const conflicts = this.selectedSecteurs.filter(s => this.selectedRedhibitoires.includes(s));
        
        if (conflicts.length > 0) {
            conflictWarning.classList.add('active');
        } else {
            conflictWarning.classList.remove('active');
        }
    }

    updateSecteurHiddenFields() {
        const hiddenSecteurs = document.getElementById('hidden-secteurs');
        const hiddenRedhibitoires = document.getElementById('hidden-secteurs-redhibitoires');
        
        if (hiddenSecteurs) {
            hiddenSecteurs.value = this.selectedSecteurs.join(',');
        }
        if (hiddenRedhibitoires) {
            hiddenRedhibitoires.value = this.selectedRedhibitoires.join(',');
        }
    }

    // === SYSTÈME DE SALAIRE ===
    initializeSalarySystem() {
        console.log('💰 Initialisation système de salaire...');
        
        const salaryMinInput = document.getElementById('salary-min');
        const salaryMaxInput = document.getElementById('salary-max');
        const salarySliderMin = document.getElementById('salary-slider-min');
        const salarySliderMax = document.getElementById('salary-slider-max');
        const salaryDisplay = document.getElementById('salary-display');
        
        if (!salaryMinInput || !salaryMaxInput) {
            console.warn('⚠️ Champs de salaire non trouvés');
            return;
        }

        // Event listeners pour les inputs
        salaryMinInput.addEventListener('input', () => this.handleSalaryInputChange('min'));
        salaryMaxInput.addEventListener('input', () => this.handleSalaryInputChange('max'));
        salaryMinInput.addEventListener('focus', () => this.handleSalaryFocus('min'));
        salaryMaxInput.addEventListener('focus', () => this.handleSalaryFocus('max'));
        salaryMinInput.addEventListener('blur', () => this.handleSalaryBlur('min'));
        salaryMaxInput.addEventListener('blur', () => this.handleSalaryBlur('max'));

        // Event listeners pour les sliders
        if (salarySliderMin) {
            salarySliderMin.addEventListener('input', () => this.handleSalarySliderChange('min'));
        }
        if (salarySliderMax) {
            salarySliderMax.addEventListener('input', () => this.handleSalarySliderChange('max'));
        }

        // Event listeners pour les suggestions
        const suggestions = document.querySelectorAll('.salary-suggestion');
        suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                const min = parseInt(suggestion.dataset.min);
                const max = parseInt(suggestion.dataset.max);
                this.setSalaryRange(min, max);
            });
        });

        this.updateSalaryDisplay();
        console.log('✅ Système de salaire initialisé');
    }

    handleSalaryInputChange(type) {
        const input = document.getElementById(`salary-${type}`);
        const value = parseInt(input.value) || (type === 'min' ? 20 : 25);
        
        if (type === 'min') {
            this.salaryMin = Math.max(20, Math.min(200, value));
        } else {
            this.salaryMax = Math.max(20, Math.min(200, value));
        }
        
        this.validateSalaryRange();
        this.updateSalaryDisplay();
        this.updateSalarySliders();
    }

    handleSalarySliderChange(type) {
        const slider = document.getElementById(`salary-slider-${type}`);
        const value = parseInt(slider.value);
        
        if (type === 'min') {
            this.salaryMin = value;
        } else {
            this.salaryMax = value;
        }
        
        this.validateSalaryRange();
        this.updateSalaryDisplay();
        this.updateSalaryInputs();
    }

    handleSalaryFocus(type) {
        const group = document.getElementById(`salary-${type}-group`);
        if (group) {
            group.classList.add('focused');
        }
    }

    handleSalaryBlur(type) {
        const group = document.getElementById(`salary-${type}-group`);
        if (group) {
            group.classList.remove('focused');
        }
    }

    setSalaryRange(min, max) {
        this.salaryMin = min;
        this.salaryMax = max;
        this.updateSalaryDisplay();
        this.updateSalaryInputs();
        this.updateSalarySliders();
        this.validateSalaryRange();
    }

    validateSalaryRange() {
        const validation = document.getElementById('salary-validation');
        const minGroup = document.getElementById('salary-min-group');
        const maxGroup = document.getElementById('salary-max-group');
        
        if (this.salaryMin >= this.salaryMax) {
            if (validation) validation.classList.add('active');
            if (minGroup) minGroup.classList.add('error');
            if (maxGroup) maxGroup.classList.add('error');
            return false;
        } else {
            if (validation) validation.classList.remove('active');
            if (minGroup) minGroup.classList.remove('error');
            if (maxGroup) maxGroup.classList.remove('error');
            return true;
        }
    }

    updateSalaryDisplay() {
        const display = document.getElementById('salary-display');
        if (display) {
            display.textContent = `Entre ${this.salaryMin}K et ${this.salaryMax}K €`;
        }
        
        this.updateSalaryHiddenFields();
    }

    updateSalaryInputs() {
        const minInput = document.getElementById('salary-min');
        const maxInput = document.getElementById('salary-max');
        
        if (minInput) minInput.value = this.salaryMin;
        if (maxInput) maxInput.value = this.salaryMax;
    }

    updateSalarySliders() {
        const minSlider = document.getElementById('salary-slider-min');
        const maxSlider = document.getElementById('salary-slider-max');
        
        if (minSlider) minSlider.value = this.salaryMin;
        if (maxSlider) maxSlider.value = this.salaryMax;
    }

    updateSalaryHiddenFields() {
        const hiddenMin = document.getElementById('hidden-salary-min');
        const hiddenMax = document.getElementById('hidden-salary-max');
        const hiddenRange = document.getElementById('hidden-salary-range');
        
        if (hiddenMin) hiddenMin.value = this.salaryMin;
        if (hiddenMax) hiddenMax.value = this.salaryMax;
        if (hiddenRange) hiddenRange.value = `${this.salaryMin}-${this.salaryMax}`;
    }

    // === VALIDATION DU FORMULAIRE ===
    setupFormValidation() {
        const nextButton = document.getElementById('next-step3');
        if (nextButton) {
            nextButton.addEventListener('click', (e) => {
                if (!this.validateStep3()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            });
        }
    }

    validateStep3() {
        let isValid = true;
        const errors = [];

        // Validation des motivations
        if (this.selectedMotivations.length === 0) {
            errors.push('Veuillez sélectionner au moins une motivation professionnelle');
            isValid = false;
        }

        // Validation de la fourchette salariale
        if (!this.validateSalaryRange()) {
            errors.push('La fourchette salariale n\'est pas valide');
            isValid = false;
        }

        // Validation du champ "autre" si sélectionné
        if (this.selectedMotivations.includes('autre')) {
            const autreText = document.getElementById('autre-motivation-text');
            if (autreText && !autreText.value.trim()) {
                errors.push('Veuillez préciser votre autre motivation');
                isValid = false;
            }
        }

        // Afficher les erreurs
        if (!isValid) {
            errors.forEach(error => this.showNotification(error, 'warning'));
        }

        return isValid;
    }

    // === UTILITAIRES ===
    showNotification(message, type = 'info') {
        // Supprimer les anciennes notifications
        document.querySelectorAll('.step3-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = 'step3-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            z-index: 10000;
            font-weight: 500;
            font-size: 14px;
            max-width: 400px;
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
        }, 4000);
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

    // === MÉTHODES PUBLIQUES ===
    getFormData() {
        return {
            motivations: this.selectedMotivations,
            secteurs: this.selectedSecteurs,
            secteursRedhibitoires: this.selectedRedhibitoires,
            salaryMin: this.salaryMin,
            salaryMax: this.salaryMax,
            autreMotivation: document.getElementById('autre-motivation-text')?.value || '',
            aspirations: document.getElementById('aspirations')?.value || ''
        };
    }

    resetStep3() {
        this.selectedMotivations = [];
        this.selectedSecteurs = [];
        this.selectedRedhibitoires = [];
        this.salaryMin = 40;
        this.salaryMax = 45;
        
        // Réinitialiser l'interface
        document.querySelectorAll('.motivation-card').forEach(card => card.classList.remove('selected', 'disabled'));
        document.querySelectorAll('.dropdown-option').forEach(option => option.classList.remove('selected'));
        
        this.updateMotivationDisplay();
        this.updateSecteurDisplay('secteurs');
        this.updateSecteurDisplay('redhibitoires');
        this.updateSalaryDisplay();
        this.updateSalaryInputs();
        this.updateSalarySliders();
    }
}

// Initialisation globale sécurisée
(function() {
    console.log('🔧 Chargement correction étape 3...');
    
    const initStep3Fix = () => {
        try {
            if (!window.nextenStep3Fix) {
                window.nextenStep3Fix = new NextenStep3Fix();
                console.log('✅ Correction étape 3 initialisée');
            }
        } catch (error) {
            console.error('❌ Erreur initialisation correction étape 3:', error);
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initStep3Fix);
    } else {
        setTimeout(initStep3Fix, 100);
    }
    
    // Fallback d'initialisation
    window.addEventListener('load', () => {
        setTimeout(() => {
            if (!window.nextenStep3Fix) {
                console.log('🔄 Initialisation de secours étape 3...');
                initStep3Fix();
            }
        }, 500);
    });
})();
